"""WHAT: HTTP/SSE routes exposing the multi-agent pipeline as a
command-and-control surface for the frontend dashboard.
WHY: Keeps transport-layer wiring (routes, request/response models)
separate from orchestration logic (AGENTS.md §1) — every handler below
calls into `engineering_studio.runs.runs`, never reimplements pipeline or
threading logic.
HOW: POST /api/runs starts a background pipeline run and returns its id;
GET endpoints expose a point-in-time snapshot, a live Server-Sent-Events
stream of stage transitions, and per-stage artifact text.
"""

from __future__ import annotations

import asyncio
import json
from queue import Empty
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from engineering_studio.runs import runs

router = APIRouter(prefix="/api/runs", tags=["runs"])

# WHAT: How long the SSE stream waits for a new event before sending a
# comment-only keep-alive line.
# WHY: Prevents idle proxies/browsers from timing out the connection while
# a long-running model call is in progress between stage transitions.
_KEEPALIVE_SECONDS = 15.0


class CreateRunRequest(BaseModel):
    """WHAT: Request body for launching a new pipeline run.

    ATTRIBUTES:
        product_brief (str): One-sentence product brief, 1-2000 chars.
    """

    product_brief: str = Field(min_length=1, max_length=2000)


@router.post("")
def create_run(payload: CreateRunRequest) -> dict[str, str]:
    """WHAT: Launches a new pipeline run in the background.

    RETURNS:
        dict[str, str]: {"run_id": <new run id>}.
    """
    run_id = runs.start_run(payload.product_brief.strip())
    return {"run_id": run_id}


@router.get("")
def list_runs() -> list[dict[str, Any]]:
    """WHAT: Lists every known run, most recent first."""
    return runs.list_runs()


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    """WHAT: Returns one run's current snapshot.

    RAISES:
        HTTPException: 404 if run_id is unknown.
    """
    state = runs.get(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="run not found")
    return state


@router.get("/{run_id}/artifacts/{stage}")
def get_artifact(run_id: str, stage: str) -> dict[str, str]:
    """WHAT: Returns the raw text of one stage's written artifact.

    RAISES:
        HTTPException: 404 if the run is unknown or the artifact does not
            exist yet (stage still pending/running, or run failed before
            reaching it).
    """
    if runs.get(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    path = runs.artifact_path(run_id, stage)
    if path is None:
        raise HTTPException(status_code=404, detail="artifact not ready")
    return {"stage": stage, "content": path.read_text(encoding="utf-8")}


@router.get("/{run_id}/stream")
async def stream_run(run_id: str) -> StreamingResponse:
    """WHAT: Streams live stage/run status transitions as Server-Sent Events.

    HOW: Sends one initial `data:` frame with the full current snapshot,
    then forwards every subsequent event published for this run id until a
    terminal ("done"/"error") run event arrives or the run was already
    terminal when the client connected.

    RAISES:
        HTTPException: 404 if run_id is unknown.
    """
    state = runs.get(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="run not found")

    queue = runs.subscribe(run_id)

    async def event_source():
        yield f"data: {json.dumps(state)}\n\n"
        if state["status"] in {"done", "error"}:
            return
        while True:
            try:
                event = await asyncio.to_thread(queue.get, True, _KEEPALIVE_SECONDS)
            except Empty:
                yield ": keep-alive\n\n"
                continue
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") == "run" and event.get("status") in {"done", "error"}:
                return

    return StreamingResponse(event_source(), media_type="text/event-stream")
