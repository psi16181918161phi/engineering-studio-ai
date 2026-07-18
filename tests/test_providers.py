"""WHAT: Unit tests for engineering_studio.sdk.providers (OPEN_AI_DEV_WEEK_
HACKATHON/PLAN.md Phase 4 provider-agnostic model-client factory).
WHY: This module is the single source of truth every surface (API `/api/
models` route, CLI `models` subcommand, TUI model-routing panel) reads
model-routing state from — must reach 100% coverage and prove it never
fabricates a model id or exposes an API key value.
HOW: Only ever monkeypatches environment variables; never performs a real
network call (this module builds a `ModelClient`, it never calls
`.complete()`).
"""

from __future__ import annotations

import pytest

from engineering_studio.fireworks_client import ModelClient
from engineering_studio.sdk import providers


def test_providers_and_roles_are_the_documented_sets() -> None:
    assert providers.PROVIDERS == ("fireworks", "openai")
    assert providers.ROLES == ("orchestrator", "specialist", "research")


def test_get_model_info_reports_unconfigured_role_without_fabricating_a_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_MODEL_SPECIALIST", raising=False)

    info = providers.get_model_info("openai", "specialist")

    assert info == providers.ModelInfo(
        role="specialist", provider="openai", model=None, configured=False
    )


def test_get_model_info_reports_configured_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_MODEL_ORCHESTRATOR", "gpt-5.6-sol")

    info = providers.get_model_info("openai", "orchestrator")

    assert info == providers.ModelInfo(
        role="orchestrator", provider="openai", model="gpt-5.6-sol", configured=True
    )


def test_get_model_info_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unknown provider"):
        providers.get_model_info("anthropic", "research")


def test_get_model_info_rejects_unknown_role() -> None:
    with pytest.raises(ValueError, match="Unknown role"):
        providers.get_model_info("fireworks", "reviewer")


def test_build_model_client_raises_when_model_env_var_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_MODEL_RESEARCH", raising=False)

    with pytest.raises(ValueError, match="OPENAI_MODEL_RESEARCH is not set"):
        providers.build_model_client("openai", "research")


def test_build_model_client_reads_provider_scoped_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_MODEL_SPECIALIST", "gpt-5.6-terra")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    client = providers.build_model_client("openai", "specialist")

    assert isinstance(client, ModelClient)
    assert client.model == "gpt-5.6-terra"
    assert client.base_url == "https://api.openai.com/v1"
    assert client.api_key == "sk-test"


def test_build_model_client_stays_isolated_per_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/gpt-oss-120b")
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
    monkeypatch.setenv("FIREWORKS_API_KEY", "fw-test")

    client = providers.build_model_client("fireworks", "research")

    assert client.model == "accounts/fireworks/models/gpt-oss-120b"
    assert client.base_url == "https://api.fireworks.ai/inference/v1"
    assert client.api_key == "fw-test"
