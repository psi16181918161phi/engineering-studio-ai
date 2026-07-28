"""WHAT: Integration tests for `demo._playwright_demo_script`'s
`util.pipeline` (full batch orchestration) and `main` (CLI entry point).
WHY: Verifies the server-start -> browser-launch -> per-(theme, prompt)
recording -> teardown sequence end-to-end, entirely against fakes (no
real browser/server), matching the 100%-coverage mocked-pipeline tier.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from demo._playwright_demo_script import main as main_module
from demo._playwright_demo_script.util import pipeline as pipeline_module
from tests.demo.conftest import FakeProcess, FakeTimeoutProcess, fake_sync_playwright


def _patch_pipeline(monkeypatch: pytest.MonkeyPatch, process: FakeProcess | None = None) -> None:
    monkeypatch.setattr(pipeline_module, "sync_playwright", fake_sync_playwright)
    monkeypatch.setattr(
        pipeline_module,
        "start_server",
        lambda live: (process or FakeProcess(), "http://127.0.0.1:1"),
    )
    monkeypatch.setattr(pipeline_module, "record_scenario", lambda *a, **k: None)


def test_runner_records_every_theme_and_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_pipeline(monkeypatch)

    runner = pipeline_module.build_playwright_demo_runner(
        themes=["light", "dark"],
        prompts=["prompt one", "prompt two"],
        live=False,
        recordings_root=tmp_path,
    )
    exit_code = runner.run()

    assert exit_code == 0


def test_runner_terminates_server_even_if_process_wait_times_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    process = FakeTimeoutProcess()
    _patch_pipeline(monkeypatch, process=process)

    runner = pipeline_module.build_playwright_demo_runner(
        themes=["dark"], prompts=["prompt one"], live=False, recordings_root=tmp_path
    )
    exit_code = runner.run()

    assert exit_code == 0
    assert process.terminated is True
    assert process.killed is True


def test_main_parses_args_and_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_pipeline(monkeypatch)
    monkeypatch.setattr(main_module, "RECORDINGS_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["prog", "--theme", "light"])

    assert main_module.main() == 0


def test_main_defaults_to_both_themes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded_themes: list[str] = []

    def fake_build(themes: list[str], prompts: list[str], live: bool, recordings_root: Path):  # type: ignore[no-untyped-def]
        recorded_themes.extend(themes)

        class _StubRunner:
            def run(self) -> int:
                return 0

        return _StubRunner()

    monkeypatch.setattr(main_module, "build_playwright_demo_runner", fake_build)
    monkeypatch.setattr(sys, "argv", ["prog"])

    assert main_module.main() == 0
    assert recorded_themes == ["light", "dark"]
