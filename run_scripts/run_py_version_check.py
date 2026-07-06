"""
run_scripts.run_py_version_check — Python interpreter version validator.

WHAT: Standalone script that validates the current Python interpreter meets
      the minimum version requirement for this project. Returns exit code 0
      if compatible, 1 if not.

WHY:  Version mismatches are the most common cause of silent compatibility
      failures. Validating the interpreter before any other build step
      surfaces this issue early with a clear diagnostic (FP Principle 9).

HOW:  1. _find_project_root() walks up from __file__ to locate project root.
      2. _MIN_PYTHON is read from RUN_SCRIPTS_MIN_PYTHON env var (default "3,9").
      3. check_version() compares sys.version_info against the minimum tuple.
      4. main() calls check_version(); prints diagnostic; returns exit code.
      5. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT    Override auto-detected project root.
    RUN_SCRIPTS_MIN_PYTHON      Minimum version as "major,minor" (default "3,9").

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_py_version_check.py)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root resolution (agnostic — works in any project)
# ---------------------------------------------------------------------------

_ROOT_MARKERS: frozenset[str] = frozenset({
    "pyproject.toml", "setup.py", "setup.cfg", ".git", "requirements.txt",
})


def _find_project_root(start: Path) -> Path:
    """Walk up from start until a root marker is found. Pure.

    WHAT: Traverses parent directories looking for root markers.
    WHY:  Enables zero-configuration use — no hardcoded paths required (G-06).
    HOW:  Iterates parents; returns the first directory containing a marker.
          Falls back to start.resolve() if no marker found.
    INPUTS:  start (Path) — directory from which to begin the search.
    OUTPUTS: Path — resolved project root.
    """
    candidate = start.resolve()
    while candidate != candidate.parent:
        if any((candidate / m).exists() for m in _ROOT_MARKERS):
            return candidate
        candidate = candidate.parent
    return start.resolve()


_OVERRIDE_ROOT: str = os.environ.get("RUN_SCRIPTS_PROJECT_ROOT", "")
_PROJECT_ROOT: Path = (
    Path(_OVERRIDE_ROOT).resolve()
    if _OVERRIDE_ROOT
    else _find_project_root(Path(__file__).parent)
)

# ---------------------------------------------------------------------------
# Frozen module-level constants (REQ-FP-04)
# ---------------------------------------------------------------------------

_PYTHON_EXECUTABLE: str = sys.executable

def _parse_min_python(raw: str) -> tuple[int, int]:
    """Parse "major,minor" string into (major, minor) tuple. Pure.

    WHAT: Converts env var string to version tuple.
    WHY:  Pure parsing extracted to avoid inline try/except in constants section.
    HOW:  Splits on comma, converts to int, validates length.
    INPUTS:  raw (str) — e.g. "3,9" or "3,11".
    OUTPUTS: tuple[int, int] — (major, minor).
    """
    try:
        parts = [int(p.strip()) for p in raw.split(",")]
        if len(parts) >= 2:
            return (parts[0], parts[1])
    except (ValueError, AttributeError):
        pass
    return (3, 9)


_MIN_PYTHON: tuple[int, int] = _parse_min_python(
    os.environ.get("RUN_SCRIPTS_MIN_PYTHON", "3,9")
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _is_bad_tuple(value: object) -> bool:
    """Return True if value is not a 2-tuple of ints. O(1). Pure.

    WHAT: Validates that value is a (major, minor) version tuple.
    WHY:  Pure predicate extracted to keep check_version() free of isinstance.
    HOW:  isinstance checks. O(1).
    INPUTS:  value (object).
    OUTPUTS: bool — True if invalid.
    """
    return (
        not isinstance(value, tuple)
        or len(value) != 2
        or not all(isinstance(x, int) for x in value)
    )


def _version_satisfied(current: tuple[int, int], minimum: tuple[int, int]) -> bool:
    """Return True if current >= minimum. Pure.

    WHAT: Compares two (major, minor) version tuples.
    WHY:  Pure predicate — extracted so check_version() avoids Compare ops.
    HOW:  Tuple comparison (lexicographic, which matches semantic version order).
    INPUTS:  current (tuple[int, int]), minimum (tuple[int, int]).
    OUTPUTS: bool — True if current satisfies minimum requirement.
    """
    if _is_bad_tuple(current):
        raise TypeError(f"current must be (int, int) tuple, got {type(current)}")
    if _is_bad_tuple(minimum):
        raise TypeError(f"minimum must be (int, int) tuple, got {type(minimum)}")
    return current >= minimum


def _format_version(v: tuple[int, int]) -> str:
    """Return 'major.minor' string. Pure.

    WHAT: Converts version tuple to display string.
    WHY:  Pure formatting extracted to keep I/O surfaces in main().
    HOW:  f-string join. O(1).
    INPUTS:  v (tuple[int, int]).
    OUTPUTS: str — e.g. "3.11".
    """
    return f"{v[0]}.{v[1]}"


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def check_version(minimum: tuple[int, int]) -> int:  # IMPURE — reads sys.version_info
    """Check current interpreter version against minimum. Returns exit code. # IMPURE.

    WHAT: Compares sys.version_info[:2] against minimum; prints diagnostic.
    WHY:  Centralises version check so it can be called both from main() and
          programmatically by other tools.
    HOW:  Reads sys.version_info (IMPURE), delegates comparison to
          _version_satisfied(), prints result.
    INPUTS:  minimum (tuple[int, int]) — required (major, minor).
    OUTPUTS: int — 0 if satisfied, 1 if not.
    """
    if _is_bad_tuple(minimum):
        raise TypeError(f"minimum must be (int, int) tuple, got {type(minimum)}")
    current: tuple[int, int] = (sys.version_info.major, sys.version_info.minor)  # IMPURE
    satisfied = _version_satisfied(current, minimum)
    status = "OK" if satisfied else "FAIL"
    print(  # IMPURE
        f"[{status}] Python {_format_version(current)} "
        f"(required >= {_format_version(minimum)}) "
        f"— {_PYTHON_EXECUTABLE}"
    )
    return 0 if satisfied else 1


def main() -> int:  # IMPURE
    """Entry point: validate Python version. Returns exit code. # IMPURE.

    WHAT: Orchestrates version check and returns combined exit code.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls check_version(_MIN_PYTHON); returns its exit code.
    OUTPUTS: int — 0 if version satisfied, 1 otherwise.
    """
    print(f"[run_py_version_check] project root: {_PROJECT_ROOT}")  # IMPURE
    return check_version(_MIN_PYTHON)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
