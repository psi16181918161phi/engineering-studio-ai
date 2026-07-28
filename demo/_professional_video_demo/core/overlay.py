"""WHAT: Browser-side overlay control functions for the professional
video demo (topbar/progress-bar/caption/title-card).
WHY: Isolates all `page.evaluate()` calls behind small, named functions
so `core.scenario` reads like a narrative rather than raw JS strings
(SOLID SRP: this module owns "how to talk to the injected overlay", the
sibling `assets/overlay.js` owns "what the overlay renders").
HOW: `inject_overlay()` reads `assets/overlay.js` once at import time and
evaluates it into the page; every other function calls one of the
`window.__demoXxx` hooks that script installs.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from playwright.sync_api import Page

_OVERLAY_JS_PATH = Path(__file__).resolve().parent.parent / "assets" / "overlay.js"


def load_overlay_js() -> str:
    """WHAT: Reads the overlay's browser-side JS source from disk.

    RETURNS:
        str: The full contents of `assets/overlay.js`.
    """
    return _OVERLAY_JS_PATH.read_text(encoding="utf-8")


def inject_overlay(page: "Page") -> None:
    """WHAT: Injects the caption/topbar/progress-bar/title-card overlay
    into the current page.
    """
    page.evaluate(load_overlay_js())


def set_topbar(page: "Page", title: str, stage_text: str) -> None:
    page.evaluate("([t, s]) => window.__demoSetTopbar(t, s)", [title, stage_text])


def set_progress(page: "Page", pct: float) -> None:
    page.evaluate("(p) => window.__demoSetProgress(p)", pct)


def truncate(text: str, limit: int = 240) -> str:
    """WHAT: Caps caption body text length so the lower-third never
    overflows the recorded viewport.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def set_caption(page: "Page", heading: str, body: str) -> None:
    page.evaluate("([h, b]) => window.__demoSetCaption(h, b)", [heading, truncate(body)])


def clear_caption(page: "Page") -> None:
    page.evaluate("() => window.__demoClearCaption()")


def show_card(page: "Page", title: str, subtitle: str, extra: str) -> None:
    page.evaluate("([t, s, e]) => window.__demoShowCard(t, s, e)", [title, subtitle, extra])


def hide_card(page: "Page") -> None:
    page.evaluate("() => window.__demoHideCard()")


def show_intro_card(page: "Page", theme: str, prompt_text: str, hold_seconds: float) -> None:
    """WHAT: Full-screen branded intro card, held for `hold_seconds`."""
    from .pacing import DISCLAIMER

    show_card(
        page,
        "Engineering Studio AI",
        f"{theme.title()} Mode — Full Pipeline Walkthrough",
        f'Brief: "{prompt_text}"  |  {DISCLAIMER}',
    )
    page.wait_for_timeout(int(hold_seconds * 1000))
    hide_card(page)


def show_outro_card(page: "Page", verdict_text: str, hold_seconds: float) -> None:
    """WHAT: Full-screen branded outro card summarizing the run, held for
    `hold_seconds` before the recording ends.
    """
    show_card(
        page,
        "Run Complete",
        "Research -> Parallel Specialists -> Challenge Division -> Quality Gate",
        truncate(verdict_text, 280)
        or "Every stage ran end-to-end under a single certifying pipeline.",
    )
    page.wait_for_timeout(int(hold_seconds * 1000))
