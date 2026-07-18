"""WHAT: Read-only route reporting which model answers which pipeline role,
across every supported provider profile (Fireworks AI, OpenAI Hackathon).
WHY: OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md Phase 4.2 — lets a judge (or the
dashboard) visibly confirm which provider/model id is wired to each stage
instead of taking it on faith (INVESTIGATE.md §5). Never returns an API
key — `sdk.get_model_info` only ever reads the `<PROVIDER>_MODEL_<ROLE>`
env var, never `<PROVIDER>_API_KEY`.
HOW: One GET route iterating every (provider, role) pair from
`sdk.PROVIDERS` x `sdk.ROLES` and returning each as a small JSON object
via pydantic's `BaseModel` (consistent with `api.runs`'s response shape).
No live network call is made — this is pure environment-variable
introspection, safe to call before any pipeline run.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from engineering_studio.sdk import PROVIDERS, ROLES, get_model_info

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelInfoResponse(BaseModel):
    """WHAT: The wire representation of one `sdk.ModelInfo` entry.

    ATTRIBUTES:
        role (str): One of `sdk.ROLES`.
        provider (str): One of `sdk.PROVIDERS`.
        model (str | None): Configured model id, or None if unset.
        configured (bool): True iff `model` is set.
    """

    role: str
    provider: str
    model: str | None
    configured: bool


@router.get("")
def list_models() -> list[ModelInfoResponse]:
    """WHAT: Reports the currently-configured model id for every
    (provider, role) pair this deployment understands.

    RETURNS:
        list[ModelInfoResponse]: One entry per `sdk.PROVIDERS` x
        `sdk.ROLES` pair, in that nested iteration order (providers
        outer, roles inner) — never includes an API key value.
    """
    return [
        ModelInfoResponse(**vars(get_model_info(provider, role)))
        for provider in PROVIDERS
        for role in ROLES
    ]
