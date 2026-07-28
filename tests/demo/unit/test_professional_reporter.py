"""WHAT: Unit tests for `demo._professional_video_demo.util.reporter`.
WHY: Isolated stdout-formatting logic — trivially unit tested via capsys.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from demo._professional_video_demo.util.reporter import ProfessionalDemoReporter
from demo._professional_video_demo.core.pacing import Pacing

_PACING = Pacing.from_target_seconds(150.0)


def test_report_pacing_prints_theme_and_prompt_counts(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ProfessionalDemoReporter().report_pacing(_PACING, theme_count=2, prompt_count=3)

    out = capsys.readouterr().out
    assert "x 2 theme(s)" in out
    assert "x 3 prompt(s)" in out


def test_report_no_prompts_matched_prints_to_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ProfessionalDemoReporter().report_no_prompts_matched({"missing-id"})

    err = capsys.readouterr().err
    assert "missing-id" in err


def test_report_summary_prints_pass_fail_lines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    results = {("dark", "p1"): True, ("light", "p2"): False}

    ProfessionalDemoReporter().report_summary(results, tmp_path)

    out = capsys.readouterr().out
    assert "1/2 videos completed successfully" in out
    assert "OK" in out
    assert "FAIL" in out
    assert str(tmp_path) in out
