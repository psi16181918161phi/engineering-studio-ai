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
import os
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

import pytest

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


def _wait_for_terminal(
    store: runs_module.RunStore, run_id: str, timeout: float = 2.0
) -> dict[str, Any]:
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


@pytest.mark.parametrize("detail", [None, "worker already reported an error"])
def test_load_from_disk_marks_interrupted_run_as_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, detail: str | None
) -> None:
    """WHAT: Recover interrupted runs with their diagnostic detail intact.

    WHY: The restart fallback must not erase information captured before shutdown.
    HOW: Exercise rehydration with and without a preexisting diagnostic.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    run_dir = tmp_path / "20260101-000000-interrupted"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260101-000000-interrupted",
                "product_brief": "a brief cut short",
                "status": "running",
                **({"detail": detail} if detail is not None else {}),
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
    if detail is None:
        assert "restart" in (state["detail"] or "")
    else:
        assert state["detail"] == detail


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
                "stages": {
                    "research": {"status": "error", "detail": "same reason", "updated_at": 1234.0}
                },
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


def test_persist_locked_logs_and_does_not_raise_on_os_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WHAT: Check best-effort persistence when the destination is a directory.

    WHY: A refused publication must not stop the live run.
    HOW: Leave the conflicting destination in place and assert the warning.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    run = runs_module.RunState(run_id="broken-run", product_brief="a brief")
    run_dir = tmp_path / "broken-run"
    run_dir.mkdir()
    (run_dir / "run.json").mkdir()

    with store._lock:
        store._persist_locked(run)

    assert "failed to persist run state for broken-run" in caplog.text
    assert list(run_dir.iterdir()) == [run_dir / "run.json"]


@pytest.mark.parametrize("has_prior_snapshot", [False, True])
def test_partial_snapshot_write_preserves_previous_publication(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    has_prior_snapshot: bool,
) -> None:
    """WHAT: Exercise a write that fails after emitting a prefix.

    WHY: A failed update cannot publish incomplete JSON or destroy prior state.
    HOW: Write a real prefix and raise before the replacement can begin.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    prior = runs_module.RunState(run_id="partial", product_brief="previous state")
    run_dir = tmp_path / prior.run_id
    snapshot = run_dir / "run.json"
    run_dir.mkdir()
    previous = (json.dumps(prior.to_dict(), indent=2) + "\n").encode()
    if has_prior_snapshot:
        snapshot.write_bytes(previous)

    write_text = Path.write_text

    def fail_after_prefix(path: Path, data: str, **kwargs: Any) -> int:
        """WHAT: Fail after a real write. WHY: Model a torn staged snapshot.

        HOW: Save an incomplete JSON prefix before raising OSError.
        """
        write_text(path, data[:8], **kwargs)
        raise OSError("injected partial snapshot write")

    monkeypatch.setattr(Path, "write_text", fail_after_prefix)
    updated = runs_module.RunState(run_id=prior.run_id, product_brief="new state")
    with store._lock:
        store._persist_locked(updated)

    if has_prior_snapshot:
        assert snapshot.read_bytes() == previous
    else:
        assert not snapshot.exists()
    assert list(run_dir.iterdir()) == ([snapshot] if has_prior_snapshot else [])
    assert "failed to persist run state for partial" in caplog.text


