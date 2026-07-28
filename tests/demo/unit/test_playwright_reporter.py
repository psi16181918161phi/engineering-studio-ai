"""WHAT: Unit tests for `demo._playwright_demo_script.util.reporter`.
WHY: Isolated stdout-formatting logic — trivially unit tested via capsys.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from demo._playwright_demo_script.util.reporter import PlaywrightDemoReporter


def test_report_saved_prints_recordings_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    PlaywrightDemoReporter().report_saved(tmp_path)

    out = capsys.readouterr().out
    assert f"Recordings saved under {tmp_path}" in out
