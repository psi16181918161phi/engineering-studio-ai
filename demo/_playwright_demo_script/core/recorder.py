"""WHAT: Drives one (theme, prompt) screenshot/short-video recording
scenario against the live demo webapp.
WHY: Isolates the Playwright page-interaction sequence from server
bootstrap and CLI orchestration (SOLID SRP).
HOW: Toggles theme if needed, fills the brief, launches the run, and
screenshots each pipeline stage as its `data-state` flips to `"done"`,
then screenshots the final Quality Gate verdict banner.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..exceptions.errors import RecordingError
from .naming import slugify

if TYPE_CHECKING:  # pragma: no cover - typing only
    from playwright.sync_api import Page

STAGE_ORDER: tuple[str, ...] = (
    "research",
    "mechanical",
    "electrical",
    "firmware",
    "simulation",
    "business",
    "challenge",
    "quality_gate",
)


def record_scenario(page: "Page", theme: str, prompt: str, screenshots_dir: Path) -> None:
    """WHAT: Runs one full pipeline cycle end-to-end, screenshotting each
    stage as it completes.

    ARGS:
        page (Page): An already-created Playwright page, navigated to
            the demo webapp's base URL.
        theme (str): `"light"` or `"dark"`.
        prompt (str): The product brief text to submit.
        screenshots_dir (Path): Parent directory; a `<theme>/` subfolder
            is created for this scenario's screenshots.

    RAISES:
        RecordingError: If any required selector never appears (wraps
        the underlying Playwright `TimeoutError`).
    """
    slug = slugify(prompt)
    theme_dir = screenshots_dir / theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    try:
        if theme == "light":
            page.click("#theme-toggle")
            page.wait_for_function("document.documentElement.dataset.theme === 'light'")

        page.screenshot(path=str(theme_dir / f"{slug}_empty.png"))

        page.fill("#brief-input", prompt)
        page.click("#launch-button")
        page.wait_for_selector("#stage-grid", state="visible", timeout=5_000)

        for stage_id in STAGE_ORDER:
            selector = f'.stage-card[data-stage="{stage_id}"] .stage-card__status'
            page.wait_for_selector(f'{selector}[data-state="done"]', timeout=15_000)
            page.screenshot(path=str(theme_dir / f"{slug}_{stage_id}.png"))

        page.wait_for_selector("#gate-banner", state="visible", timeout=5_000)
        page.screenshot(path=str(theme_dir / f"{slug}_final.png"))
    except Exception as exc:  # noqa: BLE001 - normalized into a domain error
        raise RecordingError(f"scenario failed for theme={theme!r}: {exc}") from exc
