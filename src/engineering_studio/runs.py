"""WHAT: In-memory run registry + pub/sub that backs the command-and-control
web API.
WHY: Lets the FastAPI layer track per-stage status/artifacts for concurrent
pipeline runs and stream live updates over Server-Sent Events, without the
orchestrator itself knowing anything about HTTP, threading, or transport.
HOW: One process-global `runs` RunStore instance (single-process hackathon
deploy). Each run gets a dict-based, lock-guarded RunState; each subscriber
gets its own `queue.SimpleQueue` fed by `_publish` so no client can block
another. `run_pipeline` is dispatched on a daemon thread per run so the
FastAPI event loop is never blocked by a live model call.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from queue import SimpleQueue
from typing import Any

from engineering_studio.agents.orchestrator import STAGE_MODEL_ENV_VAR, STAGE_ORDER
from engineering_studio.fireworks_client import ModelUnavailableError

_LOGGER = logging.getLogger("engineering_studio")

# WHAT: Swap in the deterministic, no-network fake pipeline when explicitly
# opted into via ENGINEERING_STUDIO_FAKE_PIPELINE=1.
# WHY: Lets Playwright end-to-end tests (tests/e2e/) drive a real, live
# `uvicorn` subprocess without a Fireworks API key or network access,
# without any test needing to monkeypatch across the process boundary.
# Never enabled implicitly — a real deploy or the unit-test suite (which
# monkeypatches this same module attribute directly) is unaffected.
if os.environ.get("ENGINEERING_STUDIO_FAKE_PIPELINE") == "1":  # pragma: no cover
    # Only ever exercised via a subprocess launched by tests/e2e/ (see
    # conftest.py's live_server fixture) — never by the unit-test suite,
    # which monkeypatches this module's `run_pipeline` attribute directly.
    from engineering_studio.testing.fake_pipeline import fake_run_pipeline as run_pipeline
else:
    from engineering_studio.agents.orchestrator import run_pipeline

# WHAT: Root directory under which every web-triggered run writes its
# artifacts, one subfolder per run id.
# WHY: The CLI (cli.py) uses runs/latest/artifacts for a single ad hoc run;
# the web API supports concurrent/historical runs, so each gets its own
# namespaced folder instead of overwriting "latest".
RUNS_ROOT = Path("runs")


@dataclass
class StageState:
    """WHAT: Live status of one pipeline stage within one run.

    ATTRIBUTES:
        status (str): "pending" | "running" | "done" | "error".
        detail (str | None): Artifact path on success, error text on failure.
        updated_at (float): Unix timestamp of the last status change.
    """

    status: str = "pending"
    detail: str | None = None
    updated_at: float = field(default_factory=time.time)


@dataclass
class RunState:
    """WHAT: Full state of one pipeline run.

    ATTRIBUTES:
        run_id (str): Opaque, URL-safe identifier.
        product_brief (str): The one-sentence brief this run was launched with.
        status (str): "pending" | "running" | "done" | "error".
        detail (str | None): Terminal-state explanation — the exception
            message when status is "error", otherwise None. Persisted here
            (not just published over SSE) so it survives a dropped/missed
            connection and is retrievable later via list_runs()/get().
        created_at (float): Unix timestamp the run was created.
        stages (dict[str, StageState]): One entry per STAGE_ORDER id.
    """

    run_id: str
    product_brief: str
    status: str = "pending"
    detail: str | None = None
    created_at: float = field(default_factory=time.time)
    stages: dict[str, StageState] = field(
        default_factory=lambda: {name: StageState() for name in STAGE_ORDER}
    )
    models: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """WHAT: Renders this run as a JSON-serializable snapshot.

        RETURNS:
            dict[str, Any]: Stable shape consumed by the frontend dashboard
                (and, doubling as this run's on-disk persistence format —
                see RunStore._persist_locked/load_from_disk below).
        """
        return {
            "run_id": self.run_id,
            "product_brief": self.product_brief,
            "status": self.status,
            "detail": self.detail,
            "created_at": self.created_at,
            "stage_order": list(STAGE_ORDER),
            "stages": {
                name: {"status": s.status, "detail": s.detail, "updated_at": s.updated_at}
                for name, s in self.stages.items()
            },
            "models": self.models,
        }


class RunStore:
    """WHAT: Thread-safe registry of pipeline runs plus an SSE-style pub/sub.

    WHY: One agent (the orchestrator) produces the engineering deliverable;
    this class is the separate, narrowly-scoped bookkeeper that tracks its
    progress for the command-and-control surface — it never touches
    pipeline logic itself (SRP, AGENTS.md §2).

    HOW: A single lock guards two dicts (runs, subscribers); pipeline
    execution happens on a daemon thread per run so callers are never
    blocked waiting on a live model call.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runs: dict[str, RunState] = {}
        self._subscribers: dict[str, list[SimpleQueue[dict[str, Any]]]] = {}

    def list_runs(self) -> list[dict[str, Any]]:
        """WHAT: Returns every known run, most recently created first."""
        with self._lock:
            snapshot = sorted(self._runs.values(), key=lambda r: r.created_at, reverse=True)
            return [r.to_dict() for r in snapshot]

    def get(self, run_id: str) -> dict[str, Any] | None:
        """WHAT: Returns one run's current snapshot, or None if unknown."""
        with self._lock:
            run = self._runs.get(run_id)
            return run.to_dict() if run else None

    def artifact_path(self, run_id: str, stage: str) -> Path | None:
        """WHAT: Resolves a stage's artifact file if the run exists and it
        has been written.

        RETURNS:
            Path | None: The output.md path, or None if the run or file
                does not exist.
        """
        with self._lock:
            if run_id not in self._runs:
                return None
        candidate = RUNS_ROOT / run_id / "artifacts" / stage / "output.md"
        return candidate if candidate.exists() else None

    def start_run(self, product_brief: str) -> str:
        """WHAT: Registers a new run and launches it on a background thread.

        ARGS:
            product_brief (str): The one-sentence hackathon demo prompt.

        RETURNS:
            str: The newly created run id.
        """
        run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        models = {stage: os.environ.get(env_var, "") for stage, env_var in STAGE_MODEL_ENV_VAR.items()}
        run = RunState(run_id=run_id, product_brief=product_brief, models=models)
        with self._lock:
            self._runs[run_id] = run
            self._subscribers[run_id] = []
            self._persist_locked(run)
        thread = threading.Thread(
            target=self._execute, args=(run_id, product_brief), daemon=True
        )
        thread.start()
        return run_id

    def subscribe(self, run_id: str) -> SimpleQueue[dict[str, Any]]:
        """WHAT: Registers a new live-event listener for one run.

        RETURNS:
            SimpleQueue[dict]: Queue that will receive every subsequent
                stage/run event dict published for this run id.
        """
        queue: SimpleQueue[dict[str, Any]] = SimpleQueue()
        with self._lock:
            self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    def _publish(self, run_id: str, event: dict[str, Any]) -> None:
        with self._lock:
            subscribers = list(self._subscribers.get(run_id, []))
        for queue in subscribers:
            queue.put(event)

    def _on_event(self, run_id: str, stage: str, status: str, detail: str | None) -> None:
        with self._lock:
            run = self._runs[run_id]
            run.stages[stage] = StageState(status=status, detail=detail)
            if run.status == "pending" and status == "running":
                run.status = "running"
            self._persist_locked(run)
        self._publish(run_id, {"type": "stage", "stage": stage, "status": status, "detail": detail})

    def _execute(self, run_id: str, product_brief: str) -> None:
        artifacts_root = RUNS_ROOT / run_id / "artifacts"
        artifacts_root.mkdir(parents=True, exist_ok=True)
        try:
            run_pipeline(
                product_brief,
                artifacts_root,
                on_event=lambda stage, status, detail: self._on_event(
                    run_id, stage, status, detail
                ),
            )
        except ModelUnavailableError as exc:
            self._finish(run_id, "error", str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - a run must always reach a terminal status
            self._finish(run_id, "error", str(exc))
            return
        self._finish(run_id, "done", None)

    def _finish(self, run_id: str, status: str, detail: str | None) -> None:
        with self._lock:
            run = self._runs[run_id]
            run.status = status
            run.detail = detail
            self._persist_locked(run)
        self._publish(run_id, {"type": "run", "status": status, "detail": detail})

    def _persist_locked(self, run: RunState) -> None:
        """WHAT: Writes one run's current state to `<run>/run.json`.

        WHY: `RunState` otherwise lives only in this process's memory —
        restarting the server (a redeploy, a crash) silently erased every
        run's history and status. The artifacts themselves already survive
        on disk (`<run>/artifacts/<stage>/output.md`); this sidecar makes
        the bookkeeping around them (status, timestamps, which models ran)
        survive too, so `load_from_disk()` can rehydrate it at startup.

        HOW: Caller must already hold `self._lock` — this both prevents a
        torn/interleaved write when two stages finish near-simultaneously
        and keeps the write on the same thread that just computed `run`'s
        new state (no second read-modify-write race). Best-effort: a
        write failure (e.g. disk full) is logged, never raised, since
        losing persistence must never crash a live pipeline run.
        """
        path = RUNS_ROOT / run.run_id / "run.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(run.to_dict()), encoding="utf-8")
        except OSError:
            _LOGGER.warning("failed to persist run state for %s", run.run_id, exc_info=True)

    def load_from_disk(self) -> None:
        """WHAT: Rehydrates every run found under RUNS_ROOT/*/run.json into
        memory, restoring history across a server restart.

        WHY: Called once at web-app startup (see webapp/app.py) — without
        it, every run's status/history is lost on redeploy even though the
        underlying artifact files are still sitting on disk untouched.

        HOW: Any run still "running" (or any stage still "running") when
        the server stopped can never actually finish — its background
        thread is gone — so it's rewritten as "error"/"interrupted" on
        load rather than shown as perpetually "Running…" with no way to
        ever complete. Malformed/unreadable run.json files are skipped,
        never fatal to startup.
        """
        if not RUNS_ROOT.is_dir():
            return
        for run_dir in sorted(RUNS_ROOT.iterdir()):
            run_json = run_dir / "run.json"
            if not run_json.is_file():
                continue
            try:
                data = json.loads(run_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("skipping unreadable run state at %s", run_json, exc_info=True)
                continue

            run = RunState(
                run_id=data.get("run_id", run_dir.name),
                product_brief=data.get("product_brief", ""),
                status=data.get("status", "error"),
                detail=data.get("detail"),
                created_at=data.get("created_at", 0.0),
                models=data.get("models", {}),
            )
            for name, stage_data in data.get("stages", {}).items():
                if name not in run.stages:
                    continue
                status = stage_data.get("status", "pending")
                detail = stage_data.get("detail")
                if status == "running":
                    status = "error"
                    detail = "Interrupted by a server restart before this stage finished."
                run.stages[name] = StageState(
                    status=status,
                    detail=detail,
                    updated_at=stage_data.get("updated_at", 0.0),
                )
            if run.status == "running":
                run.status = "error"
                if run.detail is None:
                    run.detail = "Interrupted by a server restart before this run finished."

            with self._lock:
                self._runs[run.run_id] = run
                self._subscribers.setdefault(run.run_id, [])


# WHAT: Process-global run registry.
# WHY: A single-process hackathon deploy has exactly one FastAPI app and
# therefore exactly one place runs need to live; importing this module
# elsewhere always gets the same store.
runs = RunStore()
