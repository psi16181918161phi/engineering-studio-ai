"""WHAT: Unit tests for engineering_studio.api (W5 FastAPI app).
WHY: The API is the first HTTP-transport surface in this project — must
prove it delegates to the SDK, normalizes domain exceptions to HTTP
status codes, and never fabricates a job result for an unknown id.
HOW: Monkeypatches `engineering_studio.sdk.run_pipeline` (no real
network/model call); drives the app via FastAPI's `TestClient`, one
fresh `create_app()` instance per test to avoid job-registry leakage.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from engineering_studio import sdk
from engineering_studio.api import create_app
from engineering_studio.exceptions import ModelUnavailableError


def test_health_reports_ok(tmp_path: Path) -> None:
    client = TestClient(create_app(artifacts_root=tmp_path))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_pipeline_success_and_get_by_id_roundtrip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_outputs = {"research": tmp_path / "research" / "output.md"}
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)
    client = TestClient(create_app(artifacts_root=tmp_path))

    run_response = client.post("/pipeline/run", json={"product_brief": "build a drone"})
    assert run_response.status_code == 201
    body = run_response.json()
    assert body["product_brief"] == "build a drone"
    assert body["artifacts"] == [
        {"discipline": "research", "output_path": str(fake_outputs["research"])}
    ]
    job_id = body["id"]

    get_response = client.get(f"/pipeline/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json() == body


def test_run_pipeline_rejects_blank_brief_with_422(tmp_path: Path) -> None:
    client = TestClient(create_app(artifacts_root=tmp_path))
    response = client.post("/pipeline/run", json={"product_brief": "   "})
    assert response.status_code == 422


def test_run_pipeline_maps_model_unavailable_to_503(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise ModelUnavailableError("network down")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    client = TestClient(create_app(artifacts_root=tmp_path))

    response = client.post("/pipeline/run", json={"product_brief": "build a drone"})
    assert response.status_code == 503
    assert "network down" in response.json()["detail"]


def test_run_pipeline_maps_unexpected_error_to_500(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise RuntimeError("unexpected boom")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    client = TestClient(create_app(artifacts_root=tmp_path))

    response = client.post("/pipeline/run", json={"product_brief": "build a drone"})
    assert response.status_code == 500


def test_get_unknown_job_id_returns_404_not_a_fabricated_result(tmp_path: Path) -> None:
    client = TestClient(create_app(artifacts_root=tmp_path))
    response = client.get("/pipeline/does-not-exist")
    assert response.status_code == 404
    assert "no pipeline job found" in response.json()["detail"]


def test_module_level_app_is_a_ready_instance() -> None:
    from engineering_studio.api import app

    client = TestClient(app)
    assert client.get("/health").status_code == 200
