"""WHAT: Unit tests for `engineering_studio.testing.fake_pipeline`.
WHY: This module is what makes CI-safe (Mode B) Playwright end-to-end
runs possible against a real live server; a regression here (wrong
STAGE_ORDER, missing on_event calls, malformed artifact) would silently
break every e2e test and recording.
HOW: Calls `fake_run_pipeline` directly (no threads, no HTTP), asserting
event order and written artifact content.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio.agents.orchestrator import STAGE_ORDER
from engineering_studio.testing import fake_pipeline
from engineering_studio.testing.fake_pipeline import fake_run_pipeline


@pytest.fixture(autouse=True)
def _no_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """WHAT: Removes the visual-recording pause for fast unit tests.

    WHY: `_STAGE_DELAY_SECONDS` exists to make stage transitions visible
    in a screen recording, not to slow down this module's own test suite.
    """
    monkeypatch.setattr(fake_pipeline, "_STAGE_DELAY_SECONDS", 0.0)


def test_fake_run_pipeline_emits_running_then_done_for_every_stage(tmp_path: Path) -> None:
    events: list[tuple[str, str, str | None]] = []
    fake_run_pipeline(
        "Build a thing",
        tmp_path,
        on_event=lambda stage, status, detail: events.append((stage, status, detail)),
    )

    assert [e[0] for e in events] == [stage for stage in STAGE_ORDER for _ in (0, 1)]
    for i, stage in enumerate(STAGE_ORDER):
        assert events[2 * i] == (stage, "running", None)
        assert events[2 * i + 1][0] == stage
        assert events[2 * i + 1][1] == "done"
        assert events[2 * i + 1][2] is not None


def test_fake_run_pipeline_writes_readable_artifact_per_stage(tmp_path: Path) -> None:
    outputs = fake_run_pipeline("Design a widget", tmp_path)

    assert set(outputs.keys()) == set(STAGE_ORDER)
    for stage, path in outputs.items():
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "Design a widget" in text
        assert stage in text


def test_fake_run_pipeline_works_without_on_event(tmp_path: Path) -> None:
    outputs = fake_run_pipeline("No observer brief", tmp_path, on_event=None)
    assert len(outputs) == len(STAGE_ORDER)
