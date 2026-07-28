"""WHAT: Drives one full pipeline cycle end-to-end in a given theme,
narrated by the burned-in overlay from `core.overlay`.
WHY: This is the single function responsible for the "entire scenario"
— brief entry through the Quality Gate verdict — separate from
per-video setup/teardown (`core.recorder`) and pacing math
(`core.pacing`).
HOW: Toggles theme first (if needed) and waits for the backend health
check BEFORE the overlay is injected — this ordering matters even
though every overlay element is `pointer-events: none`, since it
guarantees the real `#theme-toggle` button is never covered by
anything while Playwright clicks it. Only then does it show a branded
intro card, type the brief, launch the run, walk `STAGE_ORDER` waiting
for each stage's real `data-state` to flip to `"done"` before holding
its caption, and finally show the Quality Gate verdict plus a branded
outro card.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .overlay import (
    clear_caption,
    inject_overlay,
    set_caption,
    set_progress,
    set_topbar,
    show_intro_card,
    show_outro_card,
)
from .pacing import STAGE_CAPTIONS, STAGE_ORDER, Pacing

if TYPE_CHECKING:  # pragma: no cover - typing only
    from playwright.sync_api import Page


def type_brief(page: "Page", prompt_text: str, hold_seconds: float) -> None:
    """WHAT: Simulates realistic human typing of the product brief,
    spread across roughly `hold_seconds`.
    """
    delay_ms = max(15.0, min(80.0, (hold_seconds * 1000.0) / max(1, len(prompt_text))))
    set_caption(
        page,
        "Product Brief",
        "A single natural-language brief is all the pipeline needs to start.",
    )
    field = page.locator("#brief-input")
    field.click()
    field.fill("")
    field.press_sequentially(prompt_text, delay=delay_ms)


def record_scenario(page: "Page", theme: str, prompt_text: str, pacing: Pacing) -> None:
    """WHAT: Runs the full narrated walkthrough on an already-navigated
    page, ending with the Quality Gate verdict and outro card.

    ARGS:
        page (Page): An already-created Playwright page, navigated to
            the demo webapp's base URL.
        theme (str): `"light"` or `"dark"`.
        prompt_text (str): The product brief to type and submit.
        pacing (Pacing): Hold durations for each beat.
    """
    if theme == "light":
        page.click("#theme-toggle")
        page.wait_for_function("document.documentElement.dataset.theme === 'light'")
    page.wait_for_selector('#server-status[data-state="ok"]', timeout=10_000)
    inject_overlay(page)

    set_topbar(page, "Engineering Studio AI", "Preparing walkthrough…")
    show_intro_card(page, theme, prompt_text, pacing.intro_seconds)

    type_brief(page, prompt_text, pacing.typing_seconds)
    clear_caption(page)

    page.click("#launch-button")
    page.wait_for_selector("#stage-grid", state="visible", timeout=10_000)
    set_topbar(page, "Engineering Studio AI", "Run launched — dispatching stages…")
    set_caption(
        page,
        "Orchestrator",
        "Decomposes the brief and dispatches each discipline in the correct order.",
    )
    page.wait_for_timeout(int(pacing.launch_seconds * 1000))

    total = len(STAGE_ORDER)
    for index, stage_id in enumerate(STAGE_ORDER, start=1):
        heading, body = STAGE_CAPTIONS[stage_id]
        set_topbar(page, "Engineering Studio AI", f"Stage {index} of {total}: {heading}")
        selector = f'.stage-card[data-stage="{stage_id}"] .stage-card__status'
        page.wait_for_selector(f'{selector}[data-state="done"]', timeout=30_000)
        set_caption(page, heading, body)
        set_progress(page, (index / total) * 100.0)
        page.wait_for_timeout(int(pacing.per_stage_seconds * 1000))

    page.wait_for_selector("#gate-banner", state="visible", timeout=10_000)
    verdict_text = page.inner_text("#gate-banner").strip()
    set_topbar(page, "Engineering Studio AI", "Run complete")
    set_caption(page, "Quality Gate Verdict", verdict_text)
    page.wait_for_timeout(int(pacing.gate_seconds * 1000))

    show_outro_card(page, verdict_text, pacing.outro_seconds)
