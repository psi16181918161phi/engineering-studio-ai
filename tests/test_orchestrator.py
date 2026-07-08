"""WHAT: Unit tests for engineering_studio.agents.orchestrator.
WHY: `run_pipeline` and `_client_for` were previously at 0% coverage —
must be exercised without any real network/model call.
HOW: Monkeypatches `SpecialistAgent` with an in-memory fake that writes
artifact files under a tmp_path root, so the real Research -> fan-out ->
business sequencing logic runs, but no HTTP request is made.
"""

from __future__ import annotations

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
        "challenge",
        "quality_gate",
    }
    for discipline, path in outputs.items():
        assert path.exists(), f"missing artifact for {discipline}"
    business_text = outputs["business"].read_text(encoding="utf-8")
    assert business_text.startswith("business:")
    assert outputs["challenge"].read_text(encoding="utf-8").startswith("challenge:")
    assert outputs["quality_gate"].read_text(encoding="utf-8").startswith("quality_gate:")


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
        "challenge",
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
