"""
run_scripts.run_build_pypi_package — PyPI package build and validation.

WHAT: Standalone build script that builds a Python distribution package (wheel
      and sdist) using `python -m build` and validates the artefacts with
      `twine check`. Returns a combined exit code.

WHY:  Automating package build and validation in a single reproducible script
      ensures every release artefact is checked before upload. Running `twine
      check` locally catches malformed metadata that would fail on PyPI.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _project_has_build_config() checks for pyproject.toml or setup.py.
      3. build_package() runs `python -m build --outdir <dist_dir>`.
      4. check_package() runs `twine check <dist_dir>/*`.
      5. main() calls both in sequence; returns combined exit code.
      6. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT  Override auto-detected project root.
    RUN_SCRIPTS_DIST_DIR      PyPI distribution output directory
                               (default: <root>/dist).
    RUN_SCRIPTS_SKIP_TWINE    Set to "1" to skip twine check.

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_pypi_package.py)
"""
from __future__ import annotations

import glob
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

_DIST_DIR: str = os.environ.get("RUN_SCRIPTS_DIST_DIR", str(_PROJECT_ROOT / "dist"))
_SKIP_TWINE: bool = os.environ.get("RUN_SCRIPTS_SKIP_TWINE", "0") == "1"
_PYTHON_EXECUTABLE: str = sys.executable
_BUILD_CONFIG_MARKERS: frozenset[str] = frozenset({"pyproject.toml", "setup.py", "setup.cfg"})


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


def _project_has_build_config(project_root: Path) -> bool:
    """Return True if project root has pyproject.toml or setup.py. Pure.

    WHAT: Checks for build system configuration files.
    WHY:  `python -m build` requires at least pyproject.toml or setup.py.
    HOW:  Path.exists() for each candidate.
    INPUTS:  project_root (Path).
    OUTPUTS: bool.
    """
    return any((project_root / m).exists() for m in _BUILD_CONFIG_MARKERS)


def _artefacts_present(dist_dir: str) -> list[str]:
    """Return list of built artefacts in dist_dir. Pure-ish.

    WHAT: Globs for *.whl and *.tar.gz files in dist_dir.
    WHY:  twine check needs the artefact paths; building may produce one or both.
    HOW:  glob.glob(). O(n) on directory entries.
    INPUTS:  dist_dir (str).
    OUTPUTS: list[str] — absolute artefact paths.
    """
    if _is_bad_str(dist_dir):
        raise TypeError("dist_dir must be non-empty str")
    whl = glob.glob(str(Path(dist_dir) / "*.whl"))
    tgz = glob.glob(str(Path(dist_dir) / "*.tar.gz"))
    return whl + tgz


# ---------------------------------------------------------------------------
# Availability checks (IMPURE)
# ---------------------------------------------------------------------------


def _build_available(python_exe: str) -> bool:  # IMPURE
    """Return True if `python -m build` is available. # IMPURE.

    WHAT: Checks build package availability via subprocess.
    WHY:  Prevents misleading failures when 'build' not installed.
    HOW:  subprocess.run() python -m build --version.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "build", "--version"], capture_output=True
    )
    return result.returncode == 0


def _twine_available(python_exe: str) -> bool:  # IMPURE
    """Return True if twine is available. # IMPURE.

    WHAT: Checks twine package availability via subprocess.
    WHY:  twine check is optional — skip gracefully if absent.
    HOW:  subprocess.run() python -m twine --version.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "twine", "--version"], capture_output=True
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def build_package(python_exe: str, dist_dir: str) -> int:  # IMPURE
    """Build the Python distribution package. Returns exit code. # IMPURE.

    WHAT: Runs `python -m build --outdir <dist_dir>`.
    WHY:  Creates wheel + sdist artefacts for PyPI publishing.
    HOW:  Creates dist_dir if needed; runs subprocess; returns returncode.
    INPUTS:  python_exe (str), dist_dir (str).
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(dist_dir):
        raise TypeError("dist_dir must be non-empty str")
    Path(dist_dir).mkdir(parents=True, exist_ok=True)  # IMPURE
    cmd = [python_exe, "-m", "build", "--outdir", dist_dir]
    print(f"[run_build_pypi_package] building package → {dist_dir}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def check_package(python_exe: str, dist_dir: str) -> int:  # IMPURE
    """Run twine check on built artefacts. Returns exit code. # IMPURE.

    WHAT: Runs `python -m twine check <artefacts>`.
    WHY:  Validates package metadata before upload (REQ-FP-01).
    HOW:  Globs artefacts; skips if none found; runs subprocess.
    INPUTS:  python_exe (str), dist_dir (str).
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if _is_bad_str(dist_dir):
        raise TypeError("dist_dir must be non-empty str")
    artefacts = _artefacts_present(dist_dir)
    if not artefacts:
        print(f"[run_build_pypi_package] no artefacts found in {dist_dir} — skipping twine check.")  # IMPURE
        return 0
    if not _twine_available(python_exe):  # IMPURE
        print("[run_build_pypi_package] twine not available — skipping twine check.")  # IMPURE
        return 0
    cmd = [python_exe, "-m", "twine", "check"] + artefacts
    print(f"[run_build_pypi_package] twine check on {len(artefacts)} artefact(s)")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Build and validate PyPI package. Returns exit code. # IMPURE.

    WHAT: Orchestrates package build and twine validation.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Checks prerequisites; calls build_package(); optionally check_package();
          returns 1 if any step fails.
    OUTPUTS: int — 0 if all steps passed, 1 otherwise.
    """
    print(f"[run_build_pypi_package] project root: {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_pypi_package] dist dir:     {_DIST_DIR}")  # IMPURE

    if not _project_has_build_config(_PROJECT_ROOT):
        print("[run_build_pypi_package] no pyproject.toml / setup.py found — skipping build.")  # IMPURE
        return 0

    if not _build_available(_PYTHON_EXECUTABLE):  # IMPURE
        print("[run_build_pypi_package] 'build' package not available — skipping. (pip install build)")  # IMPURE
        return 0

    rc_build = build_package(_PYTHON_EXECUTABLE, _DIST_DIR)  # IMPURE
    if rc_build != 0:
        return rc_build

    if _SKIP_TWINE:
        print("[run_build_pypi_package] twine check skipped (RUN_SCRIPTS_SKIP_TWINE=1).")  # IMPURE
        return 0

    return check_package(_PYTHON_EXECUTABLE, _DIST_DIR)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
