"""WHAT: CLI entry point for `_playwright_demo_script`.
WHY: SCOPE §3 (def main() + __name__ guard) and SOLID SRP — argument
parsing only, orchestration delegated to `util.pipeline`.
HOW: Parses `--theme`/`--live`; builds and runs a `PlaywrightDemoRunner`.

Usage:
    python -m demo._playwright_demo_script [--theme light|dark|both] [--live]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .util.pipeline import build_playwright_demo_runner

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDINGS_ROOT = REPO_ROOT / "demo" / "recordings"

DEMO_PROMPTS = [
    "Create a Python script that automates the backup of important files to a cloud storage service.",
    "Develop a simple web application that allows users to track their daily habits and visualize their progress over time.",
    "Write a command-line tool that analyzes text files and generates a summary report of word frequency and sentiment.",
]


def main() -> int:
    """WHAT: Parses CLI args and runs the recording batch.

    RETURNS:
        int: Process exit code (`0` on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real Fireworks pipeline (Mode A) instead of the default mocked Mode B.",
    )
    args = parser.parse_args()
    themes = ["light", "dark"] if args.theme == "both" else [args.theme]

    runner = build_playwright_demo_runner(
        themes=themes,
        prompts=DEMO_PROMPTS,
        live=args.live,
        recordings_root=RECORDINGS_ROOT,
    )
    return runner.run()


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
