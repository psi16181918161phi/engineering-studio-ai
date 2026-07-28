"""WHAT: Unit tests for `demo._playwright_demo_script.core.recorder`.
WHY: Verifies the full stage-by-stage recording sequence and that any
underlying failure is normalized into `RecordingError`.
HOW: Drives a `FakePage` through `record_scenario` for both themes, and
forces an exception to confirm the `RecordingError` wrap-and-raise path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from demo._playwright_demo_script.core.recorder import STAGE_ORDER, record_scenario
from demo._playwright_demo_script.exceptions.errors import RecordingError
from tests.demo.conftest import FakePage


def test_record_scenario_dark_theme(tmp_path: Path) -> None:
    page = FakePage()
    record_scenario(page, "dark", "Build a thing", tmp_path)

    assert "#theme-toggle" not in page.clicks
    assert page.clicks.count("#launch-button") == 1
    # 1 empty + 8 stage + 1 final screenshot
    assert len(page.screenshots) == 1 + len(STAGE_ORDER) + 1
    assert (tmp_path / "dark").is_dir()


def test_record_scenario_light_theme_toggles(tmp_path: Path) -> None:
    page = FakePage()
    record_scenario(page, "light", "Build a thing", tmp_path)

    assert "#theme-toggle" in page.clicks
    assert page.theme == "light"


def test_record_scenario_wraps_failures_as_recording_error(tmp_path: Path) -> None:
    page = FakePage()

    def boom(selector: str, state: str | None = None, timeout: float | None = None) -> None:
        raise TimeoutError("selector never appeared")

    page.wait_for_selector = boom  # type: ignore[method-assign]

    with pytest.raises(RecordingError):
        record_scenario(page, "dark", "Build a thing", tmp_path)
