"""WHAT: Liveness probe for the command-and-control web API.
WHY: Lets the frontend (and any deploy/monitoring tooling) distinguish
"server not reachable" from "server up but a run failed" — a single,
trivial route with no dependency on the pipeline or model backends.
HOW: One GET route returning a static JSON body.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """WHAT: Reports that the API process is up.

    RETURNS:
        dict[str, str]: {"status": "ok"}.
    """
    return {"status": "ok"}
