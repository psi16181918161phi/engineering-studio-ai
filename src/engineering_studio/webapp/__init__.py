"""WHAT: FastAPI + Jinja2 server-rendered webapp consuming the API (W6a).
WHY: Gives the demo a browser-facing surface without a separate JS build
toolchain (PREPLAN Q4) — every page here is rendered server-side and its
only interaction with pipeline logic is over the `engineering_studio.api`
ASGI app (W5), consumed in-process via an `httpx` ASGI transport rather
than duplicating `sdk.EngineeringStudioClient` calls directly, per
AGENTS.md §1 (this package owns "how it looks", `api/` owns "the
contract", `sdk/` owns "the pipeline").
HOW: `create_app()` builds the `engineering_studio.api` app once, wraps
it in an in-process `httpx.AsyncClient` (via `httpx.ASGITransport` — no
real socket, no separate server process), and exposes two human-facing
routes: `GET /` (a brief-submission form) and `POST /run` (submits the
form, calls `POST /pipeline/run` on the wrapped API client, and renders
the result). Pages are styled exclusively from
`utils.palette.PALETTE_B` (the mandated Variant B interface-surface
palette) passed into the Jinja2 template context — no template hard-codes
a color literal.
"""

from __future__ import annotations

from pathlib import Path

import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from engineering_studio.api import create_app as create_api_app
from engineering_studio.utils.palette import get_palette_for_surface

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _render_api_response(
    templates: Jinja2Templates,
    request: Request,
    response: httpx.Response,
    palette: object,
    product_brief: str,
) -> HTMLResponse:
    """WHAT: Renders either the result page or the error-annotated form,
    given a response already received from the wrapped API app.

    ARGS:
        templates (Jinja2Templates): The webapp's template environment.
        request (Request): The incoming webapp request (for template context).
        response (httpx.Response): The API app's response to re-render.
        palette (object): The Variant B palette tokens for this page.
        product_brief (str): The brief text to re-populate the form with
            on an error (empty string for the read-only `view_result` route).

    RETURNS:
        HTMLResponse: The rendered page.

    WHY: Extracted into an ordinary (non-async) function, called as a
    single statement immediately after each route's `await api_client...`
    call, so the branching logic itself executes in a normal call frame
    rather than directly inside the coroutine's post-await continuation.
    """
    if response.status_code >= 400:
        detail = response.json().get("detail", response.text)
        return templates.TemplateResponse(
            request,
            "index.html",
            {"palette": palette, "product_brief": product_brief, "error": detail},
            status_code=200,
        )
    return templates.TemplateResponse(
        request, "result.html", {"palette": palette, "result": response.json()}
    )


def create_app(artifacts_root: Path | str | None = None) -> FastAPI:
    """WHAT: Builds a fresh webapp `FastAPI` instance, consuming its own
    freshly-built `engineering_studio.api` app in-process.

    ARGS:
        artifacts_root (Path | str | None): Forwarded to the wrapped API
            app's `EngineeringStudioClient`.

    RETURNS:
        FastAPI: A ready-to-serve (or ready-to-test-via-`TestClient`) app.

    WHY: A factory (not one shared module-level app) so tests get an
    isolated API app + job registry per webapp instance, matching the
    isolation pattern already used by `engineering_studio.api.create_app`.
    """
    webapp = FastAPI(title="Engineering Studio AI Webapp", version="0.1.0")
    api_app = create_api_app(artifacts_root=artifacts_root)
    api_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=api_app), base_url="http://api.internal"
    )
    templates = Jinja2Templates(directory=_TEMPLATES_DIR)
    palette = get_palette_for_surface("webapp")

    @webapp.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        """WHAT: Renders the brief-submission form."""
        return templates.TemplateResponse(
            request, "index.html", {"palette": palette, "product_brief": "", "error": None}
        )

    @webapp.post("/run", response_class=HTMLResponse)
    async def run(request: Request, product_brief: str = Form(...)) -> HTMLResponse:
        """WHAT: Submits `product_brief` to the wrapped API's
        `POST /pipeline/run` and renders either the result or the
        original form annotated with the API's error detail.

        WHY: Never re-implements validation/pipeline-execution logic —
        the API app (W5) is the single source of truth for both.
        """
        response = await api_client.post("/pipeline/run", json={"product_brief": product_brief})
        return _render_api_response(templates, request, response, palette, product_brief)

    @webapp.get("/pipeline/{job_id}", response_class=HTMLResponse)
    async def view_result(request: Request, job_id: str) -> HTMLResponse:
        """WHAT: Re-renders a previously-run job's result page by id."""
        response = await api_client.get(f"/pipeline/{job_id}")
        return _render_api_response(templates, request, response, palette, "")

    return webapp


app = create_app()

__all__ = ["create_app", "app"]
