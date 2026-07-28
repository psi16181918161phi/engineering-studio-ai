"""WHAT: Records one full-cycle, captioned walkthrough video for a
single (theme, prompt) combination and renames the resulting `.webm` to
a stable, descriptive filename.
WHY: Returns a bool (success/failure) rather than raising, so the batch
loop in `util.pipeline` can attempt every (theme, prompt) combination
even if one recording hits a transient error (e.g. a selector timeout)
— one bad video must never silently abort the rest of the batch. The
`.webm` is still renamed/kept on a failure, since a partial recording
is still useful for debugging.
HOW: Opens a fresh browser context/page, runs `core.scenario.record_scenario`,
screenshots the final frame, then renames the raw Playwright video file.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from demo._playwright_demo_script.core.naming import slugify

from .pacing import Pacing
from .scenario import record_scenario

if TYPE_CHECKING:  # pragma: no cover - typing only
    from playwright.sync_api import Browser

VIEWPORT = {"width": 1920, "height": 1080}


def record_one_video(
    browser: "Browser",
    base_url: str,
    theme: str,
    prompt: dict[str, str],
    pacing: Pacing,
    video_dir: Path,
    screenshots_dir: Path,
) -> bool:
    """WHAT: Records one professional walkthrough video.

    ARGS:
        browser (Browser): An already-launched Playwright browser.
        base_url (str): Base URL of the running demo webapp.
        theme (str): `"light"` or `"dark"`.
        prompt (dict[str, str]): Has `id` and `text` keys.
        pacing (Pacing): Hold durations for each beat.
        video_dir (Path): Directory Playwright writes the raw `.webm` to.
        screenshots_dir (Path): Directory for the final-frame screenshot.

    RETURNS:
        bool: `True` if the scenario completed and the video was saved;
        `False` if an exception was caught (already logged to stderr).
    """
    context = browser.new_context(
        record_video_dir=str(video_dir),
        record_video_size=VIEWPORT,
        viewport=VIEWPORT,
    )
    page = context.new_page()
    started = time.monotonic()
    success = True
    video = None
    try:
        page.goto(base_url)
        record_scenario(page, theme, prompt["text"], pacing)
        slug = slugify(prompt["text"])
        page.screenshot(path=str(screenshots_dir / f"{slug}_{theme}_final.png"))
    except Exception as exc:  # noqa: BLE001 - reported below, batch must continue
        success = False
        print(f"[{theme}] {prompt['id']}: FAILED - {exc}", file=sys.stderr)
    finally:
        video = page.video
        page.close()
        context.close()  # flushes the .webm video file to disk

    elapsed = time.monotonic() - started
    final_path = video_dir / f"{prompt['id']}_{theme}.webm"
    if video is not None:
        raw_path = Path(video.path())
        if raw_path.exists():
            if final_path.exists():
                final_path.unlink()
            raw_path.rename(final_path)

    if not success:
        return False

    in_band = 115.0 <= elapsed <= 320.0
    flag = "OK" if in_band else "WARNING: outside the 2-5 minute band"
    print(
        f"[{theme}] {prompt['id']}: recorded {elapsed:.1f}s "
        f"({elapsed / 60:.2f} min) -> {final_path.name} ({flag})"
    )
    return True
