"""WHAT: Unit tests for `demo._professional_video_demo.core.scenario`.
WHY: Verifies the full narrated walkthrough sequence (theme toggle,
brief typing, per-stage caption/progress updates, verdict capture, outro)
against a `FakePage` double.
"""

from __future__ import annotations

from demo._professional_video_demo.core.pacing import STAGE_ORDER, Pacing
from demo._professional_video_demo.core.scenario import record_scenario, type_brief
from tests.demo.conftest import FakePage

_PACING = Pacing.from_target_seconds(150.0)


def test_type_brief_fills_and_records_delay() -> None:
    page = FakePage()
    type_brief(page, "Build a thing", hold_seconds=2.0)

    assert page.fills[-1] == ("#brief-input", "Build a thing")
    assert page.typed_delays[-1] is not None


def test_record_scenario_dark_theme_runs_all_stages() -> None:
    page = FakePage(gate_text="PASS: All quality checks succeeded.")
    record_scenario(page, "dark", "Build a thing", _PACING)

    assert "#theme-toggle" not in page.clicks
    assert page.clicks.count("#launch-button") == 1
    # one set_progress evaluate call per stage (exact script match, since the
    # injected overlay.js source text also *mentions* __demoSetProgress)
    progress_calls = [
        a for s, a in page.evaluated if s == "(p) => window.__demoSetProgress(p)"
    ]
    assert len(progress_calls) == len(STAGE_ORDER)
    assert progress_calls[-1] == 100.0


def test_record_scenario_light_theme_toggles() -> None:
    page = FakePage()
    record_scenario(page, "light", "Build a thing", _PACING)

    assert "#theme-toggle" in page.clicks
    assert page.theme == "light"


def test_record_scenario_captures_verdict_text() -> None:
    page = FakePage(gate_text="FAIL: something broke")
    record_scenario(page, "dark", "Build a thing", _PACING)

    caption_calls = [
        a
        for s, a in page.evaluated
        if s == "([h, b]) => window.__demoSetCaption(h, b)"
    ]
    assert any(a[0] == "Quality Gate Verdict" for a in caption_calls)
