"""WHAT: Orchestrates the full `_professional_video_demo` batch: start
server -> launch one shared browser -> for each (theme, prompt) record
one video via `core.recorder.record_one_video` -> teardown -> print
summary and return an exit code.
WHY: Separates batch orchestration/CLI-argument handling from the
individual per-video recording mechanics (SOLID SRP + OCP, matches
`scripts/_sync_submodules/util/pipeline.py`'s shape). The batch loop is
resilient: `record_one_video()` never raises, so one bad recording never
costs the rest of the batch.
HOW: `build_professional_demo_runner()` constructs a
`ProfessionalDemoRunner` from parsed CLI args; `.run()` executes the
full pipeline and returns a process exit code (`0` only if every video
in the batch succeeded).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import sync_playwright

from demo._playwright_demo_script.core.server import start_server

from ..core.pacing import Pacing
from ..core.recorder import record_one_video
from .reporter import ProfessionalDemoReporter


@dataclass
class ProfessionalDemoRunner:
    """WHAT: Holds run configuration and orchestrates the video batch.
    WHY: Encapsulates all pipeline state in one place, easy to test by
    constructing directly with fakes/mocks.
    HOW: `run()` starts the server, launches one shared browser, iterates
    themes x prompts (always attempting every combination), tears down,
    and prints a final summary.

    ATTRS:
        themes (list[str]): Themes to record.
        prompts (list[dict[str, str]]): Prompts (`id`/`text`) to record.
        live (bool): Whether to use the real (non-mocked) pipeline.
        pacing (Pacing): Hold durations for each beat.
        recordings_root (Path): Root output directory.
        headed (bool): If True, shows the browser window (debug only).
    """

    themes: list[str]
    prompts: list[dict[str, str]]
    live: bool
    pacing: Pacing
    recordings_root: Path
    headed: bool = False
    _reporter: ProfessionalDemoReporter = field(default_factory=ProfessionalDemoReporter)

    def run(self) -> int:
        """WHAT: Executes the full record batch.

        RETURNS:
            int: `0` if every (theme, prompt) combination succeeded,
            `1` if any failed.
        """
        self._reporter.report_pacing(self.pacing, len(self.themes), len(self.prompts))

        results: dict[tuple[str, str], bool] = {}
        process, base_url = start_server(live=self.live)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=not self.headed)
                for theme in self.themes:
                    video_dir = self.recordings_root / "video" / theme
                    screenshots_dir = self.recordings_root / "screenshots" / theme
                    video_dir.mkdir(parents=True, exist_ok=True)
                    screenshots_dir.mkdir(parents=True, exist_ok=True)
                    for prompt in self.prompts:
                        ok = record_one_video(
                            browser,
                            base_url,
                            theme,
                            prompt,
                            self.pacing,
                            video_dir,
                            screenshots_dir,
                        )
                        results[(theme, prompt["id"])] = ok
                browser.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        self._reporter.report_summary(results, self.recordings_root)
        succeeded = sum(1 for ok in results.values() if ok)
        return 0 if succeeded == len(results) else 1


def build_professional_demo_runner(
    themes: list[str],
    prompts: list[dict[str, str]],
    live: bool,
    pacing: Pacing,
    recordings_root: Path,
    headed: bool = False,
) -> ProfessionalDemoRunner:
    """WHAT: Factory constructing a `ProfessionalDemoRunner` from parsed
    CLI arguments.

    RETURNS:
        ProfessionalDemoRunner: Ready to `.run()`.
    """
    return ProfessionalDemoRunner(
        themes=themes,
        prompts=prompts,
        live=live,
        pacing=pacing,
        recordings_root=recordings_root,
        headed=headed,
    )
