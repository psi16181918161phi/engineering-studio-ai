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
    fake_response = _FakeResponse(200, {"choices": [{"message": {"content": "hello world"}}]})
    monkeypatch.setattr(fireworks_client.requests, "post", lambda *a, **kw: fake_response)

    result = _client().complete("system", "user")

    assert result == "hello world"


def test_complete_raises_on_non_200_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_response = _FakeResponse(500, "internal error")
    monkeypatch.setattr(fireworks_client.requests, "post", lambda *a, **kw: fake_response)

    with pytest.raises(ModelUnavailableError, match="HTTP 500"):
        _client().complete("system", "user")


def test_complete_omits_unconfigured_reasoning_effort(monkeypatch: pytest.MonkeyPatch) -> None:
    """WHAT: Verify the JSON request omits an unset reasoning control.

    WHY: OpenAI-compatible endpoints may reject this provider-specific field.
    HOW: Capture the serialized request payload with a local response double.
    """
    payloads: list[dict[str, Any]] = []

    def capture_request(_url: str, *, json: dict[str, Any], **_options: Any) -> _FakeResponse:
        """WHAT: Capture the outgoing JSON and return a valid completion.

        WHY: Inspect the wire contract without creating a network connection.
        HOW: Store the payload before returning the canned response.
        """
        payloads.append(json)
        return _FakeResponse(200, {"choices": [{"message": {"content": "offline reply"}}]})

    monkeypatch.setattr(fireworks_client.requests, "post", capture_request)
    client = ModelClient(
        model="test",
        base_url="https://example.invalid",
        api_key="fake-key",
        reasoning_effort=None,
    )

    assert client.complete("system", "user") == "offline reply"
    assert len(payloads) == 1
    assert "reasoning_effort" not in payloads[0]
    assert payloads[0]["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]


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
