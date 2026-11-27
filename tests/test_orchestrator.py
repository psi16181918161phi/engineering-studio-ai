"""WHAT: Unit tests for engineering_studio.agents.orchestrator.
WHY: `run_pipeline` and `_client_for` were previously at 0% coverage —
must be exercised without any real network/model call.
HOW: Monkeypatches `SpecialistAgent` with an in-memory fake that writes
artifact files under a tmp_path root, so the real Research -> fan-out ->
business sequencing logic runs, but no HTTP request is made.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from engineering_studio.agents import orchestrator


class _FakeAgent:
    def __init__(self, discipline: str, client: object, artifacts_root: Path) -> None:
        self.discipline = discipline
        self.artifacts_root = Path(artifacts_root)

    def run(self, system_prompt: str, user_prompt: str) -> Path:
        path = self.artifacts_root / self.discipline / "output.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{self.discipline}: {user_prompt[:20]}", encoding="utf-8")
        return path


def test_client_for_raises_value_error_when_env_var_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FIREWORKS_MODEL_MISSING_FOR_TEST", raising=False)
    with pytest.raises(ValueError, match="FIREWORKS_MODEL_MISSING_FOR_TEST"):
        orchestrator._client_for("FIREWORKS_MODEL_MISSING_FOR_TEST")


def test_client_for_builds_model_client_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_TEST_X", "accounts/fireworks/models/test-x")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    client = orchestrator._client_for("FIREWORKS_MODEL_TEST_X")
    assert client.model == "accounts/fireworks/models/test-x"


def test_run_pipeline_dispatches_research_specialists_and_business(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    outputs = orchestrator.run_pipeline("build a small survey drone", tmp_path)

    assert set(outputs) == {
        "research",
        "mechanical",
        "electrical",
        "firmware",
        "simulation",
        "business",
        "reviewer",
        "challenge",
        "exploratory_qa",
        "validator",
        "quality_gate",
    }
    for discipline, path in outputs.items():
        assert path.exists(), f"missing artifact for {discipline}"
    business_text = outputs["business"].read_text(encoding="utf-8")
    assert business_text.startswith("business:")
    assert outputs["reviewer"].read_text(encoding="utf-8").startswith("reviewer:")
    assert outputs["challenge"].read_text(encoding="utf-8").startswith("challenge:")
    assert outputs["exploratory_qa"].read_text(encoding="utf-8").startswith("exploratory_qa:")
    assert outputs["validator"].read_text(encoding="utf-8").startswith("validator:")
    assert outputs["quality_gate"].read_text(encoding="utf-8").startswith("quality_gate:")


def test_run_pipeline_review_stages_see_same_upstream_and_validator_sees_all(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Reviewer, Challenge Division, and Exploratory QA must critique
    the same assembled package independently (none may be chained into
    another's input), and the Validator must be the join point that sees
    all three — this is the Non-Overlap Rule's runtime contract, not just
    its prompt-text description in the .agent.md files."""
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    outputs = orchestrator.run_pipeline("build a small survey drone", tmp_path)

    combined_with_business = (
        "\n\n".join(
            outputs[d].read_text(encoding="utf-8") for d in orchestrator.PARALLEL_DISCIPLINES
        )
        + "\n\n"
        + outputs["business"].read_text(encoding="utf-8")
    )

    # _FakeAgent.run() echoes f"{discipline}: {user_prompt[:20]}" — every
    # REVIEW_STAGES member must have been called with the *same* upstream
    # text (the assembled package), not with each other's findings.
    for stage in orchestrator.REVIEW_STAGES:
        assert outputs[stage].read_text(encoding="utf-8") == (
            f"{stage}: {combined_with_business[:20]}"
        )

    combined_with_review = (
        combined_with_business
        + "\n\n"
        + "\n\n".join(outputs[s].read_text(encoding="utf-8") for s in orchestrator.REVIEW_STAGES)
    )
    assert outputs["validator"].read_text(encoding="utf-8") == (
        f"validator: {combined_with_review[:20]}"
    )