def test_replace_failure_keeps_committed_snapshot_and_cleans_staging(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WHAT: Keep the old snapshot when commit is refused.

    WHY: Staging success alone has no publication effect.
    HOW: Observe the full staged update and inject a replacement failure.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    prior = runs_module.RunState(run_id="refused", product_brief="previous state")
    updated = runs_module.RunState(run_id=prior.run_id, product_brief="new state")
    snapshot = tmp_path / prior.run_id / "run.json"
    snapshot.parent.mkdir()
    previous = json.dumps(prior.to_dict()).encode()
    snapshot.write_bytes(previous)
    replacements: list[Path] = []

    def refuse(source: Path, destination: Path) -> None:
        """WHAT: Refuse one publication. WHY: Test the commit boundary.

        HOW: Check the input and destination before raising an OSError.
        """
        replacements.append(source)
        assert destination == snapshot
        assert source != snapshot
        assert json.loads(source.read_bytes()) == updated.to_dict()
        assert destination.read_bytes() == previous
        raise PermissionError("injected replacement refusal")

    monkeypatch.setattr(os, "replace", refuse)
    with store._lock:
        store._persist_locked(updated)

    assert len(replacements) == 1
    assert snapshot.read_bytes() == previous
    assert list(snapshot.parent.iterdir()) == [snapshot]
    assert "failed to persist run state for refused" in caplog.text


def test_snapshot_publication_replaces_previous_bytes_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Check exact snapshots before and after publication.

    WHY: Writing the canonical path in place exposes unfinished state.
    HOW: Capture the sibling stage and canonical paths at the real replace call.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    prior = runs_module.RunState(run_id="replace", product_brief="previous state")
    updated = runs_module.RunState(run_id=prior.run_id, product_brief="new state")
    snapshot = tmp_path / prior.run_id / "run.json"
    snapshot.parent.mkdir()
    previous = json.dumps(prior.to_dict()).encode()
    snapshot.write_bytes(previous)
    replace = os.replace
    replacements: list[Path] = []

    def inspect_then_replace(source: Path, destination: Path) -> None:
        """WHAT: Observe then commit. WHY: Preserve the visibility boundary.

        HOW: Check both paths immediately before calling the real replacement.
        """
        replacements.append(source)
        assert destination == snapshot
        assert source.parent.parent == destination.parent
        assert destination.read_bytes() == previous
        assert json.loads(source.read_bytes()) == updated.to_dict()
        replace(source, destination)

    monkeypatch.setattr(os, "replace", inspect_then_replace)
    with store._lock:
        store._persist_locked(updated)

    assert len(replacements) == 1
    assert json.loads(snapshot.read_bytes()) == updated.to_dict()
    assert list(snapshot.parent.iterdir()) == [snapshot]


def test_cleanup_failure_after_replace_keeps_new_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WHAT: Preserve a completed replacement if staging cleanup fails.

    WHY: Cleanup runs after publication and cannot undo the new snapshot.
    HOW: Raise on context exit after observing the complete new document.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    store = runs_module.RunStore()
    prior = runs_module.RunState(run_id="cleanup", product_brief="previous state")
    updated = runs_module.RunState(run_id=prior.run_id, product_brief="new state")
    snapshot = tmp_path / prior.run_id / "run.json"
    snapshot.parent.mkdir()
    snapshot.write_text(json.dumps(prior.to_dict()), encoding="utf-8")
    published = json.dumps(updated.to_dict()).encode()
    staging_paths: list[Path] = []

    @contextmanager
    def fail_cleanup(*, dir: Path, prefix: str) -> Iterator[str]:
        """WHAT: Refuse staging cleanup. WHY: Exercise the postcommit boundary.

        HOW: Retain the directory and raise after confirming atomic replacement.
        """
        directory = mkdtemp(dir=dir, prefix=prefix)
        staging_paths.append(Path(directory))
        yield directory
        assert snapshot.read_bytes() == published
        raise PermissionError("injected cleanup refusal")

    monkeypatch.setattr(runs_module, "TemporaryDirectory", fail_cleanup)
    with store._lock:
        store._persist_locked(updated)

    assert snapshot.read_bytes() == published
    assert len(staging_paths) == 1
    assert staging_paths[0].is_dir()
    assert "failed to persist run state for cleanup" in caplog.text


def test_load_from_disk_ignores_run_state_staging_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """WHAT: Recover only published run state.

    WHY: An interrupted writer may leave an unread staging directory behind.
    HOW: Leave complete staged JSON in both published and never-published runs.
    """
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    committed = runs_module.RunState(run_id="published", product_brief="committed", status="done")
    (tmp_path / committed.run_id).mkdir()
    (tmp_path / committed.run_id / "run.json").write_text(
        json.dumps(committed.to_dict()), encoding="utf-8"
    )
    for run_id in ("published", "never-published"):
        stage = tmp_path / run_id / ".run-state-orphan"
        stage.mkdir(parents=True)
        pending = runs_module.RunState(run_id=run_id, product_brief="staged only", status="done")
        (stage / "run.json").write_text(json.dumps(pending.to_dict()), encoding="utf-8")
    store = runs_module.RunStore()

    store.load_from_disk()

    assert store.list_runs() == [committed.to_dict()]
