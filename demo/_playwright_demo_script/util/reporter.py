"""WHAT: Formats and prints the final batch results summary for
`_playwright_demo_script`.
WHY: Isolates stdout formatting from orchestration (SOLID SRP), matching
`scripts/_sync_submodules/util/reporter.py`'s shape.
HOW: `PlaywrightDemoReporter.report()` prints the recordings-root line;
plain text only (no JSON mode needed — the original script had none).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlaywrightDemoReporter:
    """WHAT: Handles the final "recordings saved" summary line.
    WHY: Keeps `util.pipeline` free of print-formatting concerns.
    """

    def report_saved(self, recordings_root: Path) -> None:
        """WHAT: Prints where recordings were saved.

        ARGS:
            recordings_root (Path): The root recordings directory.
        """
        print(f"Recordings saved under {recordings_root}")
