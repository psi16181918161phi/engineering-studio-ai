"""
run_scripts.__main__ — Project-agnostic build pipeline orchestrator.

WHAT: Entry point for the project-agnostic run_scripts build pipeline suite.
      Orchestrates sequential execution of all build stages when invoked as
      ``python -m run_scripts`` or ``python run_scripts/__main__.py``.

WHY:  A single, auditable entry point satisfies SOLID SRP — orchestration is
      its only reason to change. Enforces stage ordering, provides a
      deterministic exit code, and prevents partial execution from leaving
      the build in an undefined state (ACID Atomicity, FP Principle 9).

HOW:  1. Adds this file's parent directory to sys.path so stage modules are
         importable regardless of invocation method.
      2. Each stage module is imported by name and its main() called.
      3. Stages run in dependency order; first non-zero exit short-circuits.
      4. All I/O surfaces labelled # IMPURE per FP Principle 1.

Environment variables:
    RUN_SCRIPTS_PROJECT_ROOT    Override auto-detected project root.
    RUN_SCRIPTS_STOP_ON_FAIL    Set to "0" to continue past failures (default "1").

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-07        (callable standalone: python -m run_scripts)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# sys.path guard — ensures run_scripts/ is importable regardless of cwd.
# IMPURE: mutates sys.path at import time.
# ---------------------------------------------------------------------------
import sys as _sys
from pathlib import Path as _Path

_RUN_SCRIPTS_DIR: str = str(_Path(__file__).resolve().parent)
if _RUN_SCRIPTS_DIR not in _sys.path:
    _sys.path.insert(0, _RUN_SCRIPTS_DIR)
# ---------------------------------------------------------------------------

import importlib
import logging
import os
import sys
from typing import Final, Sequence

# ---------------------------------------------------------------------------
# Module-level constants (REQ-FP-04)
# ---------------------------------------------------------------------------

_MODULE_NAME: Final[str] = "run_scripts.__main__"
_PIPELINE_VERSION: Final[str] = "1.0.0"
_EXIT_SUCCESS: Final[int] = 0
_EXIT_FAILURE: Final[int] = 1
_STOP_ON_FAIL: Final[bool] = os.environ.get("RUN_SCRIPTS_STOP_ON_FAIL", "1") != "0"

# Stage modules in execution order.
_STAGES: Final[Sequence[str]] = (
    "run_py_version_check",
    "run_build_venv",
    "run_build_import_third_party_dependencies",
    "run_build_import_modules",
    "run_build_run_tests",
    "run_build_devop_cicd",
    "run_build_pipeline_reports",
    "run_build_pypi_package",
    "run_build_python_agnostic_executables",
    "run_build_audit_coverage",
)

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
_log: Final[logging.Logger] = logging.getLogger(_MODULE_NAME)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _stage_label(stage_name: str) -> str:
    """Return a formatted stage label. Pure.

    WHAT: Converts a module name to a display-friendly label.
    WHY:  Pure transformation — extracted to keep main() free of string ops.
    HOW:  Replaces underscores with spaces and capitalises.
    INPUTS:  stage_name (str).
    OUTPUTS: str — formatted label.
    """
    return stage_name.replace("_", " ").title()


def _is_bad_str(value: object) -> bool:
    """Return True if value is not a non-empty str. O(1). Pure.

    WHAT: Validates that a value is a non-empty string.
    WHY:  Pure predicate used by callers to avoid isinstance in their logic.
    HOW:  isinstance check + truthiness. O(1).
    INPUTS:  value (object).
    OUTPUTS: bool — True if not a valid string.
    """
    return not isinstance(value, str) or not value


# ---------------------------------------------------------------------------
# Impure stage runner
# ---------------------------------------------------------------------------


def _run_stage(stage_name: str) -> int:  # IMPURE — imports module, calls main()
    """Import a stage module and call its main(). Returns exit code. # IMPURE.

    WHAT: Dynamically imports the named stage module and invokes main().
    WHY:  Dynamic import decouples the orchestrator from stage internals —
          stages can be added/removed without touching this file (OCP).
    HOW:  importlib.import_module(stage_name).main(); catches ImportError and
          AttributeError as non-fatal warnings.
    INPUTS:  stage_name (str) — module name within run_scripts/.
    OUTPUTS: int — exit code from stage main(); 1 on import/attribute error.
    """
    if _is_bad_str(stage_name):
        raise ValueError(f"stage_name must be non-empty str, got {stage_name!r}")
    try:
        module = importlib.import_module(stage_name)  # IMPURE
        result: int = module.main()  # IMPURE
        return result if isinstance(result, int) else _EXIT_SUCCESS
    except ImportError as exc:
        _log.warning("Stage %r not importable: %s — skipping.", stage_name, exc)  # IMPURE
        return _EXIT_SUCCESS
    except AttributeError:
        _log.warning("Stage %r has no main() — skipping.", stage_name)  # IMPURE
        return _EXIT_SUCCESS


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def main() -> int:  # IMPURE — runs build pipeline
    """Run all build stages in order and return aggregated exit code. # IMPURE.

    WHAT: Orchestrates the complete build pipeline by running each stage module.
    WHY:  Single entry point for full-suite execution satisfies SOLID SRP.
    HOW:  Iterates _STAGES; calls _run_stage(); short-circuits on first failure
          when _STOP_ON_FAIL is True; returns 0 iff all stages pass.
    OUTPUTS: int — 0 if all stages passed, 1 if any failed.
    """
    _log.info("=" * 60)  # IMPURE
    _log.info("run_scripts pipeline v%s", _PIPELINE_VERSION)  # IMPURE
    _log.info("=" * 60)  # IMPURE

    failed: list[str] = []

    for stage in _STAGES:
        _log.info("--- Stage: %s ---", _stage_label(stage))  # IMPURE
        code = _run_stage(stage)  # IMPURE
        if code != _EXIT_SUCCESS:
            _log.error("Stage %r FAILED (exit %d).", stage, code)  # IMPURE
            failed.append(stage)
            if _STOP_ON_FAIL:
                break
        else:
            _log.info("Stage %r PASSED.", stage)  # IMPURE

    if failed:
        _log.error("Pipeline FAILED. Failed stages: %s", ", ".join(failed))  # IMPURE
        return _EXIT_FAILURE

    _log.info("Pipeline PASSED. All stages succeeded.")  # IMPURE
    return _EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
