"""WHAT: Command-line entry point: `python -m engineering_studio.cli "<brief>"`.
WHY: Fastest path to a working hackathon demo — no web server required to
show the multi-agent pipeline producing a real artifact tree.
HOW: Loads .env, runs the pipeline, prints where each artifact landed.

NOTE: This module previously lived as a sibling file
`engineering_studio/cli.py` alongside this now-populated `cli/` package.
That was a latent bug: once both `cli.py` and `cli/__init__.py` existed,
Python's import system resolved `engineering_studio.cli` to this package
unconditionally, silently shadowing the sibling file and breaking the
documented `python -m engineering_studio.cli` invocation (it raised
"'engineering_studio.cli' is a package and cannot be directly executed").
The implementation has been merged into this package (see
`__main__.py` for the `python -m` entry point) so the module and its
reserved-for-subcommands package identity are no longer split across two
conflicting filesystem entries.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from engineering_studio.agents.orchestrator import run_pipeline
from engineering_studio.fireworks_client import ModelUnavailableError


def main(argv: list[str] | None = None) -> int:
    """WHAT: CLI entry point.

    ARGS:
        argv (list[str] | None): Defaults to `sys.argv[1:]`.

    RETURNS:
        int: Process exit code (0 success, 1 usage error, 2 model failure).
    """
    load_dotenv()
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print('Usage: python -m engineering_studio.cli "<product brief>"')
        return 1

    product_brief = " ".join(args)
    artifacts_root = Path("runs") / "latest" / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    try:
        outputs = run_pipeline(product_brief, artifacts_root)
    except ModelUnavailableError as exc:
        print(f"Model call failed — no fabricated result produced: {exc}")
        return 2

    print(f"Engineering Studio AI — brief: {product_brief!r}")
    for discipline, path in outputs.items():
        print(f"  {discipline:12s} -> {path}")
    return 0


__all__ = ["main"]
