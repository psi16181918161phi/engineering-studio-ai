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
    }
    for discipline, path in outputs.items():
        assert path.exists(), f"missing artifact for {discipline}"
    business_text = outputs["business"].read_text(encoding="utf-8")
    assert business_text.startswith("business:")
