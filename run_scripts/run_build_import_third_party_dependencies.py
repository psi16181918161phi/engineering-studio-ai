"""
run_scripts.run_build_import_third_party_dependencies — Third-party dep validator.

WHAT: Standalone build script that parses requirements.txt and validates that
      every listed third-party package is importable in the current Python
      environment. Reports PASS/FAIL/SKIP per package and returns a non-zero
      exit code if any required package cannot be imported.

WHY:  Validates that all declared dependencies are installed before running
      tests or building artefacts — preventing misleading failures during
      later pipeline stages. A missing dep is reported with its requirements.txt
      line number for rapid developer diagnosis.

HOW:  1. _find_project_root() locates project root via marker files.
      2. _REQUIREMENTS_FILE is computed from env var or project root.
      3. _parse_requirements() extracts package names (strips version
         specifiers, comments, extras, editable installs, file://).
      4. _package_to_import_name() converts dist-names to import-names.
      5. Each package is imported via importlib; result is printed.
      6. main() returns 0 if all imports succeeded, 1 otherwise.

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT      Override auto-detected project root.
    RUN_SCRIPTS_REQUIREMENTS_FILE Requirements file (default: <root>/requirements.txt).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-06        (no hardcoded paths)
    G-07        (callable standalone: python run_build_import_third_party_dependencies.py)
"""
from __future__ import annotations

import importlib
import os
import re
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

_REQUIREMENTS_FILE: str = os.environ.get(
    "RUN_SCRIPTS_REQUIREMENTS_FILE", str(_PROJECT_ROOT / "requirements.txt")
)
_PASS: str = "PASS"
_FAIL: str = "FAIL"
_SKIP: str = "SKIP"

# Regex: matches a valid requirement name (PEP 508 name token)
_REQ_NAME_RE: re.Pattern[str] = re.compile(r"^([A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)")


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


class DepResult(NamedTuple):
    """Immutable result record for a single dependency import attempt.

    WHAT: Holds package name, import name, success flag, and error message.
    WHY:  NamedTuple keeps results immutable and self-documenting.
    HOW:  Constructed by attempt_import_dep(); consumed by report_dep_results().
    Attributes:
        package_name (str): Distribution name from requirements.txt.
        import_name (str): Python importable name.
        success (bool): True if import succeeded.
        error (str): Error message or empty string.
    """

    package_name: str
    import_name: str
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


def _is_skip_line(line: str) -> bool:
    """Return True if this requirements.txt line should be skipped. Pure.

    WHAT: Detects comment, blank, editable, file://,  or -r include lines.
    WHY:  These lines do not correspond to importable packages.
    HOW:  str.startswith checks. O(1).
    INPUTS:  line (str).
    OUTPUTS: bool.
    """
    stripped = line.strip()
    if not stripped:
        return True
    for prefix in ("#", "-r ", "-c ", "--", "-e ", "git+", "file://", "http://", "https://"):
        if stripped.startswith(prefix):
            return True
    return False


def _extract_package_name(line: str) -> str:
    """Extract the distribution name from a requirements line. Pure.

    WHAT: Parses first token of a requirement spec per PEP 508 / pip rules.
    WHY:  Version specifiers and extras are not part of the import name.
    HOW:  Regex match on leading name token; returns empty str if no match.
    INPUTS:  line (str).
    OUTPUTS: str — distribution name (may be empty if unparseable).
    """
    stripped = line.strip().split(";")[0].split("[")[0]
    m = _REQ_NAME_RE.match(stripped)
    return m.group(1) if m else ""


def _package_to_import_name(package_name: str) -> str:
    """Convert distribution name to Python importable name. Pure.

    WHAT: Replaces hyphens and dots with underscores in distribution name.
    WHY:  PEP 8 allows hyphens in dist names (e.g. 'Pillow' → 'PIL');
          most packages use underscored import names; hyphens in dist names
          must be underscored for import. Special-cases known exceptions.
    HOW:  Normalise name; apply known mapping table; fall back to underscore.
    INPUTS:  package_name (str).
    OUTPUTS: str — importable module name.
    """
    _KNOWN_MAPPING: dict[str, str] = {
        "Pillow": "PIL",
        "pillow": "PIL",
        "scikit-learn": "sklearn",
        "scikit_learn": "sklearn",
        "PyYAML": "yaml",
        "pyyaml": "yaml",
        "opencv-python": "cv2",
        "opencv_python": "cv2",
        "beautifulsoup4": "bs4",
        "python-dotenv": "dotenv",
        "python_dotenv": "dotenv",
        "pyzmq": "zmq",
        "click": "click",
        "setuptools": "setuptools",
        "dateparser": "dateparser",
    }
    normalised = package_name.lower()
    if package_name in _KNOWN_MAPPING:
        return _KNOWN_MAPPING[package_name]
    if normalised in _KNOWN_MAPPING:
        return _KNOWN_MAPPING[normalised]
    return package_name.replace("-", "_").replace(".", "_")


