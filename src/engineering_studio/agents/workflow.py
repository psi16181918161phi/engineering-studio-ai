"""WHAT: Declare the Engineering Studio workflow as ordered dependency batches.

WHY: Stage ownership, model choice, and artifact visibility must be reviewable
without invoking providers or reading artifacts.
HOW: Validate immutable, topologically ordered batches. Each upstream tuple
names the exact artifact inputs in serialization order.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StageSpec:
    """WHAT: Name a stage and its task spec. WHY: Bind prompts to stage IDs.
    HOW: Retain the two strings as immutable planning data.
    """

    stage_id: str
    task_slug: str


@dataclass(frozen=True, slots=True)
class StageBatch:
    """WHAT: Group independent stages with the same inputs and model.
    WHY: A parallel stage must never consume a sibling's output.
    HOW: An ordered tuple of earlier artifact IDs defines input visibility.
    An empty upstream means this batch receives the original product brief.
    """

    stages: tuple[StageSpec, ...]
    upstream: tuple[str, ...]
    model_env_var: str


@dataclass(frozen=True, slots=True)
class WorkflowPlan:
    """WHAT: Define the ordered batches that execute a workflow.
    WHY: Reject an invalid graph before it can acquire clients or emit events.
    HOW: Check uniqueness and require each edge to point to an earlier batch.
    """

    batches: tuple[StageBatch, ...]

    def __post_init__(self) -> None:
        """WHAT: Verify the graph's structure. WHY: Prevent ambiguous routing.
        HOW: Visit batches in order, admitting only already declared producers.
        """
        if not self.batches:
            raise ValueError("workflow must contain a batch")
        seen: set[str] = set()
        for batch in self.batches:
            if not batch.stages:
                raise ValueError("workflow batch must contain a stage")
            if len(batch.upstream) != len(set(batch.upstream)):
                raise ValueError("workflow batch has duplicate upstream artifacts")
            unresolved = set(batch.upstream) - seen
            if unresolved:
                raise ValueError(f"workflow requires earlier producers: {sorted(unresolved)}")
            for stage in batch.stages:
                if stage.stage_id in seen:
                    raise ValueError(f"duplicate workflow stage: {stage.stage_id}")
                seen.add(stage.stage_id)


_RESEARCH_MODEL = "FIREWORKS_MODEL_RESEARCH"
_SPECIALIST_MODEL = "FIREWORKS_MODEL_SPECIALIST"

_DISCIPLINES = (
    StageSpec("mechanical", "mechanical-specialist-pass"),
    StageSpec("electrical", "electrical-specialist-pass"),
    StageSpec("firmware", "firmware-specialist-pass"),
    StageSpec("simulation", "simulation-specialist-pass"),
)
_CRITICS = (
    StageSpec("reviewer", "reviewer-critique-pass"),
    StageSpec("challenge", "challenge-division-adversarial-pass"),
    StageSpec("exploratory_qa", "exploratory-qa-scenario-pass"),
)
PARALLEL_DISCIPLINES = tuple(stage.stage_id for stage in _DISCIPLINES)
REVIEW_STAGES = tuple(stage.stage_id for stage in _CRITICS)
_ASSEMBLED_PACKAGE = (*PARALLEL_DISCIPLINES, "business")
_REVIEWED_PACKAGE = (*_ASSEMBLED_PACKAGE, *REVIEW_STAGES)

WORKFLOW_PLAN = WorkflowPlan(
    (
        StageBatch((StageSpec("research", "research-problem-analysis-pass"),), (), _RESEARCH_MODEL),
        StageBatch(_DISCIPLINES, ("research",), _SPECIALIST_MODEL),
        StageBatch(
            (StageSpec("business", "cost-business-legal-pass"),),
            PARALLEL_DISCIPLINES,
            _SPECIALIST_MODEL,
        ),
        StageBatch(_CRITICS, _ASSEMBLED_PACKAGE, _SPECIALIST_MODEL),
        StageBatch(
            (StageSpec("validator", "validator-cross-consistency-pass"),),
            _REVIEWED_PACKAGE,
            _SPECIALIST_MODEL,
        ),
        StageBatch(
            (StageSpec("quality_gate", "quality-gate-final-verdict"),),
            (*_REVIEWED_PACKAGE, "validator"),
            _SPECIALIST_MODEL,
        ),
    )
)
