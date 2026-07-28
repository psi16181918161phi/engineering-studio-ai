"""WHAT: Unit tests for `demo._playwright_demo_script.core.server`.
WHY: Isolates the subprocess/network I/O this module wraps so no test
here spawns a real uvicorn process or binds a real HTTP client.
HOW: Monkeypatches `subprocess.Popen` and `requests.get`.
"""

from __future__ import annotations

from typing import Any

import pytest

from demo._playwright_demo_script.core import server as server_module
from demo._playwright_demo_script.exceptions.errors import ServerStartError
from tests.demo.conftest import FakeProcess


def test_free_port_returns_a_bindable_port() -> None:
    port = server_module.free_port()
    assert isinstance(port, int)
    assert 0 < port < 65536


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def test_start_server_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_env: dict[str, Any] = {}

    def fake_popen(cmd: list[str], env: dict[str, str], cwd: Any) -> FakeProcess:
        captured_env.update(env)
        return FakeProcess()

    monkeypatch.setattr(server_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(server_module.requests, "get", lambda url, timeout=0.5: _FakeResponse(200))

    process, base_url = server_module.start_server(live=False)

    assert isinstance(process, FakeProcess)
    assert base_url.startswith("http://127.0.0.1:")
    assert captured_env["ENGINEERING_STUDIO_FAKE_PIPELINE"] == "1"


def test_start_server_live_skips_fake_pipeline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_env: dict[str, Any] = {}

    def fake_popen(cmd: list[str], env: dict[str, str], cwd: Any) -> FakeProcess:
        captured_env.update(env)
        return FakeProcess()

    monkeypatch.setattr(server_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(server_module.requests, "get", lambda url, timeout=0.5: _FakeResponse(200))

    server_module.start_server(live=True)

    assert "ENGINEERING_STUDIO_FAKE_PIPELINE" not in captured_env


def test_start_server_retries_after_transient_connection_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(server_module.subprocess, "Popen", lambda *a, **k: FakeProcess())
    monkeypatch.setattr(server_module.time, "sleep", lambda seconds: None)

    attempts = iter([server_module.requests.RequestException("not up yet"), None])

    def flaky_get(url: str, timeout: float = 0.5) -> _FakeResponse:
        outcome = next(attempts)
        if outcome is not None:
            raise outcome
        return _FakeResponse(200)

    monkeypatch.setattr(server_module.requests, "get", flaky_get)

    process, base_url = server_module.start_server(live=False)

    assert base_url.startswith("http://127.0.0.1:")


def test_start_server_raises_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    process = FakeProcess()

    monkeypatch.setattr(server_module.subprocess, "Popen", lambda *a, **k: process)

    def always_fails(url: str, timeout: float = 0.5) -> _FakeResponse:
        raise server_module.requests.RequestException("connection refused")

    monkeypatch.setattr(server_module.requests, "get", always_fails)

    with pytest.raises(ServerStartError):
        server_module.start_server(live=False, startup_timeout=0.0)

    assert process.terminated is True
