---
title: "run_scripts — Project-Agnostic Python Build Pipeline"
author: "Hadrian Hu"
date: "2026-05-19"
version: "1.0.0"
keywords:
  - build-pipeline
  - ci-cd
  - agnostic
  - python
  - automation
---
# run_scripts

> A **fully project-agnostic** Python build-pipeline suite.
> Drop it anywhere. Configure via environment variables. Zero rework required.

---

## Table of Contents

1. [Abstract](#abstract)
2. [Executive Summary](#executive-summary)
3. [Architecture](#architecture)
4. [Script Inventory](#script-inventory)
5. [Environment Variable Contract](#environment-variable-contract)
6. [Usage](#usage)
7. [Copy-Paste Portability Guide](#copy-paste-portability-guide)
8. [Design Rationale](#design-rationale)

---

## Abstract

`run_scripts` is a collection of standalone Python build scripts that collectively
form a complete CI/CD pipeline — from Python version validation through venv
creation, dependency import checks, testing, type-checking, pre-commit gates,
report generation, PyPI packaging, binary compilation, and a final coverage
audit. Each script is self-contained and requires no modification to move to a
new project.

---

## Executive Summary

| Property               | Detail                                                     |
| ---------------------- | ---------------------------------------------------------- |
| Location (parent repo) | `scripts/run_scripts/`                                   |
| Python version         | 3.9+                                                       |
| Zero-config            | Yes — auto-detects project root via marker files          |
| Override mechanism     | `RUN_SCRIPTS_*` environment variables                    |
| Exit codes             | `0` = pass, non-zero = fail                              |
| Graceful degradation   | All scripts skip (return 0) when optional tools are absent |
| Coding standard        | JPL/NASA 10 FP Principles, SOLID, ACID, WHAT/WHY/HOW docs  |

---

## Architecture

```
run_scripts/
├── __init__.py                                 # Package init, version
├── __main__.py                                 # Pipeline orchestrator
├── run_py_version_check.py                     # Stage 1: Python version gate
├── run_build_venv.py                           # Stage 2: venv creation
├── run_build_import_third_party_dependencies.py # Stage 3: third-party dep check
├── run_build_import_modules.py                 # Stage 4: internal module check
├── run_build_run_tests.py                      # Stage 5: pytest + coverage
├── run_build_devop_cicd.py                     # Stage 6: pre-commit + type check
├── run_build_pipeline_reports.py               # Stage 7: HTML + JSON reports
├── run_build_pypi_package.py                   # Stage 8: build + twine check
├── run_build_python_agnostic_executables.py    # Stage 9: PyInstaller binary
├── run_build_audit_coverage.py                 # Stage 10: coverage fail-under gate
└── README.md                                   # This file
```

**Root detection** (embedded in every script, no shared import):

```python
_ROOT_MARKERS: frozenset[str] = frozenset({
    "pyproject.toml", "setup.py", "setup.cfg", ".git", "requirements.txt",
})

def _find_project_root(start: Path) -> Path:
    candidate = start.resolve()
    while candidate != candidate.parent:
        if any((candidate / m).exists() for m in _ROOT_MARKERS):
            return candidate
        candidate = candidate.parent
    return start.resolve()
```

---

## Script Inventory

| Script                                           | Stage | Purpose                                               | Optional tools                        |
| ------------------------------------------------ | ----- | ----------------------------------------------------- | ------------------------------------- |
| `run_py_version_check.py`                      | 1     | Validate Python ≥`RUN_SCRIPTS_MIN_PYTHON`          | —                                    |
| `run_build_venv.py`                            | 2     | Create `.venv` + install `requirements.txt`       | —                                    |
| `run_build_import_third_party_dependencies.py` | 3     | Import-check each requirement                         | —                                    |
| `run_build_import_modules.py`                  | 4     | Import-check internal modules                         | —                                    |
| `run_build_run_tests.py`                       | 5     | `pytest` + optional `--cov`                       | `pytest-cov`                        |
| `run_build_devop_cicd.py`                      | 6     | `pre-commit run --all-files` + `pyright`/`mypy` | `pre-commit`, `pyright`, `mypy` |
| `run_build_pipeline_reports.py`                | 7     | `coverage html` + `coverage json`                 | `coverage`                          |
| `run_build_pypi_package.py`                    | 8     | `python -m build` + `twine check`                 | `build`, `twine`                  |
| `run_build_python_agnostic_executables.py`     | 9     | `PyInstaller --onefile` binary                      | `PyInstaller`                       |
| `run_build_audit_coverage.py`                  | 10    | `coverage report --fail-under` gate                 | `coverage`                          |

---

## Environment Variable Contract

All variables are **optional**. Sensible defaults are computed from the
auto-detected project root.

| Variable                           | Default                            | Description                                 |
| ---------------------------------- | ---------------------------------- | ------------------------------------------- |
| `RUN_SCRIPTS_PROJECT_ROOT`       | auto-detected                      | Override project root path                  |
| `RUN_SCRIPTS_SOURCE_NAME`        | `<root-folder-name>`             | Python package folder name                  |
| `RUN_SCRIPTS_SOURCE_DIR`         | `<root>/<source-name>`           | Absolute path to source package             |
| `RUN_SCRIPTS_TEST_DIR`           | `<root>/tests`                   | Test directory                              |
| `RUN_SCRIPTS_COVERAGE_THRESHOLD` | `80`                             | Minimum coverage % (0–100)                 |
| `RUN_SCRIPTS_VENV_DIR`           | `<root>/.venv`                   | Virtual environment directory               |
| `RUN_SCRIPTS_REQUIREMENTS_FILE`  | `<root>/requirements.txt`        | Requirements file path                      |
| `RUN_SCRIPTS_DIST_DIR`           | `<root>/dist`                    | PyPI distribution output                    |
| `RUN_SCRIPTS_DIST_BIN_DIR`       | `<root>/dist_bin`                | Standalone binary output                    |
| `RUN_SCRIPTS_EXECUTABLE_NAME`    | `<root-folder-name>`             | Binary name                                 |
| `RUN_SCRIPTS_REPORTS_DIR`        | `<root>/markdowns/reports`       | Coverage report output directory            |
| `RUN_SCRIPTS_COVERAGE_DATA`      | `<root>/.coverage`               | Coverage data file                          |
| `RUN_SCRIPTS_PRE_COMMIT_CONFIG`  | `<root>/.pre-commit-config.yaml` | Pre-commit config path                      |
| `RUN_SCRIPTS_MODULES`            | auto-discovered                    | Comma-separated internal module list        |
| `RUN_SCRIPTS_ENTRY_SCRIPT`       | auto-detected `__main__.py`      | CLI entry-point script                      |
| `RUN_SCRIPTS_MIN_PYTHON`         | `"3,9"`                          | Minimum Python version as `"major,minor"` |
| `RUN_SCRIPTS_STOP_ON_FAIL`       | `"1"`                            | Set `"0"` to continue past stage failures |
| `RUN_SCRIPTS_SKIP_PRE_COMMIT`    | `"0"`                            | Set `"1"` to skip pre-commit gate         |
| `RUN_SCRIPTS_SKIP_TYPE_CHECK`    | `"0"`                            | Set `"1"` to skip type-check gate         |
| `RUN_SCRIPTS_SKIP_TWINE`         | `"0"`                            | Set `"1"` to skip twine check             |

---

## Usage

### Run the full pipeline

```bash
python -m run_scripts
```

### Run a single stage

```bash
python run_py_version_check.py
python run_build_venv.py
python run_build_run_tests.py
# ... etc
```

### Override project root (e.g. running from a subdirectory)

```bash
RUN_SCRIPTS_PROJECT_ROOT=/path/to/myproject python -m run_scripts
```

### Lower the coverage threshold for a legacy project

```bash
RUN_SCRIPTS_COVERAGE_THRESHOLD=60 python run_build_audit_coverage.py
```

### Skip optional gates

```bash
RUN_SCRIPTS_SKIP_PRE_COMMIT=1 RUN_SCRIPTS_SKIP_TWINE=1 python -m run_scripts
```

### Continue pipeline past failures (collect all failures)

```bash
RUN_SCRIPTS_STOP_ON_FAIL=0 python -m run_scripts
```

### Specify a non-standard source package name

```bash
RUN_SCRIPTS_SOURCE_NAME=my_app python -m run_scripts
```

---

## Copy-Paste Portability Guide

These scripts are designed to be **copied verbatim** into any project.
No modification is required.

**Steps:**

1. Copy the entire `run_scripts/` directory into your project:

   ```bash
   cp -r run_scripts/ /path/to/target-project/scripts/run_scripts/
   ```
2. The scripts auto-detect the project root from marker files
   (`pyproject.toml`, `setup.py`, `.git`, etc.).
3. Run immediately:

   ```bash
   cd /path/to/target-project
   python -m scripts.run_scripts
   ```

   or add `scripts/` to `PYTHONPATH` and run `python -m run_scripts`.
4. Optionally create a `.env` or CI YAML setting `RUN_SCRIPTS_*` variables
   to customise thresholds, paths, or stage skips.

**No rework is needed.** If a required tool (pytest, PyInstaller, etc.) is not
installed, the corresponding stage skips gracefully and returns exit code 0.

---

## Design Rationale

### Functional Programming (REQ-FP-01, REQ-FP-04)

1. All I/O operations are isolated in functions labelled `# IMPURE`
1. Pure helpers are free of side effects and directly unit-testable
1. Module-level constants use `frozenset` and `Final` where applicable

### No Hardcoded Paths (G-06)

1. `_find_project_root()` is embedded in every script (not imported) so each
   script is completely standalone
1. All paths derive from the auto-detected or overridden project root

### Callable Standalone (G-07)

1. Every script has `if __name__ == "__main__": sys.exit(main())`
1. Every script can be invoked as `python <script>.py` OR via the package
   runner `python -m run_scripts`

### SOLID

1. **SRP**: Each script handles exactly one pipeline concern
1. **OCP**: New stages are added by creating a new script and appending to
   `_STAGES` in `__main__.py`
1. **DIP**: Scripts depend on environment variable contracts, not concrete
   project layouts

### WHAT/WHY/HOW

Every module, class, and function carries WHAT/WHY/HOW docstring headers as
mandated by the project's documentation coding standards.
