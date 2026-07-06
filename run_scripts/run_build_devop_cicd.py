"""
run_scripts.run_build_devop_cicd — DevOps/CI-CD quality gate runner.

WHAT: Standalone build script that executes the project's DevOps quality gates:
      pre-commit hook suite and pyright/mypy static type-checking. Returns a
      combined exit code (0 = all gates passed, non-zero = at least one failed).

WHY:  A scriptable CI-CD quality runner enables the same gate checks to be
      triggered identically from developer machines, GitHub Actions, and other
      CI environments. Encoding gate commands here prevents drift between local
      and remote execution.

HOW:  1. _find_project_root() locates project root via marker files.
      2. run_pre_commit() invokes pre-commit run --all-files.
      3. run_type_check() invokes pyright (or mypy as fallback) on source dir.
      4. main() calls both; returns 1 if either fails, 0 if both pass.
      5. if __name__ == "__main__" guard delegates to main() with sys.exit().

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT     Override auto-detected project root.
    RUN_SCRIPTS_PRE_COMMIT_CONFIG Pre-commit config path (default: <root>/.pre-commit-config.yaml).
    RUN_SCRIPTS_SOURCE_NAME      Python package folder name (default: root folder name).
    RUN_SCRIPTS_SOURCE_DIR       Absolute path to source (default: <root>/<source-name>).
    RUN_SCRIPTS_SKIP_PRE_COMMIT  Set to "1" to skip pre-commit gate.
    RUN_SCRIPTS_SKIP_TYPE_CHECK  Set to "1" to skip type-check gate.

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_devop_cicd.py)
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

_SOURCE_NAME: str = os.environ.get("RUN_SCRIPTS_SOURCE_NAME", _PROJECT_ROOT.name)
_SOURCE_DIR: str = os.environ.get(
    "RUN_SCRIPTS_SOURCE_DIR", str(_PROJECT_ROOT / _SOURCE_NAME)
)
_PRE_COMMIT_CONFIG: str = os.environ.get(
    "RUN_SCRIPTS_PRE_COMMIT_CONFIG",
    str(_PROJECT_ROOT / ".pre-commit-config.yaml"),
)
_SKIP_PRE_COMMIT: bool = os.environ.get("RUN_SCRIPTS_SKIP_PRE_COMMIT", "0") == "1"
_SKIP_TYPE_CHECK: bool = os.environ.get("RUN_SCRIPTS_SKIP_TYPE_CHECK", "0") == "1"
_PYTHON_EXECUTABLE: str = sys.executable
_PYTHONPATH_ENV: dict[str, str] = {**dict(os.environ), "PYTHONPATH": str(_PROJECT_ROOT)}


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


def _pre_commit_config_present(config_path: str) -> bool:
    """Return True if the pre-commit config file exists. Pure.

    WHAT: Checks pre-commit config file presence.
    WHY:  Enables graceful skip when project has no pre-commit config.
    HOW:  Path.exists(). O(1).
    INPUTS:  config_path (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(config_path):
        raise TypeError(f"config_path must be non-empty str")
    return Path(config_path).exists()


# ---------------------------------------------------------------------------
# Availability checks
# ---------------------------------------------------------------------------


def _check_pre_commit_available() -> bool:  # IMPURE
    """Return True if pre-commit CLI is on PATH. # IMPURE.

    WHAT: Attempts 'pre-commit --version' to detect pre-commit.
    WHY:  Graceful detection prevents misleading CI failure when absent.
    HOW:  subprocess.run() with captured output.
    OUTPUTS: bool.
    """
    result = subprocess.run(  # IMPURE
        ["pre-commit", "--version"], capture_output=True
    )
    return result.returncode == 0


def _check_pyright_available(python_exe: str) -> bool:  # IMPURE
    """Return True if pyright is importable. # IMPURE.

    WHAT: Attempts 'python -m pyright --version'.
    WHY:  Graceful detection prevents pipeline failure when pyright absent.
    HOW:  subprocess.run() with captured output.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "pyright", "--version"], capture_output=True
    )
    return result.returncode == 0


def _check_mypy_available(python_exe: str) -> bool:  # IMPURE
    """Return True if mypy is importable. # IMPURE.

    WHAT: Attempts 'python -m mypy --version'.
    WHY:  Used as fallback if pyright is absent.
    HOW:  subprocess.run() with captured output.
    INPUTS:  python_exe (str).
    OUTPUTS: bool.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    result = subprocess.run(  # IMPURE
        [python_exe, "-m", "mypy", "--version"], capture_output=True
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def run_pre_commit(config_path: str) -> int:  # IMPURE
    """Run pre-commit hooks against all files. Returns exit code. # IMPURE.

    WHAT: Invokes 'pre-commit run --all-files --config <config_path>'.
    WHY:  Subprocess invocation matches git hook exactly (REQ-FP-01).
    HOW:  Checks config existence and CLI availability; falls back to skip.
    INPUTS:  config_path (str) — path to .pre-commit-config.yaml.
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(config_path):
        raise TypeError("config_path must be non-empty str")
    if not _pre_commit_config_present(config_path):
        print(f"[run_build_devop_cicd] no pre-commit config at {config_path} — skipping.")  # IMPURE
        return 0
    if not _check_pre_commit_available():  # IMPURE
        print("[run_build_devop_cicd] pre-commit not available — skipping.")  # IMPURE
        return 0
    print(f"[run_build_devop_cicd] running pre-commit --all-files")  # IMPURE
    result = subprocess.run(  # IMPURE
        ["pre-commit", "run", "--all-files", "--config", config_path],
        cwd=str(_PROJECT_ROOT),
        env=_PYTHONPATH_ENV,
    )
    return result.returncode


def run_type_check(python_exe: str, source_dir: str) -> int:  # IMPURE
    """Run pyright (or mypy fallback) on source_dir. Returns exit code. # IMPURE.

    WHAT: Invokes pyright or mypy for static type analysis.
    WHY:  Type checking catches class of bugs invisible to tests (REQ-FP-01).
    HOW:  Prefers pyright; falls back to mypy; skips if neither available or
          source directory absent.
    INPUTS:  python_exe (str), source_dir (str).
    OUTPUTS: int — exit code.
    """
    if _is_bad_str(python_exe):
        raise TypeError("python_exe must be non-empty str")
    if not Path(source_dir).is_dir():
        print(f"[run_build_devop_cicd] source dir absent: {source_dir} — skipping type check.")  # IMPURE
        return 0
    if _check_pyright_available(python_exe):  # IMPURE
        tool_cmd = [python_exe, "-m", "pyright", source_dir]
        tool_name = "pyright"
    elif _check_mypy_available(python_exe):  # IMPURE
        tool_cmd = [python_exe, "-m", "mypy", source_dir]
        tool_name = "mypy"
    else:
        print("[run_build_devop_cicd] neither pyright nor mypy available — skipping type check.")  # IMPURE
        return 0
    print(f"[run_build_devop_cicd] running {tool_name} on {source_dir}")  # IMPURE
    result = subprocess.run(tool_cmd, cwd=str(_PROJECT_ROOT))  # IMPURE
    return result.returncode


def main() -> int:  # IMPURE
    """Run all CI/CD quality gates. Returns combined exit code. # IMPURE.

    WHAT: Orchestrates pre-commit and type-check gates.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls run_pre_commit() and run_type_check(); returns 1 if either fails.
    OUTPUTS: int — 0 if all gates passed, 1 otherwise.
    """
    print(f"[run_build_devop_cicd] project root: {_PROJECT_ROOT}")  # IMPURE
    rc_pc = 0
    rc_tc = 0
    if not _SKIP_PRE_COMMIT:
        rc_pc = run_pre_commit(_PRE_COMMIT_CONFIG)  # IMPURE
    else:
        print("[run_build_devop_cicd] pre-commit skipped (RUN_SCRIPTS_SKIP_PRE_COMMIT=1).")  # IMPURE
    if not _SKIP_TYPE_CHECK:
        rc_tc = run_type_check(_PYTHON_EXECUTABLE, _SOURCE_DIR)  # IMPURE
    else:
        print("[run_build_devop_cicd] type check skipped (RUN_SCRIPTS_SKIP_TYPE_CHECK=1).")  # IMPURE
    return 0 if (rc_pc == 0 and rc_tc == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
