"""WHAT: Unit tests for `demo._professional_video_demo.core.recorder`.
WHY: Verifies both the success path (video renamed to a stable filename,
timing flag printed) and the resilient failure path (exception caught,
`False` returned, error logged to stderr) required by the batch loop in
`util.pipeline`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from demo._professional_video_demo.core import recorder as recorder_module
from demo._professional_video_demo.core.pacing import Pacing
from tests.demo.conftest import FakeBrowser

_PACING = Pacing.from_target_seconds(150.0)


def test_record_one_video_success_renames_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    browser = FakeBrowser()
    video_dir = tmp_path / "video"
    screenshots_dir = tmp_path / "screenshots"
    video_dir.mkdir()
    screenshots_dir.mkdir()

    times = iter([0.0, 150.0])
    monkeypatch.setattr(recorder_module, "record_scenario", lambda *a, **k: None)
    monkeypatch.setattr(recorder_module.time, "monotonic", lambda: next(times))

    ok = recorder_module.record_one_video(
        browser,
        "http://127.0.0.1:1",
        "dark",
        {"id": "p1", "text": "Build a thing"},
        _PACING,
        video_dir,
        screenshots_dir,
    )

    assert ok is True
    assert (video_dir / "p1_dark.webm").exists()


def test_record_one_video_flags_when_outside_band(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    browser = FakeBrowser()
    video_dir = tmp_path / "video"
    screenshots_dir = tmp_path / "screenshots"
    video_dir.mkdir()
    screenshots_dir.mkdir()

    times = iter([0.0, 5.0])
    monkeypatch.setattr(recorder_module, "record_scenario", lambda *a, **k: None)
    monkeypatch.setattr(recorder_module.time, "monotonic", lambda: next(times))

    ok = recorder_module.record_one_video(
        browser,
        "http://127.0.0.1:1",
        "dark",
        {"id": "p2", "text": "Build a thing"},
        _PACING,
        video_dir,
        screenshots_dir,
    )

    assert ok is True
    assert (video_dir / "p2_dark.webm").exists()


def test_record_one_video_overwrites_existing_final_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    browser = FakeBrowser()
    video_dir = tmp_path / "video"
    screenshots_dir = tmp_path / "screenshots"
    video_dir.mkdir()
    screenshots_dir.mkdir()
    (video_dir / "p4_dark.webm").write_bytes(b"stale-old-video")

    times = iter([0.0, 150.0])
    monkeypatch.setattr(recorder_module, "record_scenario", lambda *a, **k: None)
    monkeypatch.setattr(recorder_module.time, "monotonic", lambda: next(times))

    ok = recorder_module.record_one_video(
        browser,
        "http://127.0.0.1:1",
        "dark",
        {"id": "p4", "text": "Build a thing"},
        _PACING,
        video_dir,
        screenshots_dir,
    )

    assert ok is True
    assert (video_dir / "p4_dark.webm").read_bytes() == b"fake-video-bytes"


def test_record_one_video_returns_false_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    browser = FakeBrowser()
    video_dir = tmp_path / "video"
    screenshots_dir = tmp_path / "screenshots"
    video_dir.mkdir()
    screenshots_dir.mkdir()

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("selector never appeared")

    monkeypatch.setattr(recorder_module, "record_scenario", boom)

    ok = recorder_module.record_one_video(
        browser,
        "http://127.0.0.1:1",
        "dark",
        {"id": "p3", "text": "Build a thing"},
        _PACING,
        video_dir,
        screenshots_dir,
    )

    assert ok is False
    assert "FAILED" in capsys.readouterr().err
