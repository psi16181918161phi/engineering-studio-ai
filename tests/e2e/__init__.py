"""WHAT: End-to-end (Playwright) test package for the command-and-control
webapp. WHY: Kept separate from `tests/` unit suite — these tests drive a
real subprocess server, not just importable statements, and are
intentionally excluded from the 100%-statement coverage gate (see
`pyproject.toml`'s `--ignore=tests/e2e`). HOW: run via
`pytest tests/e2e -v --tb=short --no-cov` (requires the `e2e` optional
dependency group: `pip install -e ".[e2e]"` then
`playwright install chromium`).
"""
