"""
run_scripts.run_build_python_agnostic_executables — PyInstaller binary builder.

WHAT: Standalone build script that compiles the project's entry-point Python
      script into a single-file standalone executable using PyInstaller.
      Returns a non-zero exit code if the build fails.

WHY:  A portable binary distribution allows end-users to run the application
      without installing Python. Including this step in the automated pipeline
      ensures the binary is always built from a clean, tested source tree.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _detect_entry_script() auto-locates __main__.py in source or root.
      3. _EXECUTABLE_NAME and _DIST_BIN_DIR are resolved from env vars.
      4. build_executable() invokes PyInstaller as a subprocess.
      5. main() calls build_executable(); returns exit code.
      6. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT    Override auto-detected project root.
    RUN_SCRIPTS_ENTRY_SCRIPT    CLI entry-point script (default: auto-detected __main__.py).
    RUN_SCRIPTS_EXECUTABLE_NAME Binary output name (default: <root-folder-name>).
    RUN_SCRIPTS_DIST_BIN_DIR    Binary output directory (default: <root>/dist_bin).
    RUN_SCRIPTS_SOURCE_NAME     Python package folder name (default: root folder name).
    RUN_SCRIPTS_SOURCE_DIR      Absolute path to source (default: <root>/<source-name>).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_python_agnostic_executables.py)
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
# Pure helpers — entry script detection
# ---------------------------------------------------------------------------

_SOURCE_NAME: str = os.environ.get("RUN_SCRIPTS_SOURCE_NAME", _PROJECT_ROOT.name)
_SOURCE_DIR: Path = Path(
    os.environ.get("RUN_SCRIPTS_SOURCE_DIR", str(_PROJECT_ROOT / _SOURCE_NAME))
)


def _detect_entry_script(source_dir: Path, project_root: Path) -> str:
    """Find __main__.py, preferring source_dir over project root. Pure-ish.

    WHAT: Searches for the entry-point script.
    WHY:  Avoids requiring the user to specify the entry point explicitly (G-06).
    HOW:  Checks source_dir/__main__.py then project_root/__main__.py.
    INPUTS:  source_dir (Path), project_root (Path).
    OUTPUTS: str — absolute path to __main__.py, or empty string if not found.
    """
    for candidate in (source_dir / "__main__.py", project_root / "__main__.py"):
        if candidate.is_file():
            return str(candidate.resolve())
    return ""


# ---------------------------------------------------------------------------
# Frozen module-level constants (REQ-FP-04)
# ---------------------------------------------------------------------------

_ENTRY_SCRIPT: str = os.environ.get(
    "RUN_SCRIPTS_ENTRY_SCRIPT", _detect_entry_script(_SOURCE_DIR, _PROJECT_ROOT)
)
_EXECUTABLE_NAME: str = os.environ.get(
    "RUN_SCRIPTS_EXECUTABLE_NAME", _PROJECT_ROOT.name
)
_DIST_BIN_DIR: str = os.environ.get(
    "RUN_SCRIPTS_DIST_BIN_DIR", str(_PROJECT_ROOT / "dist_bin")
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


def _build_pyinstaller_cmd(
    python_exe: str,
    entry_script: str,
    executable_name: str,
    dist_bin_dir: str,
    project_root: Path,
) -> list[str]:
    """Construct the PyInstaller command list. Pure.

    WHAT: Builds the subprocess command tokens for a PyInstaller one-file build.
    WHY:  Pure construction enables unit-testing command without running subprocess.
    HOW:  Assembles --name, --distpath, --specpath, --onefile flags.
    INPUTS:  python_exe, entry_script, executable_name, dist_bin_dir, project_root.
    OUTPUTS: list[str] — command tokens.
    """
    spec_dir = str(project_root / "build_spec")
    return [
        python_exe, "-m", "PyInstaller",
        "--name", executable_name,
        "--onefile",
        "--distpath", dist_bin_dir,
        "--specpath", spec_dir,
        "--clean",
        entry_script,
    ]


# ---------------------------------------------------------------------------
# Availability check (IMPURE)
# ---------------------------------------------------------------------------


def _pyinstaller_available(python_exe: str) -> bool:  # IMPURE
    """Return True if PyInstaller is importable. # IMPURE.

    WHAT: Checks PyInstaller availability via subprocess.
    WHY:  Graceful skip when PyInstaller not installed.
    HOW:  subprocess.run() python -m PyInstaller --version.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "PyInstaller", "--version"], capture_output=True
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def build_executable(
    python_exe: str,
    entry_script: str,
    executable_name: str,
    dist_bin_dir: str,
) -> int:  # IMPURE
    """Build standalone executable with PyInstaller. Returns exit code. # IMPURE.

    WHAT: Invokes PyInstaller to compile entry_script into a single binary.
    WHY:  Produces a portable artefact for end-users without Python installed.
    HOW:  Creates dist_bin_dir if needed; runs subprocess; returns returncode.
    INPUTS:  python_exe, entry_script, executable_name, dist_bin_dir.
    OUTPUTS: int — exit code.
    """
    for name, val in (
        ("python_exe", python_exe),
        ("entry_script", entry_script),
        ("executable_name", executable_name),
        ("dist_bin_dir", dist_bin_dir),
    ):
        if _is_bad_str(val):
            raise TypeError(f"{name} must be non-empty str")
    Path(dist_bin_dir).mkdir(parents=True, exist_ok=True)  # IMPURE
    cmd = _build_pyinstaller_cmd(
        python_exe, entry_script, executable_name, dist_bin_dir, _PROJECT_ROOT
    )
    print(f"[run_build_python_agnostic_executables] building → {dist_bin_dir}/{executable_name}")  # IMPURE
    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Build standalone executable. Returns exit code. # IMPURE.

    WHAT: Orchestrates PyInstaller build.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Checks prerequisites; calls build_executable(); returns exit code.
    OUTPUTS: int — 0 if succeeded, 1 otherwise.
    """
    print(f"[run_build_python_agnostic_executables] project root:     {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_python_agnostic_executables] entry script:     {_ENTRY_SCRIPT}")  # IMPURE
    print(f"[run_build_python_agnostic_executables] executable name:  {_EXECUTABLE_NAME}")  # IMPURE
    print(f"[run_build_python_agnostic_executables] dist bin dir:     {_DIST_BIN_DIR}")  # IMPURE

    if not _ENTRY_SCRIPT:
        print("[run_build_python_agnostic_executables] no __main__.py found — skipping executable build.")  # IMPURE
        return 0

    if not Path(_ENTRY_SCRIPT).is_file():
        print(f"[run_build_python_agnostic_executables] entry script not found: {_ENTRY_SCRIPT} — skipping.")  # IMPURE
        return 0

    if not _pyinstaller_available(_PYTHON_EXECUTABLE):  # IMPURE
        print("[run_build_python_agnostic_executables] PyInstaller not available — skipping. (pip install pyinstaller)")  # IMPURE
        return 0

    return build_executable(_PYTHON_EXECUTABLE, _ENTRY_SCRIPT, _EXECUTABLE_NAME, _DIST_BIN_DIR)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
