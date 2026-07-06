"""WHAT: Unit tests for ModelClient.complete()'s network/response branches.
WHY: Closes the remaining 0%-covered lines in fireworks_client.py (the
success path, HTTP-error path, network-exception path, and malformed-
response-shape path) without making any real network call.
HOW: Monkeypatches `requests.post` in the `fireworks_client` module with a
fake callable returning a stand-in response object (or raising), per
branch under test.
"""

from __future__ import annotations

from typing import Any

import pytest
import requests

from engineering_studio import fireworks_client
from engineering_studio.fireworks_client import ModelClient, ModelUnavailableError


class _FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> Any:
        return self._payload


def _client() -> ModelClient:
    return ModelClient(
        model="accounts/fireworks/models/test",
        base_url="https://example.invalid",
        api_key="fake-key",
    )


def test_complete_returns_content_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_response = _FakeResponse(
        200, {"choices": [{"message": {"content": "hello world"}}]}
    )
    monkeypatch.setattr(fireworks_client.requests, "post", lambda *a, **kw: fake_response)

    result = _client().complete("system", "user")

    assert result == "hello world"


def test_complete_raises_on_non_200_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_response = _FakeResponse(500, "internal error")
    monkeypatch.setattr(fireworks_client.requests, "post", lambda *a, **kw: fake_response)

    with pytest.raises(ModelUnavailableError, match="HTTP 500"):
        _client().complete("system", "user")


def test_complete_raises_on_network_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(fireworks_client.requests, "post", _raise)

    with pytest.raises(ModelUnavailableError, match="network error"):
        _client().complete("system", "user")


def test_complete_raises_on_malformed_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_response = _FakeResponse(200, {"unexpected": "shape"})
    monkeypatch.setattr(fireworks_client.requests, "post", lambda *a, **kw: fake_response)

    with pytest.raises(ModelUnavailableError, match="unexpected response shape"):
        _client().complete("system", "user")
