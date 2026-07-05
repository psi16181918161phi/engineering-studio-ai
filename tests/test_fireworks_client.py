"""WHAT: Unit tests for the Fireworks AI client error handling.
WHY: Must never raise a fabricated success — verify failure paths surface
ModelUnavailableError instead of silently returning garbage.
HOW: Constructs the client with a bogus base_url/api_key; no live network
call is expected to succeed, so this only exercises the guard clauses
that don't require network access.
"""

from __future__ import annotations

import pytest

from engineering_studio.fireworks_client import ModelClient, ModelUnavailableError


def test_missing_api_key_raises_before_network_call() -> None:
    client = ModelClient(model="accounts/fireworks/models/test", base_url="https://example.invalid")
    with pytest.raises(ModelUnavailableError, match="FIREWORKS_API_KEY"):
        client.complete("system", "user")


def test_missing_base_url_raises_value_error() -> None:
    with pytest.raises(ValueError, match="FIREWORKS_BASE_URL"):
        ModelClient(model="accounts/fireworks/models/test", base_url="", api_key="x")
