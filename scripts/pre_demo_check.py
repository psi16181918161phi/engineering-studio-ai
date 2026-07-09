"""WHAT: Single-command pre-demo regression gate — runs every quality/
security/test check the CI pipeline (`.github/workflows/ci.yml`) runs,
in the same order, against the local working tree, and prints a concise
PASS/FAIL table with an overall go/no-go exit code.
WHY: Lowers go-live risk before recording or presenting the live demo —
a presenter can run one command instead of remembering/typing six
separate tool invocations, per `docs/WISHLIST_2026-07-09_demo-one-more-round.md`
W-06. Mirrors `ci.yml`'s own step order exactly (lint -> type check ->
security static analysis -> dependency CVE audit -> unit tests -> e2e
tests) so a local green run is a genuine predictor of a green CI run,
not a narrower/looser local approximation.
HOW: Each check is invoked as `python -m <tool> ...` (matching what
`ci.yml` runs) via `subprocess.run`, capturing only the return code for
the summary table — full tool output still streams to the console live
so a failure's detail isn't hidden behind the table. Exits `0` only if
every check passed; exits `1` otherwise (never silently reports success
after a failure).

Usage:
    python scripts/pre_demo_check.py [--skip-e2e]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(label: str, args: list[str]) -> tuple[str, bool, float]:
    """WHAT: Runs one check as a subprocess, streaming its output live.

    ARGS:
        label (str): Human-readable name shown in the summary table.
        args (list[str]): Full command line (e.g. `[sys.executable, "-m", "ruff", "check", "."]`).

    RETURNS:
        tuple[str, bool, float]: `(label, passed, duration_seconds)`.
    """
    print(f"\n{'=' * 10} {label} {'=' * 10}")
    started = time.monotonic()
    result = subprocess.run(args, cwd=REPO_ROOT)
    duration = time.monotonic() - started
    return label, result.returncode == 0, round(duration, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-e2e",
        action="store_true",
        help="Skip the Playwright end-to-end suite (e.g. if browsers are not "
        "installed locally); all other checks still run.",
    )
    args = parser.parse_args()

    py = sys.executable
    checks: list[tuple[str, list[str]]] = [
        ("Lint (ruff)", [py, "-m", "ruff", "check", "."]),
        ("Type check (mypy --strict)", [py, "-m", "mypy", "src"]),
        ("Security static analysis (bandit)", [py, "-m", "bandit", "-r", "src", "-ll"]),
        ("Dependency CVE audit (pip-audit)", [py, "-m", "pip_audit"]),
        ("Unit + integration tests (100% coverage gate)", [py, "-m", "pytest", "tests", "-v", "--tb=short"]),
    ]
    if not args.skip_e2e:
        checks.append(
            (
                "End-to-end tests (Playwright, Mode B)",
                [py, "-m", "pytest", "tests/e2e", "-v", "--tb=short", "--no-cov"],
            )
        )

    results = [_run(label, cmd) for label, cmd in checks]

    print(f"\n{'=' * 10} SUMMARY {'=' * 10}")
    header = f"{'CHECK':<48} {'RESULT':<8} {'TIME(s)'}"
    print(header)
    print("-" * len(header))
    for label, passed, duration in results:
        print(f"{label:<48} {'PASS' if passed else 'FAIL':<8} {duration}")

    all_passed = all(passed for _, passed, _ in results)
    print(f"\nOverall: {'GO' if all_passed else 'NO-GO'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
