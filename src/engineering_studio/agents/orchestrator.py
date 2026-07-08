"""WHAT: Orchestrates the Engineering Studio AI pipeline: Research ->
parallel specialist fan-out -> business/legal -> challenge -> quality gate.
WHY: Single place that knows the pipeline ORDER (Workflow-position axis);
every stage's actual work stays inside its own SpecialistAgent (SRP).
HOW: Sequential Research pass, then a thread-pool fan-out of the parallel
specialists (they don't depend on each other, only on Research), then the
Business/Legal pass, the Challenge Division critique, and the Quality Gate
verdict, each depending on everything produced before it. An optional
`on_event` callback reports per-stage lifecycle transitions (running/done/
error) so a caller such as the web command-and-control API can track live
status without the orchestrator knowing anything about HTTP or threading.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from engineering_studio.agents.specialist import SpecialistAgent
from engineering_studio.fireworks_client import ModelClient
from engineering_studio.task_specs import get_task_spec

PARALLEL_DISCIPLINES = ("mechanical", "electrical", "firmware", "simulation")

# WHAT: Canonical, ordered list of every stage this orchestrator dispatches.
# WHY: A single source of truth for display order — shared with the web API
# (engineering_studio.runs) so the command-and-control dashboard always
# reflects the actual dispatch order, never a hand-maintained duplicate.
STAGE_ORDER: tuple[str, ...] = (
    "research",
    *PARALLEL_DISCIPLINES,
    "business",
    "challenge",
    "quality_gate",
)

# WHAT: Signature for the optional pipeline lifecycle observer.
# ARGS: (stage, status, detail) where status is one of
# "running" | "done" | "error" and detail is a short human-readable string
# (artifact path on success, error message on failure) or None.
EventCallback = Callable[[str, str, str | None], None]


def _client_for(model_env_var: str) -> ModelClient:
    """WHAT: Builds a ModelClient from a named model environment variable.

    ARGS:
        model_env_var (str): e.g. "FIREWORKS_MODEL_SPECIALIST".

    RETURNS:
        ModelClient: Configured client for the model id in that variable.

    RAISES:
        ValueError: If the environment variable is unset.
    """
    model = os.environ.get(model_env_var, "")
    if not model:
        raise ValueError(f"{model_env_var} is not set (see .env.example).")
    return ModelClient(model=model)


def _emit(on_event: EventCallback | None, stage: str, status: str, detail: str | None = None) -> None:
    """WHAT: Safely forwards a pipeline lifecycle event to an optional observer.

    ARGS:
        on_event (EventCallback | None): Observer to notify, or None.
        stage (str): Stage id, one of STAGE_ORDER.
        status (str): "running" | "done" | "error".
        detail (str | None): Artifact path on success, error text on failure.

    WHY: Lets the web API track live per-stage status without the
    orchestrator depending on any particular transport (SSE, logging, ...).

    HOW: No-op when on_event is None; a misbehaving observer must never
    break the pipeline, so exceptions raised by the callback are swallowed.
    """
    if on_event is None:
        return
    try:
        on_event(stage, status, detail)
    except Exception:  # noqa: BLE001 - observer failures are never fatal
        pass


def _run_stage(
    discipline: str,
    client: ModelClient,
    spec_slug: str,
    product_brief: str,
    upstream: str,
    artifacts_root: Path,
    on_event: EventCallback | None,
) -> Path:
    """WHAT: Runs exactly one stage (research or a single specialist call).

    ARGS:
        discipline (str): Artifact folder name, e.g. "mechanical".
        client (ModelClient): Model backend for this stage.
        spec_slug (str): Task Specification slug from docs/task-specs.md.
        product_brief (str): The one-sentence hackathon demo prompt.
        upstream (str): Upstream artifact text passed as the user prompt.
        artifacts_root (Path): Root directory for all written artifacts.
        on_event (EventCallback | None): Optional lifecycle observer.

    RETURNS:
        Path: The written artifact file path.

    RAISES:
        ModelUnavailableError: Propagated on model-call failure; an "error"
            event is emitted first so observers see why the stage stopped.
    """
    _emit(on_event, discipline, "running")
    agent = SpecialistAgent(discipline, client, artifacts_root)
    spec = get_task_spec(spec_slug).replace("{PRODUCT_BRIEF}", product_brief)
    try:
        path = agent.run(spec, upstream)
    except Exception as exc:
        _emit(on_event, discipline, "error", str(exc))
        raise
    _emit(on_event, discipline, "done", str(path))
    return path


def run_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: EventCallback | None = None,
) -> dict[str, Path]:
    """WHAT: Runs the full Research -> fan-out -> business -> challenge ->
    quality-gate pipeline.

    ARGS:
        product_brief (str): One-sentence hackathon demo prompt.
        artifacts_root (Path): Root directory for all written artifacts.
        on_event (EventCallback | None): Optional observer notified of every
            stage's "running"/"done"/"error" transition, in STAGE_ORDER.

    RETURNS:
        dict[str, Path]: Mapping of stage name to its output file. On a
            mid-pipeline failure this only contains the stages that
            completed before the raised exception.

    RAISES:
        ModelUnavailableError: Propagated from any stage on hard failure;
            the pipeline stops rather than continuing with a gap.
    """
    outputs: dict[str, Path] = {}

    try:
        research_client = _client_for("FIREWORKS_MODEL_RESEARCH")
    except Exception as exc:
        _emit(on_event, "research", "error", str(exc))
        raise
    research_path = _run_stage(
        "research",
        research_client,
        "research-problem-analysis-pass",
        product_brief,
        product_brief,
        artifacts_root,
        on_event,
    )
    outputs["research"] = research_path
    research_findings = research_path.read_text(encoding="utf-8")

    try:
        specialist_client = _client_for("FIREWORKS_MODEL_SPECIALIST")
    except Exception as exc:
        # WHAT: This one client is shared by every remaining stage; if it
        # can't be built, none of them will ever run — mark all of them
        # "error" (not left "pending") so the dashboard shows exactly why.
        for stage in (*PARALLEL_DISCIPLINES, "business", "challenge", "quality_gate"):
            _emit(on_event, stage, "error", str(exc))
        raise

    def _dispatch(discipline: str) -> tuple[str, Path]:
        path = _run_stage(
            discipline,
            specialist_client,
            f"{discipline}-specialist-pass",
            product_brief,
            research_findings,
            artifacts_root,
            on_event,
        )
        return discipline, path

    with ThreadPoolExecutor(max_workers=len(PARALLEL_DISCIPLINES)) as pool:
        futures = {pool.submit(_dispatch, d): d for d in PARALLEL_DISCIPLINES}
        first_error: BaseException | None = None
        for future in futures:
            try:
                discipline, path = future.result()
                outputs[discipline] = path
            except Exception as exc:  # noqa: BLE001 - collect, re-raise after all finish
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error

    combined_upstream = "\n\n".join(
        outputs[d].read_text(encoding="utf-8") for d in PARALLEL_DISCIPLINES
    )
    business_path = _run_stage(
        "business",
        specialist_client,
        "cost-business-legal-pass",
        product_brief,
        combined_upstream,
        artifacts_root,
        on_event,
    )
    outputs["business"] = business_path

    combined_with_business = combined_upstream + "\n\n" + business_path.read_text(encoding="utf-8")
    challenge_path = _run_stage(
        "challenge",
        specialist_client,
        "challenge-division-adversarial-pass",
        product_brief,
        combined_with_business,
        artifacts_root,
        on_event,
    )
    outputs["challenge"] = challenge_path

    combined_with_challenge = (
        combined_with_business + "\n\n" + challenge_path.read_text(encoding="utf-8")
    )
    outputs["quality_gate"] = _run_stage(
        "quality_gate",
        specialist_client,
        "quality-gate-final-verdict",
        product_brief,
        combined_with_challenge,
        artifacts_root,
        on_event,
    )

    return outputs
