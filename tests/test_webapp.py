"""WHAT: Unit tests for the `engineering_studio.webapp` FastAPI app
instance (`app.py` and its `__init__.py` re-export).
WHY: Proves the single-process command-and-control app wires the health
route, the runs routes, and CORS middleware together correctly, and that
`webapp:app` (the uvicorn entry point) resolves to the same instance.
HOW: Imports the real, already-constructed module-level `app` (no
per-test app factory exists for this module — matching `AGENTS.md` §1's
"one process, one running app" story) and drives it with a plain FastAPI
`TestClient`. The repo's real `frontend/` directory exists on disk, so
the static-files mount branch executes as part of just importing the
module; no monkeypatching of that path is needed or attempted.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from engineering_studio.webapp import app as webapp_app_reexport
from engineering_studio.webapp.app import app


def test_webapp_reexports_the_same_app_instance() -> None:
    assert webapp_app_reexport is app


def test_webapp_health_route_is_mounted() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webapp_serves_frontend_index_at_root() -> None:
    client = TestClient(app)

    response = client.get("/")

    # WHAT: frontend/index.html exists in this repo, so the StaticFiles
    # mount (html=True) serves it at "/" rather than 404ing.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_webapp_cors_headers_present_on_preflight() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://example.invalid",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
