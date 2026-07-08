"""WHAT: Unit tests for the command-and-control HTTP/SSE routes
(`engineering_studio.api.health`, `engineering_studio.api.runs`).
WHY: These routes are the only contract the frontend/ dashboard depends
on; a regression here (wrong status code, malformed SSE frame, wrong
404 behavior) breaks the live demo silently. 100% coverage per the
repo's coverage gate.
HOW: Builds a small standalone FastAPI app that mounts only the two
routers under test, with `engineering_studio.api.runs.runs` monkeypatched
to a fresh, isolated `RunStore` per test (never the process-global
singleton) whose own `run_pipeline` dependency is further monkeypatched
to a fast fake — no real network/model calls, no cross-test state leaks.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import engineering_studio.api.runs as api_runs_module
import engineering_studio.runs as runs_module
from engineering_studio.api.health import router as health_router
from engineering_studio.api.runs import router as runs_router


def _fake_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: Callable[[str, str, str | None], None] | None = None,
) -> dict[str, Path]:
    assert on_event is not None
    on_event("research", "running", None)
    path = Path(artifacts_root) / "research" / "output.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("research output", encoding="utf-8")
    on_event("research", "done", str(path))
    return {"research": path}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    """WHAT: A TestClient over an isolated app/store pair.

    HOW: Patches the module-level `runs` singleton `api.runs` imports
    from (not the shared process-global one) and its `run_pipeline`
    dependency, so every test gets a clean, fast, isolated store.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()
    monkeypatch.setattr(api_runs_module, "runs", store)

    app = FastAPI()
    app.include_router(health_router)
    app.include_router(runs_router)
    return TestClient(app)


def _wait_for_terminal(client: TestClient, run_id: str, timeout: float = 2.0) -> dict:
    deadline = time.time() + timeout
    state = client.get(f"/api/runs/{run_id}").json()
    while state["status"] not in {"done", "error"} and time.time() < deadline:
        time.sleep(0.02)
        state = client.get(f"/api/runs/{run_id}").json()
    return state


def test_health_route_reports_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_run_returns_run_id_and_get_run_returns_snapshot(client: TestClient) -> None:
    response = client.post("/api/runs", json={"product_brief": "build a small drone"})

    assert response.status_code == 200
    run_id = response.json()["run_id"]
    assert run_id

    state = _wait_for_terminal(client, run_id)
    assert state["status"] == "done"
    assert state["product_brief"] == "build a small drone"


def test_create_run_rejects_blank_brief(client: TestClient) -> None:
    response = client.post("/api/runs", json={"product_brief": ""})

    assert response.status_code == 422


def test_list_runs_returns_created_runs(client: TestClient) -> None:
    first = client.post("/api/runs", json={"product_brief": "first brief"}).json()["run_id"]
    second = client.post("/api/runs", json={"product_brief": "second brief"}).json()["run_id"]

    listed_ids = {run["run_id"] for run in client.get("/api/runs").json()}
    assert {first, second} <= listed_ids


def test_get_run_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist")

    assert response.status_code == 404


def test_get_artifact_returns_content_once_written(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    _wait_for_terminal(client, run_id)

    response = client.get(f"/api/runs/{run_id}/artifacts/research")

    assert response.status_code == 200
    assert response.json() == {"stage": "research", "content": "research output"}


def test_get_artifact_unknown_run_returns_404(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/artifacts/research")

    assert response.status_code == 404


def test_get_artifact_not_ready_returns_404(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]

    response = client.get(f"/api/runs/{run_id}/artifacts/business")

    assert response.status_code == 404


def test_stream_run_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/api/runs/does-not-exist/stream")

    assert response.status_code == 404


def test_stream_run_yields_initial_snapshot_and_terminates(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    _wait_for_terminal(client, run_id)

    with client.stream("GET", f"/api/runs/{run_id}/stream") as response:
        assert response.status_code == 200
        lines = list(response.iter_lines())

    assert any(line.startswith("data: ") for line in lines)


def test_stream_run_forwards_live_events_until_terminal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Exercises the SSE loop's non-terminal-at-connect-time branch:
    subscribe before the run finishes, then observe the stream forward at
    least one live stage event followed by the terminal run event.
    """

    def _slow_pipeline(
        product_brief: str,
        artifacts_root: Path,
        on_event: Callable[[str, str, str | None], None] | None = None,
    ) -> dict[str, Path]:
        assert on_event is not None
        on_event("research", "running", None)
        time.sleep(0.1)
        on_event("research", "done", "ok")
        return {"research": Path(artifacts_root) / "research" / "output.md"}

    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _slow_pipeline)
    store = runs_module.RunStore()
    monkeypatch.setattr(api_runs_module, "runs", store)

    app = FastAPI()
    app.include_router(health_router)
    app.include_router(runs_router)
    slow_client = TestClient(app)

    run_id = slow_client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]

    with slow_client.stream("GET", f"/api/runs/{run_id}/stream") as response:
        assert response.status_code == 200
        events = []
        for line in response.iter_lines():
            if line.startswith("data: "):
                events.append(line)
            if len(events) >= 2:
                break
    assert len(events) >= 2


def test_stream_run_sends_keepalive_comment_while_waiting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Exercises the SSE loop's `queue.Empty` keep-alive branch by
    shrinking the keep-alive interval to a few milliseconds and holding
    the fake pipeline's terminal event back long enough for at least one
    keep-alive comment line to be sent first.
    """
    monkeypatch.setattr(api_runs_module, "_KEEPALIVE_SECONDS", 0.01)

    def _very_slow_pipeline(
        product_brief: str,
        artifacts_root: Path,
        on_event: Callable[[str, str, str | None], None] | None = None,
    ) -> dict[str, Path]:
        assert on_event is not None
        time.sleep(0.2)
        on_event("research", "done", "ok")
        return {"research": Path(artifacts_root) / "research" / "output.md"}

    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _very_slow_pipeline)
    store = runs_module.RunStore()
    monkeypatch.setattr(api_runs_module, "runs", store)

    app = FastAPI()
    app.include_router(health_router)
    app.include_router(runs_router)
    slow_client = TestClient(app)

    run_id = slow_client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]

    with slow_client.stream("GET", f"/api/runs/{run_id}/stream") as response:
        assert response.status_code == 200
        lines = list(response.iter_lines())

    assert any(line.startswith(": keep-alive") for line in lines)
