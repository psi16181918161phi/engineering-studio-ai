"""WHAT: Unit tests for `engineering_studio.api.models` (`GET /api/models`).
WHY: This route is the only way a judge/dashboard can see which model
answers which pipeline role across both provider profiles (Fireworks AI,
OpenAI Hackathon) — a regression here (e.g. an API key leaking into the
response) would be a real security defect (OWASP A02 sensitive-data
exposure), so it is tested standalone with 100% coverage.
HOW: Builds a small standalone FastAPI app mounting only this router,
with environment variables monkeypatched — no real network call, no
dependency on the pipeline or RunStore.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from engineering_studio.api.models import router as models_router
from engineering_studio.sdk import PROVIDERS, ROLES


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(models_router)
    return TestClient(app)


def test_list_models_returns_one_entry_per_provider_role_pair(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_ORCHESTRATOR", "accounts/fireworks/models/gpt-oss-120b")
    monkeypatch.setenv("OPENAI_MODEL_SPECIALIST", "gpt-5.6-terra")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/api/models")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == len(PROVIDERS) * len(ROLES)

    fireworks_orchestrator = next(
        entry
        for entry in payload
        if entry["provider"] == "fireworks" and entry["role"] == "orchestrator"
    )
    assert fireworks_orchestrator["model"] == "accounts/fireworks/models/gpt-oss-120b"
    assert fireworks_orchestrator["configured"] is True

    openai_specialist = next(
        entry for entry in payload if entry["provider"] == "openai" and entry["role"] == "specialist"
    )
    assert openai_specialist["model"] == "gpt-5.6-terra"
    assert openai_specialist["configured"] is True


def test_list_models_never_includes_an_api_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-never-appear")
    monkeypatch.setenv("FIREWORKS_API_KEY", "fw-should-never-appear")

    response = client.get("/api/models")

    body_text = response.text
    assert "sk-should-never-appear" not in body_text
    assert "fw-should-never-appear" not in body_text


def test_list_models_reports_unconfigured_role_as_not_configured(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_MODEL_RESEARCH", raising=False)

    response = client.get("/api/models")

    payload = response.json()
    openai_research = next(
        entry for entry in payload if entry["provider"] == "openai" and entry["role"] == "research"
    )
    assert openai_research["model"] is None
    assert openai_research["configured"] is False
