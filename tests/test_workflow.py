"""WHAT: Check the workflow plan's declared execution and context contracts.
WHY: A graph edit must not silently change public stage order or feed an
artifact into the wrong prompt.
HOW: Compare the static plan with the existing contract and construct invalid
plans directly without a model client, filesystem, or event observer.
"""

from dataclasses import FrozenInstanceError

import pytest

from engineering_studio.agents.workflow import WORKFLOW_PLAN, StageBatch, StageSpec, WorkflowPlan


def test_workflow_preserves_batch_order_and_context_edges() -> None:
    """WHAT: Verify the compatibility contract for the built-in plan.
    WHY: Stage dependencies and their order determine exact prompt bytes.
    HOW: Independently specify each wave's outputs, ordered inputs, and client.
    """
    specialists = ("mechanical", "electrical", "firmware", "simulation")
    reviews = ("reviewer", "challenge", "exploratory_qa")
    package = (*specialists, "business")
    reviewed = (*package, *reviews)
    batches = WORKFLOW_PLAN.batches
    assert tuple(tuple(stage.stage_id for stage in batch.stages) for batch in batches) == (
        ("research",),
        specialists,
        ("business",),
        reviews,
        ("validator",),
        ("quality_gate",),
    )
    assert tuple(batch.upstream for batch in batches) == (
        (),
        ("research",),
        specialists,
        package,
        reviewed,
        (*reviewed, "validator"),
    )
    assert tuple(batch.model_env_var for batch in batches) == (
        "FIREWORKS_MODEL_RESEARCH",
        *("FIREWORKS_MODEL_SPECIALIST",) * 5,
    )
    assert tuple(stage.task_slug for batch in batches for stage in batch.stages) == (
        "research-problem-analysis-pass",
        "mechanical-specialist-pass",
        "electrical-specialist-pass",
        "firmware-specialist-pass",
        "simulation-specialist-pass",
        "cost-business-legal-pass",
        "reviewer-critique-pass",
        "challenge-division-adversarial-pass",
        "exploratory-qa-scenario-pass",
        "validator-cross-consistency-pass",
        "quality-gate-final-verdict",
    )


def test_plan_records_are_frozen() -> None:
    """WHAT: Verify the graph and nested records reject mutation.
    WHY: Callers share the built-in plan across runs and API readers.
    HOW: Attempt to reassign a field on each declared record type.
    """
    batch = WORKFLOW_PLAN.batches[0]
    stage = batch.stages[0]
    for record, field in ((WORKFLOW_PLAN, "batches"), (batch, "upstream"), (stage, "stage_id")):
        with pytest.raises(FrozenInstanceError):
            setattr(record, field, "unexpected")


_MODEL_ENV = "TEST_MODEL"
_FIRST = StageSpec("first", "first-spec")
_SECOND = StageSpec("second", "second-spec")
_ROOT = StageBatch((_FIRST,), (), _MODEL_ENV)


@pytest.mark.parametrize(
    "batches",
    [
        pytest.param((), id="empty-plan"),
        pytest.param((StageBatch((), (), _MODEL_ENV),), id="empty-batch"),
        pytest.param(
            (StageBatch((_FIRST, _FIRST), (), _MODEL_ENV),),
            id="duplicate-within-batch",
        ),
        pytest.param((_ROOT, _ROOT), id="duplicate-across-batches"),
        pytest.param(
            (_ROOT, StageBatch((_SECOND,), ("first", "first"), _MODEL_ENV)),
            id="duplicate-upstream",
        ),
        pytest.param(
            (_ROOT, StageBatch((_SECOND,), ("missing",), _MODEL_ENV)),
            id="unknown-upstream",
        ),
        pytest.param(
            (_ROOT, StageBatch((_SECOND,), ("second",), _MODEL_ENV)),
            id="self-upstream",
        ),
        pytest.param(
            (StageBatch((_SECOND,), ("first",), _MODEL_ENV), _ROOT),
            id="forward-upstream",
        ),
        pytest.param(
            (StageBatch((_FIRST, _SECOND), ("first",), _MODEL_ENV),),
            id="same-batch-upstream",
        ),
    ],
)
def test_plan_rejects_ambiguous_or_unavailable_dependencies(
    batches: tuple[StageBatch, ...],
) -> None:
    """WHAT: Reject invalid structural plans before dispatch.
    WHY: A stage may consume only a uniquely named output in an earlier wave.
    HOW: Construct malformed wave declarations and verify a validation error.
    """
    with pytest.raises(ValueError):
        WorkflowPlan(batches)
