"""WHAT: Execute the Engineering Studio workflow against model clients.

WHY: Keep provider calls, files, parallelism, and lifecycle events separate
from the immutable dependency plan.
HOW: Consume ordered batches from workflow.py and expose the same public
stage metadata and run_pipeline entry point.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from engineering_studio.agents.specialist import SpecialistAgent
from engineering_studio.agents.workflow import (
    PARALLEL_DISCIPLINES,
    REVIEW_STAGES,
    WORKFLOW_PLAN,
    StageBatch,
    StageSpec,
    WorkflowPlan,
)
from engineering_studio.fireworks_client import ModelClient
from engineering_studio.task_specs import get_task_spec

__all__ = [
    "PARALLEL_DISCIPLINES",
    "REVIEW_STAGES",
    "STAGE_MODEL_ENV_VAR",
    "STAGE_ORDER",
    "STAGE_SPECS",
    "EventCallback",
    "run_pipeline",
]

_LOGGER = logging.getLogger("engineering_studio")

# Public metadata consumed by the run store, downloads, and fake executor.
STAGE_SPECS = {
    stage.stage_id: stage.task_slug for batch in WORKFLOW_PLAN.batches for stage in batch.stages
}
STAGE_ORDER = tuple(STAGE_SPECS)
STAGE_MODEL_ENV_VAR = {
    stage.stage_id: batch.model_env_var for batch in WORKFLOW_PLAN.batches for stage in batch.stages
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


def _emit(
    on_event: EventCallback | None, stage: str, status: str, detail: str | None = None
) -> None:
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
    """WHAT: Runs exactly one declared stage.

    WHY: Report each stage's lifecycle around its isolated artifact write.
    HOW: Render its task specification and invoke the specialist.

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
    stages: tuple[StageSpec, ...],
    client: ModelClient,
    product_brief: str,
    upstream: str,
    artifacts_root: Path,
    on_event: EventCallback | None,
) -> dict[str, Path]:
    """WHAT: Runs a set of independent stages concurrently against the same
    upstream context, collecting every result before returning.

    ARGS:
        stages (tuple[StageSpec, ...]): Stage declarations in plan order.
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

    def _dispatch(stage: StageSpec) -> tuple[str, Path]:
        """WHAT: Dispatch the stage. WHY: Retain its ID for ordered collection.
        HOW: Forward its plan declaration and shared context to the stage runner.
        """
        path = _run_stage(
            stage.stage_id,
            client,
            stage.task_slug,
            product_brief,
            upstream,
            artifacts_root,
            on_event,
        )
        return stage.stage_id, path

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


def _upstream_text(
    batch: StageBatch,
    product_brief: str,
    outputs: dict[str, Path],
    artifact_text: dict[str, str],
) -> str:
    """WHAT: Build this batch's exact input text.
    WHY: Ordered graph edges determine which artifacts each stage may see.
    HOW: Read each referenced artifact once and preserve empty segments.
    """
    if not batch.upstream:
        return product_brief
    for upstream_id in batch.upstream:
        if upstream_id not in artifact_text:
            artifact_text[upstream_id] = outputs[upstream_id].read_text(encoding="utf-8")
    return "\n\n".join(artifact_text[upstream_id] for upstream_id in batch.upstream)


def _execute_plan(
    plan: WorkflowPlan,
    product_brief: str,
    artifacts_root: Path,
    on_event: EventCallback | None,
) -> dict[str, Path]:
    """WHAT: Execute a validated workflow plan.
    WHY: Keep client acquisition, artifact reads, and events out of planning.
    HOW: Walk dependency batches, reusing clients and draining parallel
    siblings before beginning the next batch.
    """
    outputs: dict[str, Path] = {}
    artifact_text: dict[str, str] = {}
    clients: dict[str, ModelClient] = {}
    for batch in plan.batches:
        upstream = _upstream_text(batch, product_brief, outputs, artifact_text)
        model_env = batch.model_env_var
        if model_env not in clients:
            try:
                clients[model_env] = _client_for(model_env)
            except Exception as exc:
                for affected in plan.batches:
                    if affected.model_env_var == model_env:
                        for stage in affected.stages:
                            _emit(on_event, stage.stage_id, "error", str(exc))
                raise
        client = clients[model_env]
        if len(batch.stages) == 1:
            stage = batch.stages[0]
            outputs[stage.stage_id] = _run_stage(
                stage.stage_id,
                client,
                stage.task_slug,
                product_brief,
                upstream,
                artifacts_root,
                on_event,
            )
        else:
            outputs.update(
                _run_parallel_stages(
                    batch.stages,
                    client,
                    product_brief,
                    upstream,
                    artifacts_root,
                    on_event,
                )
            )
    return outputs


def run_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: EventCallback | None = None,
) -> dict[str, Path]:
    """WHAT: Run the canonical Engineering Studio workflow.
    WHY: Give CLI, SDK, and web callers one stable pipeline entry point.
    HOW: Execute the shared graph and forward existing stage lifecycle
    events. Exceptions propagate after in-flight siblings have finished.
    """
    return _execute_plan(WORKFLOW_PLAN, product_brief, artifacts_root, on_event)
