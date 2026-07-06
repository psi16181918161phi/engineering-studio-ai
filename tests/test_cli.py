"""WHAT: Unit tests for engineering_studio.cli (the `main()` entry point).
WHY: `main()` was previously at 0% coverage — must exercise the usage,
success, and model-failure exit paths without any real network call.
HOW: Monkeypatches `cli.run_pipeline` directly rather than mocking HTTP,
and `chdir`s into `tmp_path` so the `runs/latest/artifacts` directory it
creates never touches the real working tree.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio import cli
from engineering_studio.fireworks_client import ModelUnavailableError


def test_main_prints_usage_and_returns_1_when_no_args(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Usage" in captured.out


def test_main_returns_2_on_model_unavailable_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    def _raise(product_brief: str, artifacts_root: Path) -> dict[str, Path]:
        raise ModelUnavailableError("network down")

    monkeypatch.setattr(cli, "run_pipeline", _raise)

    exit_code = cli.main(["build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "network down" in captured.out


def test_main_prints_artifact_paths_on_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    fake_outputs = {
        "research": tmp_path / "research.md",
        "mechanical": tmp_path / "mech.md",
    }
    monkeypatch.setattr(cli, "run_pipeline", lambda brief, root: fake_outputs)

    exit_code = cli.main(["build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "build a drone" in captured.out
    assert "mechanical" in captured.out
    assert str(fake_outputs["mechanical"]) in captured.out
