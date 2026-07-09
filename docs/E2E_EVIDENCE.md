---
title: "E2E Evidence Summary — Engineering Studio AI"
author: "Hadrian Hu"
date: "2026-07-09"
version: "1.0.0"
status: "Current"
keywords:
  - engineering-studio-ai
  - e2e
  - playwright
  - evidence
  - coverage
---

<!--
WHAT: A compact, auditable summary of the project's end-to-end (Playwright)
and unit/integration test evidence, intended for judges/reviewers who want
exact pass/fail numbers without re-running the suite themselves.
WHY: `reports/` (which holds the raw, regenerated `e2e-junit.xml`,
`coverage.json`, and `htmlcov/`) is intentionally gitignored in this repo
(`.gitignore` line 45, `[Rr][Ee][Pp][Oo][Rr][Tt][Ss]/` — regenerate locally,
never source of truth) — so this hand-authored, tracked doc under `docs/`
is the durable, committed record of the last verified run, rather than a
raw artifact that would silently disappear from version control.
HOW: Updated manually after each full regression pass (see
`scripts/pre_demo_check.py`); each entry states what was verified, what
was NOT verified (limits), and the exact source command used.
-->

# E2E Evidence Summary

## What this proves

The end-to-end suite (`tests/e2e/`) drives a **real** `uvicorn` subprocess
serving the actual FastAPI + SSE + vanilla-JS dashboard through a headless
Chromium browser (Playwright), with the pipeline itself running in **Mode
B** (`ENGINEERING_STUDIO_FAKE_PIPELINE=1` — deterministic, no live
Fireworks call) per `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` §3.2. It verifies:

- The dashboard renders its top bar, brief-input panel, and empty state in
  both Light Mode and Dark Mode (`test_dashboard_render.py`).
- The theme toggle switches correctly and persists across a page reload
  (`test_theme_toggle.py`).
- A full pipeline run — for **all 3 confirmed demo prompts**
  (`demo/demo_prompts.json`), in both themes — reaches the Quality Gate
  banner via live SSE-driven DOM updates, with per-stage output and
  download links becoming available as each stage completes
  (`test_pipeline_stream.py`).

## What this does NOT prove

- It does **not** exercise the real Fireworks AI integration (Mode A) —
  a green Mode-B run is evidence the browser/SSE/rendering contract works,
  not that the live model call path works. See `demo/run_demo_sequence.py
  --live` or `demo/playwright_demo_script.py --live` for the Mode-A path,
  which requires a valid `FIREWORKS_API_KEY`.
- It does not measure performance/load characteristics under concurrent
  runs — only single-run-at-a-time behavior.

## Last verified run

| Suite | Command | Result | Source |
|---|---|---|---|
| Unit + integration (100% coverage gate) | `pytest tests -v --tb=short` | **111 passed**, 0 failed, coverage 100.00% (640/640 statements), 0 warnings | local run, 2026-07-09 |
| End-to-end (Playwright, Mode B) | `pytest tests/e2e -v --tb=short --no-cov --junitxml=reports/e2e-junit.xml` | **17 passed**, 0 failed, 0 errors, 25.25s | local run, 2026-07-09T15:12:35-04:00, `reports/e2e-junit.xml` (gitignored, regenerate locally) |
| Lint (ruff) | `ruff check .` | Clean, 0 issues | local run, 2026-07-09 |
| Type check (mypy --strict) | `mypy src` | Clean, 0 issues | local run, 2026-07-09 |
| Security static analysis (bandit) | `bandit -r src -ll` | Clean, 0 issues | local run, 2026-07-09 |
| Dependency CVE audit (pip-audit) | `pip-audit` | Clean, 0 known vulnerabilities (own unpublished package skipped, expected) | local run, 2026-07-09 |

**Reproduce locally:** run `python scripts/pre_demo_check.py` (see
[../scripts/pre_demo_check.py](../scripts/pre_demo_check.py)) for a single
command that re-runs every row above and prints a PASS/FAIL table.

## Regenerating the raw evidence files (not committed)

`reports/coverage.json`, `reports/htmlcov/`, and `reports/e2e-junit.xml`
are regenerated locally by the commands in the table above — they are
**not** committed (see this doc's HOW note above). If you need the raw
JUnit XML or HTML coverage report for offline review, run the commands
yourself; do not expect them to already exist after a fresh `git clone`.
