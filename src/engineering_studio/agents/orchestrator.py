"""WHAT: Orchestrates the Engineering Studio AI pipeline: Research ->
parallel specialist fan-out -> business/legal -> Reviewer || Challenge ||
Exploratory QA -> Validator -> quality gate.
WHY: Single place that knows the pipeline ORDER (Workflow-position axis);
every stage's actual work stays inside its own SpecialistAgent (SRP). The
Reviewer, Challenge Division, Exploratory QA, and Validator stages exist so
no specialist's output is ever accepted without an independent critique —
the Non-Overlap Rule (AGENTS.md SS2/SS3): the agent that builds a thing is
never the agent that reviews, validates, or certifies it.
HOW: Sequential Research pass, then a thread-pool fan-out of the parallel
specialists (they don't depend on each other, only on Research), then the
Business/Legal pass, then a second thread-pool fan-out where the Reviewer,
Challenge Division, and Exploratory QA independently critique the same
assembled package, then the Validator reconciles all three sets of
findings, and finally the Quality Gate verdict — each stage depending on
everything produced before it. An optional `on_event` callback reports
per-stage lifecycle transitions (running/done/error) so a caller such as
the web command-and-control API can track live status without the
orchestrator knowing anything about HTTP or threading.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from engineering_studio.agents.specialist import SpecialistAgent
from engineering_studio.fireworks_client import ModelClient
from engineering_studio.task_specs import get_task_spec

_LOGGER = logging.getLogger("engineering_studio")

PARALLEL_DISCIPLINES = ("mechanical", "electrical", "firmware", "simulation")

# WHAT: The Review, Challenge, and Exploratory QA stages independently
# examine the same assembled artifact set and run concurrently, joining at
# Validate.
# WHY: Mirrors the whitepaper's Review || Challenge -> Validate phase
# ordering, extended with a third independent critic — Exploratory QA
# walks realistic usage scenarios, distinct from Reviewer's checklist and
# Challenge Division's adversarial stances. None may see or depend on each
# other's findings; the Validator is the only agent that reconciles them
# (Non-Overlap Rule).
REVIEW_STAGES = ("reviewer", "challenge", "exploratory_qa")

# WHAT: Canonical, ordered list of every stage this orchestrator dispatches.
# WHY: A single source of truth for display order — shared with the web API
# (engineering_studio.runs) so the command-and-control dashboard always
# reflects the actual dispatch order, never a hand-maintained duplicate.
STAGE_ORDER: tuple[str, ...] = (
    "research",
    *PARALLEL_DISCIPLINES,
    "business",
    *REVIEW_STAGES,
    "validator",
    "quality_gate",
)

# WHAT: Task Specification slug (docs/task-specs.md heading, slugified) for
# every dispatched stage.
# WHY: Single source of truth for the stage-to-prompt mapping — previously
# spread across per-call-site string literals/f-strings; adding a stage now
# means adding one line here, not touching dispatch logic.
STAGE_SPECS: dict[str, str] = {
    "research": "research-problem-analysis-pass",
    "mechanical": "mechanical-specialist-pass",
    "electrical": "electrical-specialist-pass",
    "firmware": "firmware-specialist-pass",
    "simulation": "simulation-specialist-pass",
    "business": "cost-business-legal-pass",
    "reviewer": "reviewer-critique-pass",
    "challenge": "challenge-division-adversarial-pass",
    "exploratory_qa": "exploratory-qa-scenario-pass",
    "validator": "validator-cross-consistency-pass",
    "quality_gate": "quality-gate-final-verdict",
}

# WHAT: Which environment variable names the model id used for each stage
# (research gets its own model; every other stage shares the specialist
# model). WHY: single source of truth reused both by `_client_for()` below
# and by `engineering_studio.runs` (which surfaces the resolved model id
# per stage to the dashboard for cost/model transparency) — avoids the two
# modules independently hard-coding the same research-vs-specialist split.
STAGE_MODEL_ENV_VAR: dict[str, str] = {
    stage: ("FIREWORKS_MODEL_RESEARCH" if stage == "research" else "FIREWORKS_MODEL_SPECIALIST")
    for stage in STAGE_ORDER
}

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
    break the pipeline, so exceptions raised by the callback are logged at
    debug level (for diagnosability) and otherwise swallowed, never re-raised.
    """
    if on_event is None:
        return
    try:
        on_event(stage, status, detail)
    except Exception:
        _LOGGER.debug(
            "on_event observer raised for stage=%s status=%s", stage, status, exc_info=True
        )


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
        TaskSpecNotFoundError: Propagated if spec_slug has no matching Task
            Specification; an "error" event is emitted first, same as any
            other stage failure — a missing spec must never leave a stage
            stuck at "running" forever.
    """
    _emit(on_event, discipline, "running")
    try:
        agent = SpecialistAgent(discipline, client, artifacts_root)
        spec = get_task_spec(spec_slug).replace("{PRODUCT_BRIEF}", product_brief)
        path = agent.run(spec, upstream)
    except Exception as exc:
        _emit(on_event, discipline, "error", str(exc))
        raise
    _emit(on_event, discipline, "done", str(path))
    return path


def _run_parallel_stages(
    stages: tuple[str, ...],
    client: ModelClient,
    product_brief: str,
    upstream: str,
    artifacts_root: Path,
    on_event: EventCallback | None,
) -> dict[str, Path]:
    """WHAT: Runs a set of independent stages concurrently against the same
    upstream context, collecting every result before returning.

    ARGS:
        stages (tuple[str, ...]): Stage ids to dispatch; each must have an
            entry in STAGE_SPECS.
        client (ModelClient): Shared model backend for every stage.
        product_brief (str): One-sentence hackathon demo prompt.
        upstream (str): Shared upstream artifact text passed as the user
            prompt to every stage — the stages examine the same input
            independently; they never feed each other (that reconciliation
            is the Validator's job, not this function's).
        artifacts_root (Path): Root directory for all written artifacts.
        on_event (EventCallback | None): Optional lifecycle observer.

    RETURNS:
        dict[str, Path]: Mapping of stage name to its output file, covering
            every stage in `stages` that completed successfully.

    RAISES:
        ModelUnavailableError: Re-raised only after every in-flight stage
            finishes (success or failure) — a slow sibling stage is never
            abandoned mid-write just because another one failed first.

    HOW: Same "submit all, collect all, re-raise the first error" pattern
    already used for the PARALLEL_DISCIPLINES fan-out, generalized so the
    Review/Challenge fan-out doesn't duplicate the ThreadPoolExecutor
    bookkeeping.
    """

    def _dispatch(stage: str) -> tuple[str, Path]:
        path = _run_stage(
            stage, client, STAGE_SPECS[stage], product_brief, upstream, artifacts_root, on_event
        )
        return stage, path

    results: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=len(stages)) as pool:
        futures = {pool.submit(_dispatch, s): s for s in stages}
        first_error: BaseException | None = None
        for future in futures:
            try:
                stage, path = future.result()
                results[stage] = path
            except Exception as exc:  # noqa: BLE001 - collect, re-raise after all finish
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error
    return results


def run_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: EventCallback | None = None,
) -> dict[str, Path]:
    """WHAT: Runs the full Research -> fan-out -> business -> Review ||
    Challenge -> Validate -> quality-gate pipeline.

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
        STAGE_SPECS["research"],
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
        for stage in (*PARALLEL_DISCIPLINES, "business", *REVIEW_STAGES, "validator", "quality_gate"):
            _emit(on_event, stage, "error", str(exc))
        raise

    outputs.update(
        _run_parallel_stages(
            PARALLEL_DISCIPLINES,
            specialist_client,
            product_brief,
            research_findings,
            artifacts_root,
            on_event,
        )
    )

    combined_upstream = "\n\n".join(
        outputs[d].read_text(encoding="utf-8") for d in PARALLEL_DISCIPLINES
    )
    business_path = _run_stage(
        "business",
        specialist_client,
        STAGE_SPECS["business"],
        product_brief,
        combined_upstream,
        artifacts_root,
        on_event,
    )
    outputs["business"] = business_path

    combined_with_business = combined_upstream + "\n\n" + business_path.read_text(encoding="utf-8")

    # WHAT: Reviewer, Challenge Division, and Exploratory QA all critique
    # the same assembled package independently and concurrently — see
    # REVIEW_STAGES's docstring comment for why none may see each other's
    # findings before Validate.
    outputs.update(
        _run_parallel_stages(
            REVIEW_STAGES,
            specialist_client,
            product_brief,
            combined_with_business,
            artifacts_root,
            on_event,
        )
    )

    combined_with_review = combined_with_business + "\n\n" + "\n\n".join(
        outputs[s].read_text(encoding="utf-8") for s in REVIEW_STAGES
    )
    validator_path = _run_stage(
        "validator",
        specialist_client,
        STAGE_SPECS["validator"],
        product_brief,
        combined_with_review,
        artifacts_root,
        on_event,
    )
    outputs["validator"] = validator_path

    combined_with_validation = combined_with_review + "\n\n" + validator_path.read_text(encoding="utf-8")
    outputs["quality_gate"] = _run_stage(
        "quality_gate",
        specialist_client,
        STAGE_SPECS["quality_gate"],
        product_brief,
        combined_with_validation,
        artifacts_root,
        on_event,
    )

    return outputs
