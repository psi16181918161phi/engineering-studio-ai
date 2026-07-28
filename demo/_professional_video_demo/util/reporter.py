"""WHAT: Formats and prints per-video and final batch results for
`_professional_video_demo`.
WHY: Isolates stdout formatting from orchestration (SOLID SRP), matching
`scripts/_sync_submodules/util/reporter.py`'s shape.
HOW: `ProfessionalDemoReporter.report_pacing()` / `.report_summary()`
print the pre-batch pacing line and the final PASS/FAIL summary table.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from ..core.pacing import Pacing


@dataclass
class ProfessionalDemoReporter:
    """WHAT: Handles all pre/post-batch stdout reporting.
    WHY: Keeps `util.pipeline` free of print-formatting concerns.
    """

    def report_pacing(self, pacing: Pacing, theme_count: int, prompt_count: int) -> None:
        """WHAT: Prints the computed pacing before the batch starts."""
        print(
            f"Pacing: ~{pacing.total_seconds:.0f}s ({pacing.total_seconds / 60:.1f} min) "
            f"per video x {theme_count} theme(s) x {prompt_count} prompt(s)"
        )

    def report_no_prompts_matched(self, wanted: set[str]) -> None:
        """WHAT: Prints an error when `--prompt-id` matched nothing."""
        print(f"No prompts matched --prompt-id {sorted(wanted)}", file=sys.stderr)

    def report_summary(
        self, results: dict[tuple[str, str], bool], recordings_root: Path
    ) -> None:
        """WHAT: Prints the final PASS/FAIL summary table.

        ARGS:
            results (dict[tuple[str, str], bool]): One (theme, prompt_id)
                -> success bool per attempted video.
            recordings_root (Path): Root recordings directory.
        """
        succeeded = sum(1 for ok in results.values() if ok)
        print(f"\n{succeeded}/{len(results)} videos completed successfully:")
        for (theme, prompt_id), ok in results.items():
            print(f"  [{'OK  ' if ok else 'FAIL'}] {theme}/{prompt_id}")
        print(f"Professional demo videos saved under {recordings_root}")
