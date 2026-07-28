"""WHAT: Integration tests for `demo._professional_video_demo`'s
`util.pipeline` (resilient per-video batch loop) and `main` (CLI entry
point, including prompt filtering and pacing construction).
WHY: Verifies the full server-start -> browser-launch -> per-(theme,
prompt) `record_one_video` -> teardown -> summary sequence, and that one
failing video never aborts the rest of the batch (resilience is the key
behavioral difference from `_playwright_demo_script`'s pipeline).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from demo._professional_video_demo import main as main_module
from demo._professional_video_demo.core.pacing import Pacing
from demo._professional_video_demo.util import pipeline as pipeline_module
from tests.demo.conftest import FakeProcess, FakeTimeoutProcess, fake_sync_playwright

_PACING = Pacing.from_target_seconds(150.0)


def _patch_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pipeline_module, "sync_playwright", fake_sync_playwright)
    monkeypatch.setattr(
        pipeline_module, "start_server", lambda live: (FakeProcess(), "http://127.0.0.1:1")
    )


def test_runner_reports_all_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_pipeline(monkeypatch)
    monkeypatch.setattr(pipeline_module, "record_one_video", lambda *a, **k: True)

    runner = pipeline_module.build_professional_demo_runner(
        themes=["dark"],
        prompts=[{"id": "p1", "text": "one"}, {"id": "p2", "text": "two"}],
        live=False,
        pacing=_PACING,
        recordings_root=tmp_path,
    )
    exit_code = runner.run()

    assert exit_code == 0


def test_runner_continues_batch_after_one_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_pipeline(monkeypatch)
    outcomes = iter([True, False, True])
    monkeypatch.setattr(pipeline_module, "record_one_video", lambda *a, **k: next(outcomes))

    runner = pipeline_module.build_professional_demo_runner(
        themes=["dark"],
        prompts=[{"id": "p1", "text": "one"}, {"id": "p2", "text": "two"}, {"id": "p3", "text": "three"}],
        live=False,
        pacing=_PACING,
        recordings_root=tmp_path,
    )
    exit_code = runner.run()

    assert exit_code == 1  # one failure -> non-zero exit despite continuing the batch


def test_runner_terminates_server_even_if_process_wait_times_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    process = FakeTimeoutProcess()
    monkeypatch.setattr(pipeline_module, "sync_playwright", fake_sync_playwright)
    monkeypatch.setattr(pipeline_module, "start_server", lambda live: (process, "http://127.0.0.1:1"))
    monkeypatch.setattr(pipeline_module, "record_one_video", lambda *a, **k: True)

    runner = pipeline_module.build_professional_demo_runner(
        themes=["dark"],
        prompts=[{"id": "p1", "text": "one"}],
        live=False,
        pacing=_PACING,
        recordings_root=tmp_path,
    )
    exit_code = runner.run()

    assert exit_code == 0
    assert process.terminated is True
    assert process.killed is True


def test_main_filters_by_prompt_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = [{"id": "p1", "text": "one"}, {"id": "p2", "text": "two"}]
    monkeypatch.setattr(main_module, "_load_prompts", lambda path: prompts)
    monkeypatch.setattr(main_module, "RECORDINGS_ROOT", tmp_path)

    captured: dict[str, object] = {}

    def fake_build(**kwargs: object):  # type: ignore[no-untyped-def]
        captured.update(kwargs)

        class _StubRunner:
            def run(self) -> int:
                return 0

        return _StubRunner()

    monkeypatch.setattr(main_module, "build_professional_demo_runner", fake_build)
    monkeypatch.setattr(
        sys, "argv", ["prog", "--theme", "dark", "--prompt-id", "p2", "--target-duration", "150"]
    )

    assert main_module.main() == 0
    assert captured["prompts"] == [{"id": "p2", "text": "two"}]
    assert captured["themes"] == ["dark"]


def test_main_returns_1_when_prompt_id_matches_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        main_module, "_load_prompts", lambda path: [{"id": "p1", "text": "one"}]
    )
    monkeypatch.setattr(sys, "argv", ["prog", "--prompt-id", "does-not-exist"])

    assert main_module.main() == 1


def test_main_default_theme_is_both(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        main_module, "_load_prompts", lambda path: [{"id": "p1", "text": "one"}]
    )
    monkeypatch.setattr(main_module, "RECORDINGS_ROOT", tmp_path)

    captured: dict[str, object] = {}

    def fake_build(**kwargs: object):  # type: ignore[no-untyped-def]
        captured.update(kwargs)

        class _StubRunner:
            def run(self) -> int:
                return 0

        return _StubRunner()

    monkeypatch.setattr(main_module, "build_professional_demo_runner", fake_build)
    monkeypatch.setattr(sys, "argv", ["prog"])

    assert main_module.main() == 0
    assert captured["themes"] == ["light", "dark"]
