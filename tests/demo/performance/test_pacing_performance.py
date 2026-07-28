"""WHAT: Performance/bounded-time tests for the mocked demo pipelines.
WHY: `_professional_video_demo`'s batch loop and `Pacing` math must never
accidentally introduce a real (multi-second/minute) `time.sleep()` in the
non-`--live`, fake-browser code path — these tests assert wall-clock
bounds using `FakeBrowser`/mocked `record_scenario`/`record_one_video`
(never a real browser), so a regression that reintroduces a stray real
wait is caught immediately instead of silently making CI slow.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from demo._professional_video_demo.core.pacing import Pacing
from demo._professional_video_demo.util import pipeline as pipeline_module
from tests.demo.conftest import FakeProcess, fake_sync_playwright


def test_pacing_construction_is_effectively_instantaneous() -> None:
    started = time.monotonic()
    for target in (100.0, 150.0, 200.0, 250.0, 300.0, 350.0):
        Pacing.from_target_seconds(target)
    elapsed = time.monotonic() - started

    assert elapsed < 0.5


def test_mocked_batch_of_six_videos_completes_in_under_a_second(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WHAT: A 2-theme x 3-prompt mocked batch (6 videos) must complete
    near-instantly, since `record_one_video` is fully mocked here — this
    bounds the pure orchestration overhead in `util.pipeline`.
    """
    monkeypatch.setattr(pipeline_module, "sync_playwright", fake_sync_playwright)
    monkeypatch.setattr(
        pipeline_module, "start_server", lambda live: (FakeProcess(), "http://127.0.0.1:1")
    )
    monkeypatch.setattr(pipeline_module, "record_one_video", lambda *a, **k: True)

    pacing = Pacing.from_target_seconds(150.0)
    runner = pipeline_module.build_professional_demo_runner(
        themes=["light", "dark"],
        prompts=[{"id": f"p{i}", "text": f"prompt {i}"} for i in range(3)],
        live=False,
        pacing=pacing,
        recordings_root=tmp_path,
    )

    started = time.monotonic()
    exit_code = runner.run()
    elapsed = time.monotonic() - started

    assert exit_code == 0
    assert elapsed < 1.0