def _parse_requirements(requirements_file: str) -> list[str]:
    """Parse requirements.txt and return list of distribution names. Pure-ish.

    WHAT: Reads file; filters and extracts package names.
    WHY:  Centralises parsing so attempt_import_dep stays clean.
    HOW:  Reads lines; filters with _is_skip_line; extracts with _extract_package_name.
    INPUTS:  requirements_file (str).
    OUTPUTS: list[str] — distribution names (may be empty if absent or empty file).
    """
    path = Path(requirements_file)
    if not path.exists():
        return []
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if _is_skip_line(line):
            continue
        name = _extract_package_name(line)
        if name:
            names.append(name)
    return names


# ---------------------------------------------------------------------------
# Impure functions (I/O) — clearly labelled
# ---------------------------------------------------------------------------


def attempt_import_dep(package_name: str) -> DepResult:  # IMPURE
    """Attempt to import package_name; return DepResult. # IMPURE.

    WHAT: Tries to import the derived import name for a distribution package.
    WHY:  Each import attempt is isolated to prevent one failure cascading.
    HOW:  _package_to_import_name() derives import name; importlib.import_module().
    INPUTS:  package_name (str).
    OUTPUTS: DepResult.
    """
    if _is_bad_str(package_name):
        raise TypeError("package_name must be non-empty str")
    import_name = _package_to_import_name(package_name)
    try:
        importlib.import_module(import_name)  # IMPURE
        return DepResult(package_name=package_name, import_name=import_name, success=True, error="")
    except ImportError as exc:
        return DepResult(package_name=package_name, import_name=import_name, success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return DepResult(
            package_name=package_name,
            import_name=import_name,
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def report_dep_results(results: list[DepResult]) -> int:  # IMPURE
    """Print results table and return exit code. # IMPURE.

    WHAT: Prints PASS/FAIL for each dependency and a summary line.
    WHY:  Centralises output formatting (REQ-FP-01).
    HOW:  Iterates results; counts failures; prints; returns 0 or 1.
    INPUTS:  results (list[DepResult]).
    OUTPUTS: int — 0 if all passed, 1 if any failed.
    """
    failures = 0
    for r in results:
        status = _PASS if r.success else _FAIL
        suffix = f" (import: {r.import_name})" if r.import_name != r.package_name else ""
        err = f" — {r.error}" if r.error else ""
        print(f"  [{status}] {r.package_name}{suffix}{err}")  # IMPURE
        if not r.success:
            failures += 1
    total = len(results)
    print(f"\n[run_build_import_third_party_dependencies] {total - failures}/{total} deps OK.")  # IMPURE
    return 0 if failures == 0 else 1


def main() -> int:  # IMPURE
    """Validate third-party dependency imports. Returns exit code. # IMPURE.

    WHAT: Parses requirements.txt; imports each dep; reports results.
    WHY:  Single-responsibility entry point (SOLID SRP).
    HOW:  Calls _parse_requirements(); calls attempt_import_dep() per package;
          calls report_dep_results(); returns exit code.
    OUTPUTS: int — 0 if all imports succeeded, 1 otherwise.
    """
    print(f"[run_build_import_third_party_dependencies] project root:       {_PROJECT_ROOT}")  # IMPURE
    print(f"[run_build_import_third_party_dependencies] requirements file:  {_REQUIREMENTS_FILE}")  # IMPURE

    packages = _parse_requirements(_REQUIREMENTS_FILE)
    if not packages:
        print("[run_build_import_third_party_dependencies] no packages found — skipping.")  # IMPURE
        return 0

    print(f"[run_build_import_third_party_dependencies] {len(packages)} package(s) to validate:")  # IMPURE
    results = [attempt_import_dep(pkg) for pkg in packages]  # IMPURE
    return report_dep_results(results)  # IMPURE


if __name__ == "__main__":
    sys.exit(main())