def test_run_pipeline_reports_lifecycle_events_in_stage_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    events: list[tuple[str, str, str | None]] = []
    orchestrator.run_pipeline(
        "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
    )

    seen_stages = {stage for stage, _status, _detail in events}
    assert seen_stages == set(orchestrator.STAGE_ORDER)
    # WHAT: Every stage must report "running" then "done" (never skip
    # straight to "done", and never report "error" on the happy path).
    statuses_by_stage: dict[str, list[str]] = {}
    for stage, status, _detail in events:
        statuses_by_stage.setdefault(stage, []).append(status)
    for stage, statuses in statuses_by_stage.items():
        assert statuses == ["running", "done"], f"{stage} had unexpected transitions: {statuses}"


def test_workflow_preserves_full_prompts_artifact_order_and_barriers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Check the executor's complete prompt and lifecycle contract.
    WHY: Reordering, skipping empty artifacts, or reading sibling artifacts
    early would change the prompts or observable run progress.
    HOW: Record every input and artifact read with a deterministic fake agent,
    then compare the full payload and events against independent expectations.
    """
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")

    waves = (
        ("research",),
        ("mechanical", "electrical", "firmware", "simulation"),
        ("business",),
        ("reviewer", "challenge", "exploratory_qa"),
        ("validator",),
        ("quality_gate",),
    )
    stage_order = tuple(stage for wave in waves for stage in wave)
    content = {stage: f"artifact:: {stage}\n" for stage in stage_order}
    content["electrical"] = ""
    prompts: dict[str, str] = {}
    read_count: Counter[str] = Counter()
    original_read_text = Path.read_text

    def _track_reads(
        path: Path,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> str:
        """WHAT: Count artifact reads and pass through all reads.
        WHY: Empty artifacts should be cached just like nonempty artifacts.
        HOW: Record only temporary stage artifacts and delegate to Path.
        """
        if path.parent.parent == tmp_path and path.name == "output.md":
            read_count[path.parent.name] += 1
        return original_read_text(path, encoding=encoding, errors=errors, newline=newline)

    class _CaptureAgent(_FakeAgent):
        """WHAT: Emit distinct artifacts and record full upstream prompts.
        WHY: Truncated echoes cannot detect a missing suffix or separator.
        HOW: Write known text by stage and save the complete prompt.
        """

        def run(self, system_prompt: str, user_prompt: str) -> Path:
            """WHAT: Capture an input and publish its stage artifact.
            WHY: Exercise genuine file reads and exact artifact concatenation.
            HOW: Record the input and write the predetermined payload.
            """
            prompts[self.discipline] = user_prompt
            artifact = self.artifacts_root / self.discipline / "output.md"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(content[self.discipline], encoding="utf-8")
            return artifact

    monkeypatch.setattr(orchestrator, "SpecialistAgent", _CaptureAgent)
    monkeypatch.setattr(Path, "read_text", _track_reads)
    events: list[tuple[str, str, str | None]] = []
    brief = "A stable fixture product brief"

    outputs = orchestrator.run_pipeline(brief, tmp_path, on_event=lambda *args: events.append(args))

    disciplines = "\n\n".join(content[stage] for stage in waves[1])
    package = f"{disciplines}\n\n{content['business']}"
    reviewed = package + "\n\n" + "\n\n".join(content[stage] for stage in waves[3])
    assert prompts == {
        "research": brief,
        **dict.fromkeys(waves[1], content["research"]),
        "business": disciplines,
        **dict.fromkeys(waves[3], package),
        "validator": reviewed,
        "quality_gate": f"{reviewed}\n\n{content['validator']}",
    }
    assert tuple(outputs) == stage_order
    assert read_count == Counter(dict.fromkeys(stage_order[:-1], 1))
    offset = 0
    for wave in waves:
        span = events[offset : offset + 2 * len(wave)]
        assert set(span) == {
            event
            for stage in wave
            for event in (
                (stage, "running", None),
                (stage, "done", str(outputs[stage])),
            )
        }
        for stage in wave:
            assert span.index((stage, "running", None)) < span.index(
                (stage, "done", str(outputs[stage]))
            )
        offset += len(span)
    assert offset == len(events)


def test_run_pipeline_emits_error_event_and_reraises_on_specialist_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")

    class _FailingAgent(_FakeAgent):
        def run(self, system_prompt: str, user_prompt: str) -> Path:
            if self.discipline == "electrical":
                raise RuntimeError("simulated model failure")
            return super().run(system_prompt, user_prompt)

    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FailingAgent)

    events: list[tuple[str, str, str | None]] = []
    with pytest.raises(RuntimeError, match="simulated model failure"):
        orchestrator.run_pipeline(
            "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
        )

    error_events = [e for e in events if e[1] == "error" and e[0] == "electrical"]
    assert len(error_events) == 1
    assert "simulated model failure" in (error_events[0][2] or "")


def test_run_pipeline_emits_error_when_task_spec_lookup_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: A failure resolving the stage's Task Specification (e.g. a
    missing docs/task-specs.md — the exact bug that broke the first real
    deployment) must report "error" for that stage, not leave it stuck at
    "running" forever. get_task_spec() is called inside _run_stage's own
    try block precisely so this failure mode is never silently unreported."""
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    def _boom(slug: str) -> str:
        raise FileNotFoundError(f"docs/task-specs.md not found (slug={slug!r})")

    monkeypatch.setattr(orchestrator, "get_task_spec", _boom)

    events: list[tuple[str, str, str | None]] = []
    with pytest.raises(FileNotFoundError, match="docs/task-specs.md not found"):
        orchestrator.run_pipeline(
            "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
        )

    research_events = [e for e in events if e[0] == "research"]
    assert [e[1] for e in research_events] == ["running", "error"], (
        "research must transition running -> error, never stay stuck at running"
    )
    assert "docs/task-specs.md not found" in (research_events[-1][2] or "")


