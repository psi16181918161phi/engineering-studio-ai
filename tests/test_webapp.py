"""WHAT: Unit tests for engineering_studio.webapp (W6a FastAPI+Jinja2 app).
WHY: The webapp must prove it renders pages using only
`utils.palette.PALETTE_B` tokens (no hard-coded color literals reaching
the response) and that it genuinely round-trips through the wrapped
`engineering_studio.api` app rather than reimplementing pipeline logic.
HOW: Monkeypatches `engineering_studio.sdk.run_pipeline` (no real
network/model call); drives the app via FastAPI's `TestClient`, one
fresh `create_app()` instance per test.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from engineering_studio import sdk
from engineering_studio.utils.palette import PALETTE_B
from engineering_studio.webapp import create_app


def test_index_page_renders_form_and_palette(tmp_path: Path) -> None:
    client = TestClient(create_app(artifacts_root=tmp_path))
    response = client.get("/")
    assert response.status_code == 200
    assert "Product brief" in response.text
    assert PALETTE_B.background in response.text
    assert PALETTE_B.foreground_primary in response.text


def test_run_success_renders_result_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_outputs = {"research": tmp_path / "research" / "output.md"}
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)
    client = TestClient(create_app(artifacts_root=tmp_path))

    response = client.post("/run", data={"product_brief": "build a drone"})

    assert response.status_code == 200
    assert "build a drone" in response.text
    assert "research" in response.text


def test_run_validation_error_rerenders_form_with_error(tmp_path: Path) -> None:
    client = TestClient(create_app(artifacts_root=tmp_path))
    response = client.post("/run", data={"product_brief": "   "})
    assert response.status_code == 200
    assert "Product brief" in response.text
    assert "must not be blank" in response.text


def test_view_result_roundtrip_and_unknown_id(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_outputs = {"research": tmp_path / "research" / "output.md"}
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)
    client = TestClient(create_app(artifacts_root=tmp_path))

    run_response = client.post("/run", data={"product_brief": "build a drone"})
    # Extract the job id embedded in the rendered result page's heading.
    text = run_response.text
    job_id = text.split("Job ")[1].split("<")[0].strip()

    view_response = client.get(f"/pipeline/{job_id}")
    assert view_response.status_code == 200
    assert "build a drone" in view_response.text

    missing_response = client.get("/pipeline/does-not-exist")
    assert missing_response.status_code == 200
    assert "no pipeline job found" in missing_response.text


def test_module_level_app_is_a_ready_instance() -> None:
    from engineering_studio.webapp import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
