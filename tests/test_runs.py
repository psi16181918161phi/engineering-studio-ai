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

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import engineering_studio.runs as runs_module
from engineering_studio.fireworks_client import ModelUnavailableError


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


def test_artifact_path_resolves_for_a_known_run(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    _wait_for_terminal(store, run_id)

    # WHAT: research's artifact was actually written by _fake_pipeline's
    # return value being ignored by RunStore (it only tracks status via
    # on_event) -- RunStore resolves the artifact by convention
    # (RUNS_ROOT/run_id/artifacts/<stage>/output.md), so write it directly
    # here to exercise the "exists" branch deterministically.
    artifact_dir = tmp_path / run_id / "artifacts" / "research"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "output.md").write_text("research output", encoding="utf-8")

    assert store.artifact_path(run_id, "research") == artifact_dir / "output.md"
    # A stage that never wrote a file yet resolves to None (still pending).
    assert store.artifact_path(run_id, "business") is None


def _fake_pipeline_raises_model_unavailable(
    product_brief: str,
    artifacts_root: Path,
    on_event: Callable[[str, str, str | None], None] | None = None,
) -> dict[str, Path]:
    assert on_event is not None
    on_event("research", "error", "simulated model-unavailable")
    raise ModelUnavailableError("simulated model-unavailable")


def _fake_pipeline_raises_generic_error(
    product_brief: str,
    artifacts_root: Path,
    on_event: Callable[[str, str, str | None], None] | None = None,
) -> dict[str, Path]:
    assert on_event is not None
    on_event("research", "error", "simulated unexpected failure")
    raise RuntimeError("simulated unexpected failure")


def test_execute_finishes_error_on_model_unavailable(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline_raises_model_unavailable)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    state = _wait_for_terminal(store, run_id)

    assert state["status"] == "error"
    # WHAT: The exception message must be persisted on the run itself, not
    # only published transiently over SSE — otherwise a client that missed
    # the live event (a dropped/reconnecting connection) can never recover
    # the actual reason a run failed via list_runs()/get().
    assert "simulated model-unavailable" in (state["detail"] or "")


def test_execute_finishes_error_on_unexpected_exception(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline_raises_generic_error)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    state = _wait_for_terminal(store, run_id)

    assert state["status"] == "error"
    assert "simulated unexpected failure" in (state["detail"] or "")


def test_start_run_captures_resolved_model_per_stage(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    monkeypatch.setenv("FIREWORKS_MODEL_RESEARCH", "accounts/fireworks/models/research-model")
    monkeypatch.setenv("FIREWORKS_MODEL_SPECIALIST", "accounts/fireworks/models/specialist-model")
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    state = store.get(run_id)

    assert state is not None
    assert state["models"]["research"] == "accounts/fireworks/models/research-model"
    assert state["models"]["mechanical"] == "accounts/fireworks/models/specialist-model"
    assert state["models"]["quality_gate"] == "accounts/fireworks/models/specialist-model"


def test_start_run_writes_run_json_sidecar(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()

    run_id = store.start_run("a test brief")
    _wait_for_terminal(store, run_id)

    run_json = tmp_path / run_id / "run.json"
    assert run_json.is_file()
    data = json.loads(run_json.read_text(encoding="utf-8"))
    assert data["run_id"] == run_id
    assert data["status"] == "done"
    assert data["stages"]["research"]["status"] == "done"


def test_load_from_disk_rehydrates_a_completed_run(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-abcd1234"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260101-000000-abcd1234",
                "product_brief": "a persisted brief",
                "status": "done",
                "created_at": 1234.0,
                "stages": {"research": {"status": "done", "detail": "ok", "updated_at": 1234.0}},
                "models": {"research": "accounts/fireworks/models/research-model"},
            }
        ),
        encoding="utf-8",
    )
    store = runs_module.RunStore()

    store.load_from_disk()
    state = store.get("20260101-000000-abcd1234")

    assert state is not None
    assert state["status"] == "done"
    assert state["product_brief"] == "a persisted brief"
    assert state["stages"]["research"]["status"] == "done"
    assert state["models"]["research"] == "accounts/fireworks/models/research-model"
    listed_ids = [run["run_id"] for run in store.list_runs()]
    assert "20260101-000000-abcd1234" in listed_ids


