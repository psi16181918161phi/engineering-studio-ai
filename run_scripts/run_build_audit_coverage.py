"""
run_scripts.run_build_audit_coverage — Final coverage audit / fail-under gate.

WHAT: Standalone build script that runs `coverage report --fail-under=<N>` on
      an existing .coverage data file and returns a non-zero exit code if the
      total coverage is below the threshold. Designed as the last CI gate.

WHY:  Separating the coverage fail-under gate from the test runner (run_build_run_tests)
      allows reports to be generated first and the fail gate to be applied last,
      giving maximum diagnostic information before the pipeline terminates.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _COVERAGE_DATA and _COVERAGE_THRESHOLD are resolved from env vars.
      3. run_coverage_audit() invokes `python -m coverage report --fail-under=<N>`.
      4. main() calls run_coverage_audit(); returns its exit code.
      5. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT       Override auto-detected project root.
    RUN_SCRIPTS_COVERAGE_DATA      Coverage data file (default: <root>/.coverage).
    RUN_SCRIPTS_COVERAGE_THRESHOLD Minimum coverage % (default: 80).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_audit_coverage.py)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root resolution (agnostic)
# ---------------------------------------------------------------------------

_ROOT_MARKERS: frozenset[str] = frozenset({
    "pyproject.toml", "setup.py", "setup.cfg", ".git", "requirements.txt",
})


def _find_project_root(start: Path) -> Path:
    """Walk up from start until a root marker is found. Pure.

    WHAT: Traverses parent directories looking for root markers.
    WHY:  Enables zero-configuration use — no hardcoded paths required (G-06).
    HOW:  Iterates parents; returns the first directory containing a marker.
    INPUTS:  start (Path).
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

_COVERAGE_DATA: str = os.environ.get(
    "RUN_SCRIPTS_COVERAGE_DATA", str(_PROJECT_ROOT / ".coverage")
)
_MAX_COVERAGE: int = 100
_COVERAGE_THRESHOLD: int = int(
    os.environ.get("RUN_SCRIPTS_COVERAGE_THRESHOLD", "80")
)
_PYTHON_EXECUTABLE: str = sys.executable


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _is_bad_str(value: object) -> bool:
    """Return True if value is not a non-empty str. O(1). Pure.

    WHAT: Validates that value is a non-empty string.
    WHY:  Pure predicate.
    HOW:  isinstance + truthiness. O(1).
    INPUTS:  value (object).
    OUTPUTS: bool — True if invalid.
    """
    return not isinstance(value, str) or not value


def _is_bad_int(value: object) -> bool:
    """Return True if value is not an int. O(1). Pure.

    WHAT: Validates int type.
    WHY:  Pure predicate.
    HOW:  isinstance. O(1).
    INPUTS:  value (object).
    OUTPUTS: bool.
    """
    return not isinstance(value, int)


def _is_valid_threshold(threshold: int) -> bool:
    """Return True if threshold is in [0, 100]. Pure.

    WHAT: Checks coverage threshold range.
    WHY:  Pure predicate — extracted to avoid chained Compare in callers.
    HOW:  Chained comparison. O(1).
    INPUTS:  threshold (int).
    OUTPUTS: bool.
    """
    if _is_bad_int(threshold):
        raise TypeError(f"threshold must be int, got {type(threshold)}")
    return 0 <= threshold <= _MAX_COVERAGE


def _coverage_data_present(data_path: str) -> bool:
    """Return True if the .coverage data file exists. Pure.

    WHAT: Checks coverage data file presence.
    WHY:  Enables graceful skip if tests have not been run yet.
    HOW:  Path.exists(). O(1).
    INPUTS:  data_path (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(data_path):
        raise TypeError("data_path must be non-empty str")
    return Path(data_path).exists()


def _build_coverage_cmd(
    python_exe: str, coverage_data: str, threshold: int
) -> list[str]:
    """Build coverage report command. Pure.

    WHAT: Constructs the subprocess command for coverage report.
    WHY:  Pure construction enables unit-testing without subprocess.
    HOW:  Assembles coverage report --data-file --fail-under flags.
    INPUTS:  python_exe, coverage_data, threshold.
    OUTPUTS: list[str] — command tokens.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(coverage_data):
        raise TypeError("coverage_data must be non-empty str")
    if not _is_valid_threshold(threshold):
        raise ValueError(f"threshold {threshold} not in [0, 100]")
    return [
        python_exe, "-m", "coverage", "report",
        f"--data-file={coverage_data}",
        f"--fail-under={threshold}",
    ]


# ---------------------------------------------------------------------------
# Availability check (IMPURE)
# ---------------------------------------------------------------------------


def _coverage_available(python_exe: str) -> bool:  # IMPURE
    """Return True if coverage is importable. # IMPURE.

    WHAT: Checks coverage package availability via subprocess.
    WHY:  Prevents misleading failures when coverage not installed.
    HOW:  subprocess.run() python -m coverage --version.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "coverage", "--version"], capture_output=True
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def run_coverage_audit(
    python_exe: str, coverage_data: str, threshold: int
) -> int:  # IMPURE
    """Run coverage report --fail-under. Returns exit code. # IMPURE.

    WHAT: Invokes `coverage report --fail-under=<threshold>` on coverage_data.
    WHY:  Final pipeline gate — rejects builds that do not meet coverage bar.
    HOW:  Checks prerequisites; builds cmd; runs subprocess; returns returncode.
    INPUTS:  python_exe (str), coverage_data (str), threshold (int).
    OUTPUTS: int — exit code (non-zero if below threshold or data absent).
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if not _is_valid_threshold(threshold):
        raise ValueError(f"threshold {threshold} not in [0, 100]")

    if not _coverage_data_present(coverage_data):
        print(f"[run_build_audit_coverage] .coverage file absent: {coverage_data} — skipping audit.")  # IMPURE
        return 0

    if not _coverage_available(python_exe):  # IMPURE
        print("[run_build_audit_coverage] coverage not available — skipping. (pip install coverage)")  # IMPURE
        return 0

    cmd = _build_coverage_cmd(python_exe, coverage_data, threshold)
    print(f"[run_build_audit_coverage] auditing coverage ≥ {threshold}% from {coverage_data}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Run coverage audit gate. Returns exit code. # IMPURE.

    WHAT: Applies the coverage fail-under gate as the final pipeline check.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls run_coverage_audit() with configured values; returns exit code.
    OUTPUTS: int — 0 if coverage ≥ threshold, non-zero otherwise.
    """
    print(f"[run_build_audit_coverage] project root: {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_audit_coverage] coverage data: {_COVERAGE_DATA}")  # IMPURE
    print(f"[run_build_audit_coverage] threshold:     {_COVERAGE_THRESHOLD}%")  # IMPURE
    return run_coverage_audit(_PYTHON_EXECUTABLE, _COVERAGE_DATA, _COVERAGE_THRESHOLD)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
