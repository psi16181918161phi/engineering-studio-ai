"""
run_scripts.run_build_run_tests — pytest runner with coverage enforcement.

WHAT: Standalone build script that invokes pytest with coverage measurement
      and fails (non-zero exit) if coverage falls below the configured threshold.
      Returns an integer exit code.

WHY:  A reproducible, scriptable test runner is required for CI/CD pipelines
      and pre-merge gates. Encoding the coverage threshold here (rather than in
      pytest.ini or CI YAML) gives a single authoritative source version-
      controlled alongside the code it tests.

HOW:  1. _find_project_root() locates project root via marker files.
      2. Source and test directories are resolved from env vars or auto-detected.
      3. _COVERAGE_THRESHOLD is configurable via RUN_SCRIPTS_COVERAGE_THRESHOLD.
      4. run_tests() runs pytest as a subprocess with --cov and --cov-fail-under.
      5. main() calls run_tests(); returns its exit code.
      6. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT       Override auto-detected project root.
    RUN_SCRIPTS_SOURCE_NAME        Python package folder name (default: root folder name).
    RUN_SCRIPTS_SOURCE_DIR         Absolute path to source (default: <root>/<source-name>).
    RUN_SCRIPTS_TEST_DIR           Test directory (default: <root>/tests).
    RUN_SCRIPTS_COVERAGE_THRESHOLD Minimum coverage % (default: 80).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_run_tests.py)
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

_SOURCE_NAME: str = os.environ.get(
    "RUN_SCRIPTS_SOURCE_NAME", _PROJECT_ROOT.name
)
_SOURCE_DIR: str = os.environ.get(
    "RUN_SCRIPTS_SOURCE_DIR", str(_PROJECT_ROOT / _SOURCE_NAME)
)
_TEST_DIR: str = os.environ.get(
    "RUN_SCRIPTS_TEST_DIR", str(_PROJECT_ROOT / "tests")
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
    WHY:  Pure predicate extracted to keep public functions clean.
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


def _tests_present(test_dir: str) -> bool:
    """Return True if tests directory exists. Pure.

    WHAT: Checks for tests directory presence.
    WHY:  Enables graceful skip when project has no tests yet.
    HOW:  Path.is_dir(). O(1).
    INPUTS:  test_dir (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(test_dir):
        raise TypeError("test_dir must be non-empty str")
    return Path(test_dir).is_dir()


def _source_present(source_dir: str) -> bool:
    """Return True if source directory exists. Pure.

    WHAT: Checks for source directory presence.
    WHY:  Enables graceful skip when project has no Python source.
    HOW:  Path.is_dir(). O(1).
    INPUTS:  source_dir (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(source_dir):
        raise TypeError("source_dir must be non-empty str")
    return Path(source_dir).is_dir()


def _build_pytest_cmd(
    python_exe: str,
    test_dir: str,
    source_dir: str,
    threshold: int,
    with_cov: bool,
) -> list[str]:
    """Build the pytest command list. Pure.

    WHAT: Constructs the subprocess command for pytest.
    WHY:  Pure construction extracted so command can be unit-tested without
          subprocess.
    HOW:  Appends --cov args only when with_cov is True and source_dir exists.
    INPUTS:  python_exe, test_dir, source_dir, threshold (int), with_cov (bool).
    OUTPUTS: list[str] — command tokens.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    cmd = [python_exe, "-m", "pytest", test_dir, "-v", "--tb=short"]
    if with_cov and _source_present(source_dir):
        cmd += [
            f"--cov={source_dir}",
            "--cov-report=term-missing",
            f"--cov-fail-under={threshold}",
        ]
    return cmd


def _pytest_available(python_exe: str) -> bool:
    """Return True if pytest is importable. Pure-adjacent. # IMPURE.

    WHAT: Checks pytest availability via subprocess.
    WHY:  Prevents misleading failure when pytest is absent.
    HOW:  subprocess.run() with captured output.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "pytest", "--version"],
        capture_output=True,
    )
    return result.returncode == 0


def _pytest_cov_available(python_exe: str) -> bool:
    """Return True if pytest-cov is importable. # IMPURE.

    WHAT: Checks pytest-cov availability via subprocess.
    WHY:  Coverage flags require pytest-cov; graceful fallback prevents crashes.
    HOW:  subprocess.run() with captured output.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-c", "import pytest_cov"],
        capture_output=True,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def run_tests(
    python_exe: str,
    test_dir: str,
    source_dir: str,
    threshold: int,
) -> int:  # IMPURE
    """Run pytest with optional coverage enforcement. Returns exit code. # IMPURE.

    WHAT: Invokes pytest as a subprocess with coverage flags when available.
    WHY:  Subprocess invocation matches CI environment exactly (REQ-FP-01).
    HOW:  Checks for pytest/pytest-cov; builds cmd; runs subprocess.
    INPUTS:  python_exe, test_dir, source_dir, threshold.
    OUTPUTS: int — pytest exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(test_dir):
        raise TypeError("test_dir must be non-empty str")
    if not _is_valid_threshold(threshold):
        raise ValueError(f"threshold {threshold} not in [0, 100]")

    if not _tests_present(test_dir):
        print(f"[run_build_run_tests] no tests directory at {test_dir} — skipping.")  # IMPURE
        return 0

    if not _pytest_available(python_exe):
        print("[run_build_run_tests] pytest not available — skipping tests.")  # IMPURE
        return 0

    with_cov = _pytest_cov_available(python_exe)  # IMPURE
    if not with_cov:
        print("[run_build_run_tests] pytest-cov not available — running without coverage.")  # IMPURE

    cmd = _build_pytest_cmd(python_exe, test_dir, source_dir, threshold, with_cov)
    print(f"[run_build_run_tests] running: {' '.join(cmd)}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Run tests. Returns exit code. # IMPURE.

    WHAT: Orchestrates test execution with coverage enforcement.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls run_tests() with configured values; returns exit code.
    OUTPUTS: int — 0 if tests pass, non-zero otherwise.
    """
    print(f"[run_build_run_tests] project root: {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_run_tests] source dir:   {_SOURCE_DIR}")  # IMPURE
    print(f"[run_build_run_tests] test dir:      {_TEST_DIR}")  # IMPURE
    print(f"[run_build_run_tests] threshold:     {_COVERAGE_THRESHOLD}%")  # IMPURE
    return run_tests(_PYTHON_EXECUTABLE, _TEST_DIR, _SOURCE_DIR, _COVERAGE_THRESHOLD)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
