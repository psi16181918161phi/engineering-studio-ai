"""WHAT: Unit tests for the `engineering_studio.webapp` FastAPI app
instance (`app.py` and its `__init__.py` re-export).
WHY: Proves the single-process command-and-control app wires the health
route, the runs routes, and CORS middleware together correctly, and that
`webapp:app` (the uvicorn entry point) resolves to the same instance.
HOW: Imports the real, already-constructed module-level `app` (no
per-test app factory exists for this module — matching `AGENTS.md` §1's
"one process, one running app" story) and drives it with a plain FastAPI
`TestClient`. The standard import mounts the repository's frontend.
A separate module load tests API-only startup with no frontend.
"""

from __future__ import annotations

from importlib.util import find_spec, module_from_spec, spec_from_file_location
from pathlib import Path

import dotenv
import pytest
from fastapi.testclient import TestClient

from engineering_studio.runs import runs
from engineering_studio.webapp import app as webapp_app_reexport
from engineering_studio.webapp.app import app


def test_webapp_reexports_the_same_app_instance() -> None:
    assert webapp_app_reexport is app


def test_webapp_health_route_is_mounted() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webapp_models_route_is_mounted() -> None:
    # WHAT: OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md Phase 4.2 — the model-routing
    # route must be registered on the real app instance, not only testable
    # in isolation (see tests/test_api_models.py for the full behavior).
    client = TestClient(app)

    response = client.get("/api/models")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


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


def test_webapp_without_frontend_still_exposes_health(monkeypatch: pytest.MonkeyPatch) -> None:
    """WHAT: Confirm API-only installations can start without frontend files.

    WHY: Some deployments use the API without a static dashboard directory.
    HOW: Load a separate application instance from the real module source,
    simulating a missing frontend and suppressing history/config reload.
    """
    original = find_spec("engineering_studio.webapp.app")
    assert original is not None and original.origin is not None
    source = Path(original.origin)
    frontend = source.resolve().parents[3] / "frontend"
    original_is_dir = Path.is_dir

    def is_dir(path: Path) -> bool:
        """WHAT: Simulate an absent dashboard directory.

        WHY: Avoid modifying repository files during the import.
        HOW: Override only the frontend path and delegate every other query.
        """
        return path != frontend and original_is_dir(path)

    spec = spec_from_file_location("_engineering_studio_api_only_test", source)
    assert spec is not None and spec.loader is not None
    isolated = module_from_spec(spec)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "is_dir", is_dir)
        patch.setattr(dotenv, "load_dotenv", lambda: False)
        patch.setattr(runs, "load_from_disk", lambda: None)
        spec.loader.exec_module(isolated)

    with TestClient(isolated.app) as client:
        assert client.get("/").status_code == 404
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
