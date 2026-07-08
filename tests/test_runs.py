"""WHAT: Unit tests for the in-memory RunStore backing the command-and-
control web API.
WHY: The API layer trusts RunStore to reach a terminal status and to fan
out live stage events; a threading bug here would silently hang the SSE
endpoint the frontend depends on.
HOW: Monkeypatches engineering_studio.runs.run_pipeline with a fast fake
that calls on_event synchronously — no network, no real model calls, no
FastAPI TestClient needed to exercise the store's own concurrency.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import engineering_studio.runs as runs_module


def _fake_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: Callable[[str, str, str | None], None] | None = None,
) -> dict[str, Path]:
    assert on_event is not None
    # WHAT: Small delays give a subscriber that attaches immediately after
    # start_run() a real chance to receive every event, mirroring how a
    # browser's EventSource connects right after the POST /api/runs response.
    time.sleep(0.05)
    on_event("research", "running", None)
    time.sleep(0.05)
    on_event("research", "done", "ok")
    return {"research": Path(artifacts_root) / "research" / "output.md"}


def _wait_for_terminal(store: runs_module.RunStore, run_id: str, timeout: float = 2.0) -> dict[str, Any]:
    deadline = time.time() + timeout
    state = store.get(run_id)
    while state is not None and state["status"] not in {"done", "error"} and time.time() < deadline:
        time.sleep(0.02)
        state = store.get(run_id)
    assert state is not None
    return state


def test_start_run_reaches_done_and_updates_stage(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    state = _wait_for_terminal(store, run_id)

    assert state["status"] == "done"
    assert state["stages"]["research"]["status"] == "done"
    assert state["stages"]["research"]["detail"] == "ok"
    # Stages never dispatched by the fake pipeline stay "pending" until a
    # terminal status is reached; the API layer is what maps that to
    # "skipped" for display (see frontend/app.js markRemainingPendingAsSkipped).
    assert state["stages"]["quality_gate"]["status"] == "pending"


def test_unknown_run_id_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()

    assert store.get("does-not-exist") is None
    assert store.artifact_path("does-not-exist", "research") is None


def test_subscribe_receives_stage_and_run_events(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    queue = store.subscribe(run_id)

    events = [queue.get(timeout=2.0) for _ in range(3)]
    kinds = [(event["type"], event.get("status")) for event in events]

    assert ("stage", "running") in kinds
    assert ("stage", "done") in kinds
    assert ("run", "done") in kinds


def test_list_runs_sorted_most_recent_first(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()

    first_id = store.start_run("first brief")
    time.sleep(0.01)
    second_id = store.start_run("second brief")

    _wait_for_terminal(store, first_id)
    _wait_for_terminal(store, second_id)

    listed_ids = [run["run_id"] for run in store.list_runs()]
    assert listed_ids[0] == second_id
    assert listed_ids[1] == first_id
