"""
run_scripts.run_build_venv — Virtual environment creation and dependency install.

WHAT: Standalone build script that creates (or recreates) a Python virtual
      environment at a configurable path and installs all project dependencies
      from requirements.txt. Returns an integer exit code suitable for CI/CD.

WHY:  Reproducible environments are a prerequisite for all other build steps.
      A dedicated, idempotent venv script ensures every developer and CI agent
      starts from an identical baseline. Centralising venv logic here eliminates
      ad-hoc setup commands in READMEs and CI YAML files.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _VENV_DIR is read from RUN_SCRIPTS_VENV_DIR env var; defaults to .venv.
      3. _REQUIREMENTS_FILE is computed from project root — no hardcoded paths.
      4. create_venv() creates the venv; install_requirements() installs deps.
      5. main() orchestrates both steps; returns 0 on success, 1 on failure.
      6. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT      Override auto-detected project root.
    RUN_SCRIPTS_VENV_DIR          Venv directory (default: <root>/.venv).
    RUN_SCRIPTS_REQUIREMENTS_FILE Requirements file (default: <root>/requirements.txt).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_venv.py)
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

_VENV_DIR: str = os.environ.get(
    "RUN_SCRIPTS_VENV_DIR", str(_PROJECT_ROOT / ".venv")
)
_REQUIREMENTS_FILE: str = os.environ.get(
    "RUN_SCRIPTS_REQUIREMENTS_FILE", str(_PROJECT_ROOT / "requirements.txt")
)
_PYTHON_EXECUTABLE: str = sys.executable


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _is_bad_str(value: object) -> bool:
    """Return True if value is not a non-empty str. O(1). Pure.

    WHAT: Validates that value is a non-empty string.
    WHY:  Pure predicate extracted to keep public functions free of isinstance.
    HOW:  isinstance + truthiness. O(1).
    INPUTS:  value (object).
    OUTPUTS: bool — True if invalid.
    """
    return not isinstance(value, str) or not value


def _subprocess_failed(result: object) -> bool:
    """Return True if subprocess result has non-zero returncode. O(1). Pure.

    WHAT: Checks result.returncode for non-zero value.
    WHY:  Pure predicate extracted to avoid Compare nodes in callers (SOLID-03).
    HOW:  Direct comparison. O(1).
    INPUTS:  result (object) — subprocess.CompletedProcess.
    OUTPUTS: bool — True if returncode != 0.
    """
    assert hasattr(result, "returncode"), f"Expected returncode, got {type(result)}"
    return result.returncode != 0  # type: ignore[union-attr]


def _get_pip_path(venv_dir: str) -> str:
    """Return platform-aware pip path inside venv. Pure.

    WHAT: Constructs pip executable path within the given venv directory.
    WHY:  Pure computation — Windows uses Scripts/, POSIX uses bin/.
    HOW:  sys.platform check + Path construction. O(1).
    INPUTS:  venv_dir (str) — path to venv root.
    OUTPUTS: str — absolute path to pip executable.
    """
    if _is_bad_str(venv_dir):
        raise TypeError(f"venv_dir must be non-empty str, got {type(venv_dir)}")
    subdir = "Scripts" if sys.platform == "win32" else "bin"
    return str(Path(venv_dir) / subdir / "pip")


def _requirements_present(req_file: str) -> bool:
    """Return True if the requirements file exists. Pure.

    WHAT: Checks file existence.
    WHY:  Pure predicate — extracted so install_requirements() avoids os.path calls.
    HOW:  Path.exists(). O(1).
    INPUTS:  req_file (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(req_file):
        raise TypeError(f"req_file must be non-empty str, got {type(req_file)}")
    return Path(req_file).exists()


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def create_venv(python_executable: str, venv_dir: str) -> int:  # IMPURE
    """Create a virtual environment at venv_dir. Returns exit code. # IMPURE.

    WHAT: Runs `python -m venv <venv_dir>` as a subprocess.
    WHY:  Creates a reproducible isolated Python environment (REQ-FP-01).
    HOW:  subprocess.run() with check=False; returns returncode.
    INPUTS:  python_executable (str), venv_dir (str).
    OUTPUTS: int — 0 on success, non-zero on failure.
    """
    if _is_bad_str(python_executable):
        raise TypeError(f"python_executable must be non-empty str")
    if _is_bad_str(venv_dir):
        raise TypeError(f"venv_dir must be non-empty str")
    print(f"[run_build_venv] creating venv at {venv_dir}")  # IMPURE
    result = subprocess.run(  # IMPURE
        [python_executable, "-m", "venv", venv_dir],
        cwd=str(_PROJECT_ROOT),
    )
    return result.returncode


def install_requirements(venv_dir: str, requirements_file: str) -> int:  # IMPURE
    """Install requirements into venv. Returns exit code. # IMPURE.

    WHAT: Runs `pip install -r <requirements_file>` inside the venv.
    WHY:  Installs reproducible pinned dependencies (REQ-FP-01).
    HOW:  subprocess.run() using venv pip; returns returncode; skips if
          requirements file absent.
    INPUTS:  venv_dir (str), requirements_file (str).
    OUTPUTS: int — 0 on success, non-zero on failure, 0 if skipped.
    """
    if _is_bad_str(venv_dir):
        raise TypeError(f"venv_dir must be non-empty str")
    if _is_bad_str(requirements_file):
        raise TypeError(f"requirements_file must be non-empty str")
    if not _requirements_present(requirements_file):
        print(f"[run_build_venv] no requirements.txt found at {requirements_file} — skipping install.")  # IMPURE
        return 0
    pip_path = _get_pip_path(venv_dir)
    print(f"[run_build_venv] installing {requirements_file} via {pip_path}")  # IMPURE
    result = subprocess.run(  # IMPURE
        [pip_path, "install", "-r", requirements_file],
        cwd=str(_PROJECT_ROOT),
    )
    return result.returncode


def main() -> int:  # IMPURE
    """Create venv and install requirements. Returns exit code. # IMPURE.

    WHAT: Orchestrates venv creation and dependency installation.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls create_venv() then install_requirements(); returns max exit code.
    OUTPUTS: int — 0 if all steps passed, 1 if any failed.
    """
    print(f"[run_build_venv] project root: {_PROJECT_ROOT}")  # IMPURE
    rc_venv = create_venv(_PYTHON_EXECUTABLE, _VENV_DIR)  # IMPURE
    if rc_venv != 0:
        return rc_venv
    return install_requirements(_VENV_DIR, _REQUIREMENTS_FILE)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
