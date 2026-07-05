"""WHAT: Command-line entry point: `python -m engineering_studio.cli "<brief>"`.
WHY: Fastest path to a working hackathon demo — no web server required to
show the multi-agent pipeline producing a real artifact tree.
HOW: Loads .env, runs the pipeline, prints where each artifact landed.
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


if __name__ == "__main__":
    raise SystemExit(main())
