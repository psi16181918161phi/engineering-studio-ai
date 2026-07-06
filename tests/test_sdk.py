"""WHAT: Unit tests for engineering_studio.sdk.EngineeringStudioClient.
WHY: The SDK is the first layer meant to be depended on by future
webapp/GUI/API code — must reach 100% coverage and prove it normalizes
every failure into this package's own exception hierarchy.
HOW: Monkeypatches `sdk.run_pipeline` directly; no real network/model call.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio import sdk
from engineering_studio.exceptions import (
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)
from engineering_studio.models import PipelineResult


def test_default_artifacts_root_matches_cli_default() -> None:
    client = sdk.EngineeringStudioClient()
    assert client.artifacts_root == Path("runs") / "latest" / "artifacts"


def test_custom_artifacts_root_is_honored(tmp_path: Path) -> None:
    client = sdk.EngineeringStudioClient(artifacts_root=tmp_path / "custom")
    assert client.artifacts_root == tmp_path / "custom"


def test_run_rejects_blank_brief_before_any_pipeline_call(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _unexpected_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("run_pipeline should not be called for invalid input")

    monkeypatch.setattr(sdk, "run_pipeline", _unexpected_call)
    client = sdk.EngineeringStudioClient(artifacts_root=tmp_path)

    with pytest.raises(ValidationError):
        client.run("   ")


def test_run_returns_typed_pipeline_result_on_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_outputs = {
        "research": tmp_path / "research" / "output.md",
        "mechanical": tmp_path / "mechanical" / "output.md",
    }
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)
    client = sdk.EngineeringStudioClient(artifacts_root=tmp_path)

    result = client.run("build a small survey drone")

    assert isinstance(result, PipelineResult)
    assert result.product_brief.text == "build a small survey drone"
    assert result.artifact_for("mechanical") == fake_outputs["mechanical"]
    assert client.artifacts_root.exists()


def test_run_propagates_model_unavailable_error_unchanged(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise ModelUnavailableError("network down")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    client = sdk.EngineeringStudioClient(artifacts_root=tmp_path)

    with pytest.raises(ModelUnavailableError, match="network down"):
        client.run("build a small survey drone")


def test_run_wraps_unexpected_error_in_pipeline_execution_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise RuntimeError("unexpected boom")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    client = sdk.EngineeringStudioClient(artifacts_root=tmp_path)

    with pytest.raises(PipelineExecutionError, match="unexpected boom") as exc_info:
        client.run("build a small survey drone")
    assert isinstance(exc_info.value.__cause__, RuntimeError)
