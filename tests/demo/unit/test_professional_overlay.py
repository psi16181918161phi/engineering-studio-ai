"""WHAT: Unit tests for `demo._professional_video_demo.core.overlay`.
WHY: All `page.evaluate()` calls are wrapped in small named functions —
each is trivially testable against a `FakePage` without a real browser.
HOW: Asserts the right `window.__demoXxx` hook name and arguments were
passed to `page.evaluate(...)`, and that `truncate()`'s ellipsis logic
is correct at the boundary.
"""

from __future__ import annotations

from demo._professional_video_demo.core.overlay import (
    clear_caption,
    hide_card,
    inject_overlay,
    load_overlay_js,
    set_caption,
    set_progress,
    set_topbar,
    show_card,
    show_intro_card,
    show_outro_card,
    truncate,
)
from tests.demo.conftest import FakePage


def test_load_overlay_js_reads_asset_file() -> None:
    js = load_overlay_js()
    assert "__demoOverlayReady" in js


def test_inject_overlay_evaluates_the_asset_js() -> None:
    page = FakePage()
    inject_overlay(page)
    assert page.evaluated[0][0] == load_overlay_js()


def test_set_topbar_calls_hook_with_args() -> None:
    page = FakePage()
    set_topbar(page, "Title", "Stage text")
    script, arg = page.evaluated[-1]
    assert "__demoSetTopbar" in script
    assert arg == ["Title", "Stage text"]


def test_set_progress_calls_hook_with_pct() -> None:
    page = FakePage()
    set_progress(page, 42.5)
    script, arg = page.evaluated[-1]
    assert "__demoSetProgress" in script
    assert arg == 42.5


def test_truncate_short_text_unchanged() -> None:
    assert truncate("short text", limit=240) == "short text"


def test_truncate_collapses_whitespace() -> None:
    assert truncate("a   b\nc", limit=240) == "a b c"


def test_truncate_long_text_gets_ellipsis() -> None:
    text = "word " * 100
    result = truncate(text, limit=20)
    assert len(result) == 20
    assert result.endswith("…")


def test_set_caption_calls_hook_with_truncated_body() -> None:
    page = FakePage()
    set_caption(page, "Heading", "body")
    script, arg = page.evaluated[-1]
    assert "__demoSetCaption" in script
    assert arg == ["Heading", "body"]


def test_clear_caption_calls_hook() -> None:
    page = FakePage()
    clear_caption(page)
    assert "__demoClearCaption" in page.evaluated[-1][0]


def test_show_card_and_hide_card_call_hooks() -> None:
    page = FakePage()
    show_card(page, "T", "S", "E")
    script, arg = page.evaluated[-1]
    assert "__demoShowCard" in script
    assert arg == ["T", "S", "E"]

    hide_card(page)
    assert "__demoHideCard" in page.evaluated[-1][0]


def test_show_intro_card_holds_then_hides(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    page = FakePage()
    show_intro_card(page, "dark", "Build a thing", hold_seconds=1.0)

    assert page.timeouts_ms == [1000]
    assert any("__demoShowCard" in s for s, _ in page.evaluated)
    assert any("__demoHideCard" in s for s, _ in page.evaluated)


def test_show_outro_card_holds_with_verdict_text() -> None:
    page = FakePage()
    show_outro_card(page, "PASS: All quality checks succeeded.", hold_seconds=2.0)

    assert page.timeouts_ms == [2000]
    assert any("__demoShowCard" in s for s, _ in page.evaluated)


def test_show_outro_card_falls_back_when_verdict_empty() -> None:
    page = FakePage()
    show_outro_card(page, "", hold_seconds=1.0)

    _, arg = [e for e in page.evaluated if "__demoShowCard" in e[0]][-1]
    assert "Every stage ran end-to-end" in arg[2]
