"""WHAT: Artifact-download routes for the command-and-control API — a
single stage's raw file, or every artifact from one run zipped together.
WHY: Complements `api.runs.get_artifact` (JSON text preview): users asked
to be able to actually download a completed run's recommended outcome,
not just read it in the browser (per session directive: "users can
actually download the recommended outcome").
HOW: Reuses `engineering_studio.runs.runs` for existence/readiness
checks (never re-implements run-state logic here — SRP); zips are built
in-memory with `zipfile.ZipFile` over a `BytesIO` buffer, since a demo
run's artifact set is a handful of small Markdown files, not large binary
output.
"""

from __future__ import annotations

import io
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from engineering_studio.agents.orchestrator import STAGE_ORDER
from engineering_studio.runs import runs

router = APIRouter(prefix="/api/runs", tags=["downloads"])


@router.get("/{run_id}/artifacts/{stage}/download")
def download_artifact(run_id: str, stage: str) -> Response:
    """WHAT: Downloads one stage's artifact as a file attachment.

    RAISES:
        HTTPException: 404 if the run is unknown or the artifact is not
            ready yet (stage still pending/running, or never reached).
    """
    if runs.get(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    path = runs.artifact_path(run_id, stage)
    if path is None:
        raise HTTPException(status_code=404, detail="artifact not ready")
    return Response(
        content=path.read_bytes(),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{stage}-output.md"'},
    )


@router.get("/{run_id}/download")
def download_all_artifacts(run_id: str) -> Response:
    """WHAT: Downloads every ready artifact from one run as a single
    `.zip` file.

    RAISES:
        HTTPException: 404 if the run is unknown, or 409 if no stage has
            produced an artifact yet.
    """
    if runs.get(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")

    buffer = io.BytesIO()
    written = 0
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for stage in STAGE_ORDER:
            path = runs.artifact_path(run_id, stage)
            if path is None:
                continue
            archive.write(path, arcname=f"{stage}-output.md")
            written += 1

    if written == 0:
        raise HTTPException(status_code=409, detail="no artifacts ready yet")

    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_id}-artifacts.zip"'},
    )
