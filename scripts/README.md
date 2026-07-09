# scripts/ — Local developer utilities

WHAT: Small, standalone operational scripts that don't belong to any
single Role's ownership zone (see `../SCAFFOLDING.md` §2).
WHY: Keeps one-off developer/presenter tooling out of `src/` (the shipped
package) and `run_scripts/` (the project-agnostic build-pipeline suite),
while still being easy to find and run.
HOW: Run scripts directly with `python scripts/<name>.py` from the repo
root (or `.[e2e]`/`.[gui]` venv active, as needed per script).

## Files in this folder

| File | Purpose |
|---|---|
| `pre_demo_check.py` | Single-command pre-demo regression gate: runs ruff, mypy --strict, bandit, pip-audit, the unit/integration suite (100% coverage gate), and the Playwright e2e suite, in the same order as `.github/workflows/ci.yml`, then prints a PASS/FAIL summary table and returns a go/no-go exit code. Run with `python scripts/pre_demo_check.py` (add `--skip-e2e` to skip the browser suite). |
