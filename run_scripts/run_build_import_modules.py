"""
run_scripts.run_build_import_modules — Internal module import validator.

WHAT: Standalone build script that validates all internal Python modules are
      importable. Auto-discovers modules from the source directory or reads
      them from the RUN_SCRIPTS_MODULES environment variable. Reports PASS/FAIL
      per module and returns a non-zero exit code if any import fails.

WHY:  Ensures all internally built modules and their components are importable,
      correctly structured, and compliant with project architecture standards.
      Broken imports discovered early prevent hard-to-diagnose runtime failures.

HOW:  1. _find_project_root() locates project root via marker files.
      2. Source directory is auto-detected or read from RUN_SCRIPTS_SOURCE_DIR.
      3. Module list is read from RUN_SCRIPTS_MODULES (comma-separated) or
         auto-discovered by walking the source directory for *.py files.
      4. Each module is imported; ImportError/AttributeError are caught.
      5. Results are printed and exit code returned.

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT  Override auto-detected project root.
    RUN_SCRIPTS_SOURCE_NAME   Python package folder name (default: root folder name).
    RUN_SCRIPTS_SOURCE_DIR    Absolute path to source (default: <root>/<source-name>).
    RUN_SCRIPTS_MODULES       Comma-separated module list (default: auto-discovered).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_import_modules.py)
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import NamedTuple

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
_MODULES_ENV: str = os.environ.get("RUN_SCRIPTS_MODULES", "")
_PASS: str = "PASS"
_FAIL: str = "FAIL"
_SKIP: str = "SKIP"


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


class ImportResult(NamedTuple):
    """Immutable result record for a single module import attempt.

    WHAT: Holds module name, success flag, and error message if any.
    WHY:  Named tuple keeps results pure/immutable and self-documenting.
    HOW:  Constructed by attempt_import(); consumed by report_results().
    Attributes:
        module_name (str): Fully-qualified module name.
        success (bool): True if import succeeded.
        error (str): Error message or empty string.
    """

    module_name: str
    success: bool
    error: str


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


def _path_to_module_name(py_file: Path, source_root: Path) -> str:
    """Convert a .py file path to a dotted module name. Pure.

    WHAT: Translates filesystem path to importable module name.
    WHY:  Enables auto-discovery of modules without a manifest.
    HOW:  Relative path from source_root; replaces os.sep with '.';
          strips .py suffix; strips __init__ suffix.
    INPUTS:  py_file (Path), source_root (Path).
    OUTPUTS: str — dotted module name.
    """
    rel = py_file.relative_to(source_root.parent)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _discover_modules(source_dir: str) -> list[str]:
    """Auto-discover Python modules under source_dir. Pure-ish.

    WHAT: Walks source_dir to find all *.py files and converts to module names.
    WHY:  Removes need for a hardcoded module manifest (agnostic design).
    HOW:  Path.rglob("*.py"); converts each via _path_to_module_name.
    INPUTS:  source_dir (str).
    OUTPUTS: list[str] — sorted list of dotted module names.
    """
    source_path = Path(source_dir)
    if not source_path.is_dir():
        return []
    modules = []
    for py_file in sorted(source_path.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        mod = _path_to_module_name(py_file, source_path)
        if mod:
            modules.append(mod)
    return modules


def _parse_modules_env(env_val: str) -> list[str]:
    """Parse comma-separated module names from env var. Pure.

    WHAT: Splits and strips module names from RUN_SCRIPTS_MODULES.
    WHY:  Pure parsing extracted to isolate env var handling.
    HOW:  str.split(",") + strip + filter empty.
    INPUTS:  env_val (str).
    OUTPUTS: list[str].
    """
    return [m.strip() for m in env_val.split(",") if m.strip()]


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def attempt_import(module_name: str, project_root: Path) -> ImportResult:  # IMPURE
    """Attempt to import module_name; return ImportResult. # IMPURE.

    WHAT: Imports the named module; catches ImportError and exceptions.
    WHY:  Each import attempt is isolated to prevent one failure cascading.
    HOW:  Adds project_root to sys.path if absent; calls importlib.import_module.
    INPUTS:  module_name (str), project_root (Path).
    OUTPUTS: ImportResult.
    """
    if _is_bad_str(module_name):
        raise TypeError(f"module_name must be non-empty str")
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)  # IMPURE
    try:
        importlib.import_module(module_name)  # IMPURE
        return ImportResult(module_name=module_name, success=True, error="")
    except ImportError as exc:
        return ImportResult(module_name=module_name, success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return ImportResult(module_name=module_name, success=False, error=f"{type(exc).__name__}: {exc}")


def report_results(results: list[ImportResult]) -> int:  # IMPURE
    """Print results table and return exit code. # IMPURE.

    WHAT: Prints PASS/FAIL for each module and a summary line.
    WHY:  Centralises output formatting so attempt_import() stays pure-ish.
    HOW:  Iterates results; counts failures; prints; returns 0 or 1.
    INPUTS:  results (list[ImportResult]).
    OUTPUTS: int — 0 if all passed, 1 if any failed.
    """
    failures = 0
    for r in results:
        status = _PASS if r.success else _FAIL
        suffix = f" — {r.error}" if r.error else ""
        print(f"  [{status}] {r.module_name}{suffix}")  # IMPURE
        if not r.success:
            failures += 1
    total = len(results)
    print(f"\n[run_build_import_modules] {total - failures}/{total} modules OK.")  # IMPURE
    return 0 if failures == 0 else 1


def main() -> int:  # IMPURE
    """Validate internal module imports. Returns exit code. # IMPURE.

    WHAT: Discovers or reads module list; attempts each import; reports results.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Resolves module list; calls attempt_import() per module; calls
          report_results(); returns exit code.
    OUTPUTS: int — 0 if all imports succeeded, 1 otherwise.
    """
    print(f"[run_build_import_modules] project root:  {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_import_modules] source dir:    {_SOURCE_DIR}")  # IMPURE

    if not Path(_SOURCE_DIR).is_dir():
        print(f"[run_build_import_modules] source dir absent — skipping.")  # IMPURE
        return 0

    modules: list[str] = (
        _parse_modules_env(_MODULES_ENV)
        if _MODULES_ENV
        else _discover_modules(_SOURCE_DIR)
    )

    if not modules:
        print("[run_build_import_modules] no modules found — skipping.")  # IMPURE
        return 0

    print(f"[run_build_import_modules] {len(modules)} module(s) to validate:")  # IMPURE
    results = [attempt_import(m, _PROJECT_ROOT) for m in modules]  # IMPURE
    return report_results(results)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
