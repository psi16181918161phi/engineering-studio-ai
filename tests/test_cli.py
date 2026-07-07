"""WHAT: Unit tests for engineering_studio.cli (the `main()` entry point)
and engineering_studio.cli.commands (the `run`/`status`/`artifacts`
subcommand implementations).
WHY: W4 migrated the CLI onto `sdk.EngineeringStudioClient` instead of
calling `agents.orchestrator.run_pipeline` directly, and added the
`status`/`artifacts` read-only introspection subcommands — all three
paths, plus the legacy bare-brief invocation form, need coverage.
HOW: Monkeypatches `engineering_studio.sdk.run_pipeline` (the seam the
SDK itself is tested against, see `test_sdk.py`) rather than mocking
HTTP/network calls, and `chdir`s into `tmp_path` so any default
`runs/latest/artifacts` directory never touches the real working tree.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio import cli, sdk
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

    monkeypatch.setattr(sdk, "run_pipeline", _raise)

    exit_code = cli.main(["build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "network down" in captured.out


def test_main_returns_1_on_blank_legacy_brief(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = cli.main(["run", "   "])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Invalid product brief" in captured.out


def test_main_prints_artifact_paths_on_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    fake_outputs = {
        "research": tmp_path / "research" / "output.md",
        "mechanical": tmp_path / "mechanical" / "output.md",
    }
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)

    exit_code = cli.main(["build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "build a drone" in captured.out
    assert "mechanical" in captured.out
    assert str(fake_outputs["mechanical"]) in captured.out


def test_main_run_subcommand_honors_explicit_artifacts_root(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    custom_root = tmp_path / "custom-artifacts"
    fake_outputs = {"research": custom_root / "research" / "output.md"}
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)

    exit_code = cli.main(["run", "--artifacts-root", str(custom_root), "build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(custom_root) in captured.out


def test_main_run_subcommand_with_no_brief_prints_usage(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    exit_code = cli.main(["run", "--artifacts-root", str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Usage" in captured.out


def test_main_returns_2_on_pipeline_execution_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    def _raise(product_brief: str, artifacts_root: Path) -> dict[str, Path]:
        raise RuntimeError("unexpected boom")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)

    exit_code = cli.main(["run", "--artifacts-root", str(tmp_path), "build", "a", "drone"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Pipeline execution failed" in captured.out


def test_main_status_reports_missing_root(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    missing_root = tmp_path / "does-not-exist"

    exit_code = cli.main(["status", "--artifacts-root", str(missing_root)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No artifacts found" in captured.out


def test_main_status_lists_discipline_folders(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = tmp_path / "artifacts"
    (root / "mechanical").mkdir(parents=True)
    (root / "research").mkdir(parents=True)

    exit_code = cli.main(["status", "--artifacts-root", str(root)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "mechanical" in captured.out
    assert "research" in captured.out


def test_main_status_reports_empty_root(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = tmp_path / "artifacts"
    root.mkdir()

    exit_code = cli.main(["status", "--artifacts-root", str(root)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "contains no discipline output yet" in captured.out


def test_main_artifacts_reports_missing_root(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    missing_root = tmp_path / "does-not-exist"

    exit_code = cli.main(["artifacts", "--artifacts-root", str(missing_root)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No artifacts found" in captured.out


def test_main_artifacts_reports_empty_root(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = tmp_path / "artifacts"
    root.mkdir()

    exit_code = cli.main(["artifacts", "--artifacts-root", str(root)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "contains no files" in captured.out


def test_main_artifacts_lists_files(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    (root / "mechanical").mkdir(parents=True)
    (root / "mechanical" / "output.md").write_text("content", encoding="utf-8")

    exit_code = cli.main(["artifacts", "--artifacts-root", str(root)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "mechanical" in captured.out
    assert "output.md" in captured.out