def test_load_from_disk_marks_interrupted_run_as_error(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-interrupted"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260101-000000-interrupted",
                "product_brief": "a brief cut short",
                "status": "running",
                "created_at": 1234.0,
                "stages": {
                    "research": {"status": "done", "detail": "ok", "updated_at": 1234.0},
                    "mechanical": {"status": "running", "detail": None, "updated_at": 1234.0},
                },
                "models": {},
            }
        ),
        encoding="utf-8",
    )
    store = runs_module.RunStore()

    store.load_from_disk()
    state = store.get("20260101-000000-interrupted")

    assert state is not None
    assert state["status"] == "error"
    assert state["stages"]["research"]["status"] == "done"
    assert state["stages"]["mechanical"]["status"] == "error"
    assert "restart" in state["stages"]["mechanical"]["detail"]
    # WHAT: The persisted run.json had no top-level "detail" (it predates
    # this field / was never set), so the interrupted-on-restart fallback
    # message must be filled in here too — a run-level error must always
    # have *some* human-readable explanation, never a bare None.
    assert "restart" in (state["detail"] or "")


def test_load_from_disk_preserves_persisted_run_level_detail(monkeypatch, tmp_path) -> None:
    """WHAT: A run that already finished with an error before the last
    server restart must keep its original detail message on rehydration —
    load_from_disk() must not overwrite a real, already-terminal detail
    with the generic "interrupted by restart" fallback."""
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-erroredout"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260101-000000-erroredout",
                "product_brief": "a brief that failed cleanly",
                "status": "error",
                "detail": "docs/task-specs.md not found (slug='research-problem-analysis-pass')",
                "created_at": 1234.0,
                "stages": {"research": {"status": "error", "detail": "same reason", "updated_at": 1234.0}},
                "models": {},
            }
        ),
        encoding="utf-8",
    )
    store = runs_module.RunStore()

    store.load_from_disk()
    state = store.get("20260101-000000-erroredout")

    assert state is not None
    assert state["status"] == "error"
    assert state["detail"] == "docs/task-specs.md not found (slug='research-problem-analysis-pass')"


def test_load_from_disk_skips_malformed_run_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-broken"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text("{not valid json", encoding="utf-8")
    store = runs_module.RunStore()

    store.load_from_disk()  # must not raise

    assert store.list_runs() == []


def test_load_from_disk_noop_when_runs_root_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path / "does-not-exist")
    store = runs_module.RunStore()

    store.load_from_disk()  # must not raise

    assert store.list_runs() == []


def test_load_from_disk_skips_run_dir_without_run_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    # WHAT: a run directory with an artifacts/ tree but no run.json sidecar
    # — e.g. a run created before this persistence feature existed.
    (tmp_path / "20260101-000000-no-sidecar" / "artifacts").mkdir(parents=True)
    store = runs_module.RunStore()

    store.load_from_disk()  # must not raise, and must not fabricate a run

    assert store.list_runs() == []


def test_load_from_disk_skips_unknown_stage_name(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-unknownstage"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260101-000000-unknownstage",
                "product_brief": "a brief",
                "status": "done",
                "created_at": 1234.0,
                "stages": {
                    "research": {"status": "done", "detail": "ok", "updated_at": 1234.0},
                    # WHAT: a stage name that predates a STAGE_ORDER rename/removal
                    # — must be skipped, never crash the whole load.
                    "not_a_real_stage": {"status": "done", "detail": "ok", "updated_at": 1234.0},
                },
                "models": {},
            }
        ),
        encoding="utf-8",
    )
    store = runs_module.RunStore()

    store.load_from_disk()
    state = store.get("20260101-000000-unknownstage")

    assert state is not None
    assert "not_a_real_stage" not in state["stages"]
    assert state["stages"]["research"]["status"] == "done"


def test_persist_locked_logs_and_does_not_raise_on_os_error(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    run = runs_module.RunState(run_id="broken-run", product_brief="a brief")
    # WHAT: make the run.json path itself an existing directory, so
    # path.write_text() raises IsADirectoryError (an OSError subclass) —
    # simulates a disk-level failure without needing to mock the filesystem.
    run_dir = tmp_path / "broken-run"
    run_dir.mkdir()
    (run_dir / "run.json").mkdir()

    store._persist_locked(run)  # must log a warning, never raise
