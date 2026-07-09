"""WHAT: Unit tests for `engineering_studio.api.downloads` (per-stage
artifact download, run-level zip download).
WHY: These routes back the "Download output" / "Download all (.zip)"
affordances added to the dashboard; a regression here would silently
break a user's ability to actually take away a run's recommendations.
HOW: Mirrors tests/test_api.py's isolated-app + fake-pipeline pattern —
own FastAPI app, own RunStore, own monkeypatched run_pipeline, no real
network/model calls.
"""

from __future__ import annotations

import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import engineering_studio.api.downloads as api_downloads_module
import engineering_studio.api.runs as api_runs_module
import engineering_studio.runs as runs_module
from engineering_studio.api.downloads import router as downloads_router
from engineering_studio.api.runs import router as runs_router


def _fake_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: Callable[[str, str, str | None], None] | None = None,
) -> dict[str, Path]:
    assert on_event is not None
    on_event("research", "running", None)
    path = Path(artifacts_root) / "research" / "output.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("research findings body", encoding="utf-8")
    on_event("research", "done", str(path))
    return {"research": path}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setattr(runs_module, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(runs_module, "run_pipeline", _fake_pipeline)
    store = runs_module.RunStore()
    monkeypatch.setattr(api_runs_module, "runs", store)
    monkeypatch.setattr(api_downloads_module, "runs", store)

    app = FastAPI()
    app.include_router(runs_router)
    app.include_router(downloads_router)
    return TestClient(app)


def _wait_for_terminal(client: TestClient, run_id: str, timeout: float = 2.0) -> dict:
    deadline = time.time() + timeout
    state = client.get(f"/api/runs/{run_id}").json()
    while state["status"] not in {"done", "error"} and time.time() < deadline:
        time.sleep(0.02)
        state = client.get(f"/api/runs/{run_id}").json()
    return state


def test_download_artifact_returns_file_with_content_disposition(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    _wait_for_terminal(client, run_id)

    res = client.get(f"/api/runs/{run_id}/artifacts/research/download")

    assert res.status_code == 200
    assert res.content == b"research findings body"
    assert 'attachment; filename="research-output.md"' in res.headers["content-disposition"]


def test_download_artifact_404_for_unknown_run(client: TestClient) -> None:
    res = client.get("/api/runs/does-not-exist/artifacts/research/download")
    assert res.status_code == 404


def test_download_artifact_404_when_not_ready(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    res = client.get(f"/api/runs/{run_id}/artifacts/mechanical/download")
    assert res.status_code == 404


def test_download_all_returns_zip_with_ready_artifacts(client: TestClient) -> None:
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    _wait_for_terminal(client, run_id)

    res = client.get(f"/api/runs/{run_id}/download")

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert f'attachment; filename="{run_id}-artifacts.zip"' in res.headers["content-disposition"]
    with zipfile.ZipFile(BytesIO(res.content)) as archive:
        assert archive.namelist() == ["research-output.md"]
        assert archive.read("research-output.md") == b"research findings body"


def test_download_all_404_for_unknown_run(client: TestClient) -> None:
    res = client.get("/api/runs/does-not-exist/download")
    assert res.status_code == 404


def test_download_all_409_when_nothing_ready(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _never_finishes(
        product_brief: str,
        artifacts_root: Path,
        on_event: Callable[[str, str, str | None], None] | None = None,
    ) -> dict[str, Path]:
        assert on_event is not None
        on_event("research", "running", None)
        time.sleep(5)  # never actually reached within this test's lifetime
        return {}

    monkeypatch.setattr(runs_module, "run_pipeline", _never_finishes)
    run_id = client.post("/api/runs", json={"product_brief": "brief"}).json()["run_id"]
    res = client.get(f"/api/runs/{run_id}/download")
    assert res.status_code == 409