def test_parallel_failures_preserve_first_error_and_report_both_stages(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Confirm the parallel join reports both failures and raises the first.

    WHY: A sibling failure must not replace the selected error or be abandoned.
    HOW: Fail two specialists and compare error events without assuming their timing.
    """
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    first = RuntimeError("mechanical failure")
    second = RuntimeError("electrical failure")
    failures = {"mechanical": first, "electrical": second}

    class _FailingAgent(_FakeAgent):
        """WHAT: Simulate two independent specialist failures.

        WHY: Exercise the orchestrator's collection of more than one error.
        HOW: Raise the stage's configured error or delegate to the offline fake.
        """

        def run(self, system_prompt: str, user_prompt: str) -> Path:
            """WHAT: Fail a selected stage or write its usual fake artifact.

            WHY: Isolate the failure to the parallel specialist group.
            HOW: Look up an exception by discipline before invoking the fake.
            """
            error = failures.get(self.discipline)
            if error is not None:
                raise error
            return super().run(system_prompt, user_prompt)

    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FailingAgent)
    events: list[tuple[str, str, str | None]] = []

    with pytest.raises(RuntimeError) as raised:
        orchestrator.run_pipeline(
            "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
        )

    assert raised.value is first
    assert {(stage, detail) for stage, status, detail in events if status == "error"} == {
        ("mechanical", str(first)),
        ("electrical", str(second)),
    }


def test_run_pipeline_marks_all_downstream_stages_error_when_specialist_client_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research")
    monkeypatch.delenv("FIREWORKS_MODEL_SPECIALIST", raising=False)
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    events: list[tuple[str, str, str | None]] = []
    with pytest.raises(ValueError, match="FIREWORKS_MODEL_SPECIALIST"):
        orchestrator.run_pipeline(
            "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
        )

    errored_stages = {stage for stage, status, _detail in events if status == "error"}
    assert errored_stages == {
        "mechanical",
        "electrical",
        "firmware",
        "simulation",
        "business",
        "reviewer",
        "challenge",
        "exploratory_qa",
        "validator",
        "quality_gate",
    }


def test_emit_swallows_observer_exceptions(tmp_path: Path) -> None:
    def _bad_observer(stage: str, status: str, detail: str | None) -> None:
        raise RuntimeError("observer bug must never break the pipeline")

    # WHAT: Must not raise even though the observer itself always raises.
    orchestrator._emit(_bad_observer, "research", "running", None)


def test_run_pipeline_emits_research_error_and_reraises_when_research_client_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("FIREWORKS_MODEL_RESEARCH", raising=False)
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(orchestrator, "SpecialistAgent", _FakeAgent)

    events: list[tuple[str, str, str | None]] = []
    with pytest.raises(ValueError, match="FIREWORKS_MODEL_RESEARCH"):
        orchestrator.run_pipeline(
            "build a small survey drone", tmp_path, on_event=lambda *args: events.append(args)
        )

    assert events == [("research", "error", events[0][2])]
    assert "FIREWORKS_MODEL_RESEARCH" in (events[0][2] or "")
