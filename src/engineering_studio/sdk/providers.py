"""WHAT: Provider-agnostic model-client factory + key-free introspection.
WHY: PLAN.md (OPEN_AI_DEV_WEEK_HACKATHON) Phase 4 requires the SDK/API/
CLI/TUI surfaces to swap between the Fireworks AI provider profile and
the new OpenAI Hackathon provider profile by config alone, per the Model
Routing Layer pattern already implemented by `fireworks_client.ModelClient`
(constructor already takes `base_url`/`api_key`/`model` — no client-class
change needed, only a small factory choosing which env vars to read).
HOW: `build_model_client(provider, role)` resolves the
`<PROVIDER>_MODEL_<ROLE>` / `<PROVIDER>_BASE_URL` / `<PROVIDER>_API_KEY`
environment variables (mirroring `agents.orchestrator._client_for`'s
existing Fireworks-only convention) and constructs a `ModelClient`.
`get_model_info(provider, role)` reports the currently-configured model id
only (never the API key) for read-only surfaces (API route, CLI
subcommand, TUI panel) — this module never fabricates a model id: an
unset env var reports `configured=False`, never a placeholder string.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from engineering_studio.fireworks_client import ModelClient

__all__ = ["ModelInfo", "PROVIDERS", "ROLES", "build_model_client", "get_model_info"]

# WHAT: The two provider profiles this factory currently understands.
# WHY: Matches .env.example's two provider blocks (FIREWORKS_*, OPENAI_*).
PROVIDERS: tuple[str, ...] = ("fireworks", "openai")

# WHAT: The three pipeline roles every provider profile routes independently.
# WHY: Mirrors the existing 3-way split (`FIREWORKS_MODEL_ORCHESTRATOR` /
# `_SPECIALIST` / `_RESEARCH`) already consumed by `agents.orchestrator`.
ROLES: tuple[str, ...] = ("orchestrator", "specialist", "research")

_BASE_URL_ENV_VAR: dict[str, str] = {
    "fireworks": "FIREWORKS_BASE_URL",
    "openai": "OPENAI_BASE_URL",
}
_API_KEY_ENV_VAR: dict[str, str] = {
    "fireworks": "FIREWORKS_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def _validate(provider: str, role: str) -> None:
    """WHAT: Rejects an unknown provider/role before touching any env var.

    RAISES:
        ValueError: If `provider` is not in `PROVIDERS` or `role` is not
            in `ROLES`.
    """
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r} — expected one of {PROVIDERS}.")
    if role not in ROLES:
        raise ValueError(f"Unknown role {role!r} — expected one of {ROLES}.")


def _model_env_var(provider: str, role: str) -> str:
    """WHAT: Builds the `<PROVIDER>_MODEL_<ROLE>` environment variable name.

    ARGS:
        provider (str): One of `PROVIDERS`.
        role (str): One of `ROLES`.

    RETURNS:
        str: e.g. "OPENAI_MODEL_SPECIALIST".
    """
    _validate(provider, role)
    return f"{provider.upper()}_MODEL_{role.upper()}"


@dataclass(frozen=True)
class ModelInfo:
    """WHAT: A read-only, key-free snapshot of one role's model routing.

    ATTRIBUTES:
        role (str): One of `ROLES`.
        provider (str): One of `PROVIDERS`.
        model (str | None): The configured model id, or None if unset.
        configured (bool): True iff `model` is a non-empty string.

    WHY: Lets the API/CLI/TUI surfaces show a judge *which* model answers
    *which* stage (INVESTIGATE.md §5) without ever exposing `api_key`.
    """

    role: str
    provider: str
    model: str | None
    configured: bool


def get_model_info(provider: str, role: str) -> ModelInfo:
    """WHAT: Reports the currently-configured model id for one role, if any.

    ARGS:
        provider (str): One of `PROVIDERS`.
        role (str): One of `ROLES`.

    RETURNS:
        ModelInfo: Never raises for an unset model id — `configured` is
        False and `model` is None in that case; only raises for a genuinely
        unknown provider/role name (a programming-time error, not a
        configuration-time one).

    RAISES:
        ValueError: If `provider` or `role` is not recognized.
    """
    model = os.environ.get(_model_env_var(provider, role), "")
    return ModelInfo(role=role, provider=provider, model=model or None, configured=bool(model))


def build_model_client(provider: str, role: str) -> ModelClient:
    """WHAT: Constructs a `ModelClient` for one (provider, role) pair.

    ARGS:
        provider (str): One of `PROVIDERS`.
        role (str): One of `ROLES`.

    RETURNS:
        ModelClient: Configured with that provider's base URL, API key,
        and the role's configured model id.

    RAISES:
        ValueError: If `provider`/`role` is unrecognized, or if the
            `<PROVIDER>_MODEL_<ROLE>` environment variable is unset — this
            factory never fabricates a model id to unblock a caller.
    """
    model_env_var = _model_env_var(provider, role)
    model = os.environ.get(model_env_var, "")
    if not model:
        raise ValueError(f"{model_env_var} is not set (see .env.example).")
    return ModelClient(
        model=model,
        base_url=os.environ.get(_BASE_URL_ENV_VAR[provider]),
        api_key=os.environ.get(_API_KEY_ENV_VAR[provider]),
    )
