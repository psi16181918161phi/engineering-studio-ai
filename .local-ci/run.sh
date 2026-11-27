#!/usr/bin/env bash
# WHAT: Local CI recipe for git-autosync (commit status context local-ci/wsl).
# WHY:  The built-in Python recipe runs python:3.12-slim, but pyproject.toml requires
#       Python >= 3.14, so every job failed at `pip install`. A .local-ci/run.sh opts
#       this repository out of the built-in recipes and runs in the image named in
#       .local-ci/image (python:3.14.10-slim).
# HOW:  The same checks as the `test` job of .github/workflows/ci.yml (kept as a
#       reference; GitHub Actions stays disabled) plus the mutation gate from the
#       README "Local CI" section, in order, stopping at the first failure:
#         install -> ruff -> mypy -> bandit -> pip-audit -> pytest (100% line and
#         branch coverage) -> mutation gate.
#       Not run here: the Playwright e2e tests (tests/e2e), which need a browser
#       installed with system packages; run them locally as the README describes.
#       Needs network for pip and pip-audit. No secrets are used: tests run with
#       the mocked pipeline and make no live API calls.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s\n' "$1"; }

step "python"
python --version

step "install"
python -m pip install -q --root-user-action=ignore --upgrade pip setuptools wheel
python -m pip install -q --root-user-action=ignore -e ".[gui]"
python -m pip install -q --root-user-action=ignore -r requirements-dev.txt

step "ruff"
ruff check .

step "mypy"
mypy src

step "bandit"
bandit -q -r src -ll

step "pip-audit"
pip-audit

step "pytest"
python -m pytest --cov-branch

step "mutation"
mkdir -p .local-ci/out
python scripts/local_mutation_gate.py --report .local-ci/out/mutation.json

step "done"
