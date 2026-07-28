"""WHAT: CLI entry point for `_professional_video_demo`.
WHY: SCOPE §3 (def main() + __name__ guard) and SOLID SRP — argument
parsing and prompt loading only, orchestration delegated to
`util.pipeline`.
HOW: Parses the original script's flags 1:1; builds and runs a
`ProfessionalDemoRunner`.

Usage:
    python -m demo._professional_video_demo [--theme light|dark|both]
        [--target-duration SECONDS] [--prompt-id ID ...] [--live] [--headed]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from demo.run_demo_sequence import _load_prompts

from .core.pacing import Pacing
from .util.pipeline import build_professional_demo_runner
from .util.reporter import ProfessionalDemoReporter

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDINGS_ROOT = REPO_ROOT / "demo" / "recordings" / "professional"
DEFAULT_PROMPTS_FILE = REPO_ROOT / "demo" / "demo_prompts.json"


def main() -> int:
    """WHAT: Parses CLI args and runs the professional video batch.

    RETURNS:
        int: Process exit code (`0` only if every video succeeded).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real Fireworks-backed pipeline (Mode A) instead of the "
        "default deterministic mocked pipeline (Mode B, requires no API key).",
    )
    parser.add_argument(
        "--target-duration",
        type=float,
        default=200.0,
        help="Target seconds per video, clamped to the mandatory 120-300s "
        "(2-5 minute) band (default: 200).",
    )
    parser.add_argument(
        "--prompts-file",
        type=Path,
        default=DEFAULT_PROMPTS_FILE,
        help=f"Path to the demo prompts JSON file (default: {DEFAULT_PROMPTS_FILE.relative_to(REPO_ROOT)}).",
    )
    parser.add_argument(
        "--prompt-id",
        action="append",
        default=None,
        help="Limit to specific prompt id(s) from demo_prompts.json (repeatable); "
        "default: all confirmed prompts.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Local debugging escape hatch only — shows the browser window "
        "instead of running headless. Never use this for batch generation.",
    )
    args = parser.parse_args()

    reporter = ProfessionalDemoReporter()
    prompts = _load_prompts(args.prompts_file)
    if args.prompt_id:
        wanted = set(args.prompt_id)
        prompts = [p for p in prompts if p["id"] in wanted]
        if not prompts:
            reporter.report_no_prompts_matched(wanted)
            return 1

    themes = ["light", "dark"] if args.theme == "both" else [args.theme]
    pacing = Pacing.from_target_seconds(args.target_duration)

    runner = build_professional_demo_runner(
        themes=themes,
        prompts=prompts,
        live=args.live,
        pacing=pacing,
        recordings_root=RECORDINGS_ROOT,
        headed=args.headed,
    )
    return runner.run()


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
