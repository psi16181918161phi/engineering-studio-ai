"""WHAT: Orchestrates the full `_playwright_demo_script` run: start
server -> for each (theme, prompt) open a fresh browser context/page,
record the scenario, save the video -> tear down.
WHY: Separates orchestration/CLI-argument handling from the individual
per-scenario recording mechanics in `core.recorder` (SOLID SRP + OCP,
matches `scripts/_sync_submodules/util/pipeline.py`'s shape).
HOW: `build_playwright_demo_runner()` constructs a `PlaywrightDemoRunner`
from parsed CLI args; `.run()` executes the full pipeline and returns a
process exit code.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import sync_playwright

from ..core.recorder import record_scenario
from ..core.server import start_server
from .reporter import PlaywrightDemoReporter

VIEWPORT = {"width": 1366, "height": 768}


@dataclass
class PlaywrightDemoRunner:
    """WHAT: Holds run configuration and orchestrates the recording batch.
    WHY: Encapsulates all pipeline state in one place, easy to test by
    constructing directly with fakes/mocks.
    HOW: `run()` starts the server, iterates themes x prompts, and tears
    down the server process in a `finally` block.

    ATTRS:
        themes (list[str]): Themes to record (`"light"`/`"dark"`).
        prompts (list[str]): Prompt texts to record.
        live (bool): Whether to use the real (non-mocked) pipeline.
        recordings_root (Path): Root output directory.
    """

    themes: list[str]
    prompts: list[str]
    live: bool
    recordings_root: Path
    _reporter: PlaywrightDemoReporter = field(default_factory=PlaywrightDemoReporter)

    def run(self) -> int:
        """WHAT: Executes the full record batch.

        RETURNS:
            int: `0` on success. Raises rather than swallowing errors —
            this script has no partial-failure recovery, unlike the
            professional video demo's batch loop.
        """
        process, base_url = start_server(live=self.live)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                for theme in self.themes:
                    video_dir = self.recordings_root / "video" / theme
                    video_dir.mkdir(parents=True, exist_ok=True)
                    for prompt in self.prompts:
                        context = browser.new_context(
                            record_video_dir=str(video_dir),
                            record_video_size=VIEWPORT,
                            viewport=VIEWPORT,
                        )
                        page = context.new_page()
                        page.goto(base_url)
                        record_scenario(
                            page, theme, prompt, self.recordings_root / "screenshots"
                        )
                        page.close()
                        context.close()  # flushes the .webm video file
                browser.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        self._reporter.report_saved(self.recordings_root)
        return 0


def build_playwright_demo_runner(
    themes: list[str],
    prompts: list[str],
    live: bool,
    recordings_root: Path,
) -> PlaywrightDemoRunner:
    """WHAT: Factory constructing a `PlaywrightDemoRunner` from parsed
    CLI arguments.

    ARGS:
        themes (list[str]): Themes to record.
        prompts (list[str]): Prompt texts to record.
        live (bool): Whether to use the real (non-mocked) pipeline.
        recordings_root (Path): Root output directory.

    RETURNS:
        PlaywrightDemoRunner: Ready to `.run()`.
    """
    return PlaywrightDemoRunner(
        themes=themes, prompts=prompts, live=live, recordings_root=recordings_root
    )
