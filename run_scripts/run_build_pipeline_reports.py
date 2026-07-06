"""
run_scripts.run_build_pipeline_reports — Coverage HTML and JSON report generator.

WHAT: Standalone build script that generates HTML and JSON coverage reports
      from a .coverage data file. Skips gracefully if the data file is absent
      or if coverage is not installed.

WHY:  Human-readable and machine-readable coverage reports are required for
      code-review, traceability dashboards, and CI artefact archiving. Placing
      report generation in a dedicated script decouples it from the test runner,
      allowing reports to be regenerated independently.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _COVERAGE_DATA path and _REPORTS_DIR are resolved from env vars.
      3. generate_html_report() runs `python -m coverage html`.
      4. generate_json_report() runs `python -m coverage json`.
      5. main() calls both; returns 0 if all succeed, 1 otherwise.
      6. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT  Override auto-detected project root.
    RUN_SCRIPTS_COVERAGE_DATA Coverage data file (default: <root>/.coverage).
    RUN_SCRIPTS_REPORTS_DIR   Report output directory (default: <root>/markdowns/reports,
                               falls back to <root>/reports).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_pipeline_reports.py)
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

_DEFAULT_REPORTS_DIR: Path = (
    _PROJECT_ROOT / "markdowns" / "reports"
    if (_PROJECT_ROOT / "markdowns").is_dir()
    else _PROJECT_ROOT / "reports"
)
_REPORTS_DIR: str = os.environ.get(
    "RUN_SCRIPTS_REPORTS_DIR", str(_DEFAULT_REPORTS_DIR)
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


def _coverage_data_present(data_path: str) -> bool:
    """Return True if the .coverage data file exists. Pure.

    WHAT: Checks coverage data file presence.
    WHY:  Enables graceful skip when tests have not been run yet.
    HOW:  Path.exists(). O(1).
    INPUTS:  data_path (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(data_path):
        raise TypeError("data_path must be non-empty str")
    return Path(data_path).exists()


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


def generate_html_report(
    python_exe: str, coverage_data: str, reports_dir: str
) -> int:  # IMPURE
    """Generate HTML coverage report. Returns exit code. # IMPURE.

    WHAT: Runs `python -m coverage html --data-file=<data> -d <reports_dir>`.
    WHY:  Human-readable report for developers and code-review (REQ-FP-01).
    HOW:  Creates output directory if needed; runs subprocess.
    INPUTS:  python_exe (str), coverage_data (str), reports_dir (str).
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(coverage_data):
        raise TypeError("coverage_data must be non-empty str")
    if _is_bad_str(reports_dir):
        raise TypeError("reports_dir must be non-empty str")
    Path(reports_dir).mkdir(parents=True, exist_ok=True)  # IMPURE
    html_dir = str(Path(reports_dir) / "htmlcov")
    cmd = [
        python_exe, "-m", "coverage", "html",
        f"--data-file={coverage_data}",
        f"-d", html_dir,
    ]
    print(f"[run_build_pipeline_reports] generating HTML report → {html_dir}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def generate_json_report(
    python_exe: str, coverage_data: str, reports_dir: str
) -> int:  # IMPURE
    """Generate JSON coverage report. Returns exit code. # IMPURE.

    WHAT: Runs `python -m coverage json --data-file=<data> -o <output>`.
    WHY:  Machine-readable report for dashboards and CI artefact parsing.
    HOW:  Creates output directory if needed; runs subprocess.
    INPUTS:  python_exe (str), coverage_data (str), reports_dir (str).
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(coverage_data):
        raise TypeError("coverage_data must be non-empty str")
    if _is_bad_str(reports_dir):
        raise TypeError("reports_dir must be non-empty str")
    Path(reports_dir).mkdir(parents=True, exist_ok=True)  # IMPURE
    json_out = str(Path(reports_dir) / "coverage.json")
    cmd = [
        python_exe, "-m", "coverage", "json",
        f"--data-file={coverage_data}",
        f"-o", json_out,
    ]
    print(f"[run_build_pipeline_reports] generating JSON report → {json_out}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Generate coverage reports. Returns exit code. # IMPURE.

    WHAT: Orchestrates HTML and JSON report generation.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Checks prerequisites; calls generate_html_report() and
          generate_json_report(); returns 1 if any fail.
    OUTPUTS: int — 0 if both succeeded, 1 otherwise.
    """
    print(f"[run_build_pipeline_reports] project root:   {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_pipeline_reports] coverage data:  {_COVERAGE_DATA}")  # IMPURE
    print(f"[run_build_pipeline_reports] reports dir:    {_REPORTS_DIR}")  # IMPURE

    if not _coverage_data_present(_COVERAGE_DATA):
        print("[run_build_pipeline_reports] .coverage data file absent — skipping report generation.")  # IMPURE
        return 0

    if not _coverage_available(_PYTHON_EXECUTABLE):  # IMPURE
        print("[run_build_pipeline_reports] coverage not available — skipping.")  # IMPURE
        return 0

    rc_html = generate_html_report(_PYTHON_EXECUTABLE, _COVERAGE_DATA, _REPORTS_DIR)  # IMPURE
    rc_json = generate_json_report(_PYTHON_EXECUTABLE, _COVERAGE_DATA, _REPORTS_DIR)  # IMPURE
    return 0 if (rc_html == 0 and rc_json == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
