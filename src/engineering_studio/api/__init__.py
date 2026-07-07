"""WHAT: FastAPI application exposing the studio pipeline over HTTP (W5).
WHY: Gives non-Python callers (webapp W6a, external tooling, demo
scripting) a transport-layer surface without reimplementing pipeline
logic — every route here delegates to `sdk.EngineeringStudioClient`,
never to `agents.orchestrator` directly, per `AGENTS.md` §1 (routes call
the SDK, they do not reimplement it).
HOW: `create_app()` builds a fresh `FastAPI` instance bound to one
in-memory job registry (`dict[str, PipelineResult]`). This registry is
intentionally NOT persisted to disk or a database: per the
live-data-honesty rule (constitution rule 8 / `AGENTS.md` §5), a restart
losing in-memory jobs is an honest, disclosed limitation rather than a
fabricated "durable job store". `POST /pipeline/run` executes the
pipeline synchronously (matching the SDK's synchronous `run()` — no
background task queue exists yet) and returns the new job's id
immediately alongside its result; `GET /pipeline/{id}` re-fetches that
same in-memory record; `GET /health` reports process liveness only, not
downstream model-backend health (a false "healthy" would violate
live-data-honesty).
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engineering_studio.exceptions import (
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)
from engineering_studio.models import PipelineResult
from engineering_studio.sdk import EngineeringStudioClient

_DEFAULT_ARTIFACTS_ROOT = Path("runs") / "latest" / "artifacts"


class PipelineRunRequest(BaseModel):
    """WHAT: Request body for `POST /pipeline/run`.

    ATTRIBUTES:
        product_brief (str): One-sentence hackathon demo prompt.
    """

    product_brief: str = Field(..., min_length=1, max_length=2000)


class SpecialistArtifactOut(BaseModel):
    """WHAT: JSON-safe representation of one `models.SpecialistArtifact`."""

    discipline: str
    output_path: str


class PipelineRunResponse(BaseModel):
    """WHAT: Response body for both `POST /pipeline/run` and
    `GET /pipeline/{id}`.

    ATTRIBUTES:
        id (str): Server-generated job id (uuid4 hex), valid only for the
            lifetime of the current process (see module docstring).
        product_brief (str): The validated brief that produced this result.
        artifacts (list[SpecialistArtifactOut]): One entry per discipline
            stage that produced output.
    """

    id: str
    product_brief: str
    artifacts: list[SpecialistArtifactOut]

    @classmethod
    def from_result(cls, job_id: str, result: PipelineResult) -> PipelineRunResponse:
        """WHAT: Builds a JSON-safe response from a typed `PipelineResult`."""
        return cls(
            id=job_id,
            product_brief=result.product_brief.text,
            artifacts=[
                SpecialistArtifactOut(
                    discipline=artifact.discipline,
                    output_path=str(artifact.output_path),
                )
                for artifact in result.artifacts
            ],
        )


class HealthResponse(BaseModel):
    """WHAT: Response body for `GET /health`."""

    status: str = "ok"


def create_app(artifacts_root: Path | str | None = None) -> FastAPI:
    """WHAT: Builds a fresh `FastAPI` app instance bound to its own SDK
    client and in-memory job registry.

    ARGS:
        artifacts_root (Path | str | None): Forwarded to
            `EngineeringStudioClient`; defaults to `runs/latest/artifacts`.

    RETURNS:
        FastAPI: A ready-to-serve (or ready-to-test-via-`TestClient`) app.

    WHY: A factory function (rather than one shared module-level app with
    mutable global state) so tests can construct an isolated app/registry
    per test without cross-test contamination.
    """
    app = FastAPI(title="Engineering Studio AI API", version="0.1.0")
    client = EngineeringStudioClient(
        artifacts_root=Path(artifacts_root) if artifacts_root is not None else _DEFAULT_ARTIFACTS_ROOT
    )
    jobs: dict[str, PipelineResult] = {}

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """WHAT: Liveness probe. Reports process liveness only — never
        claims a downstream model backend is reachable."""
        return HealthResponse()

    @app.post("/pipeline/run", response_model=PipelineRunResponse, status_code=201)
    def run_pipeline_route(request: PipelineRunRequest) -> PipelineRunResponse:
        """WHAT: Runs the full pipeline synchronously and records the
        result under a new job id.

        RAISES:
            HTTPException(422): Invalid product brief.
            HTTPException(503): Model backend unavailable.
            HTTPException(500): Unexpected pipeline failure.
        """
        try:
            result = client.run(request.product_brief)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ModelUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except PipelineExecutionError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        job_id = uuid.uuid4().hex
        jobs[job_id] = result
        return PipelineRunResponse.from_result(job_id, result)

    @app.get("/pipeline/{job_id}", response_model=PipelineRunResponse)
    def get_pipeline_result(job_id: str) -> PipelineRunResponse:
        """WHAT: Re-fetches a previously-run job's result by id.

        RAISES:
            HTTPException(404): No such job in this process's in-memory
                registry (never running, or process has since restarted).
        """
        result = jobs.get(job_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"no pipeline job found for id={job_id!r} "
                "(never run in this process, or the process has since restarted)",
            )
        return PipelineRunResponse.from_result(job_id, result)

    return app


app = create_app()

__all__ = [
    "create_app",
    "app",
    "PipelineRunRequest",
    "PipelineRunResponse",
    "SpecialistArtifactOut",
    "HealthResponse",
]
