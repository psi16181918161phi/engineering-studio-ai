---
title: "WISHLIST — engineering-studio-ai demo improvements for one more round"
author: "GitHub Copilot (agent session)"
date: "2026-07-09"
version: "2026.1.0.0"
status: "Draft"
confidentiality: "INTERNAL"
---

# WISHLIST — One More Round For Prototype Demonstration

## Purpose

Capture the highest-value, one-round tasks that improve live-demo reliability,
presentation clarity, and evidence quality without widening scope beyond the
 already-working pipeline/API/webapp/CLI baseline.

## Current State Snapshot (evidence)

- Core gates pass after latest CI fix: lint, strict types, security scan,
  dependency audit, and unit/integration test suite at 100% coverage.
- E2E suite is green with 17 tests (recorded in
  `reports/e2e-junit.xml`: `failures=0`, `errors=0`).
- Demo and presentation docs still have unresolved placeholders:
  `demo/demo-script.md` and `presentation/slides-outline.md`.
- One warning remains in test output: `fastapi.testclient` path emits a
  Starlette deprecation warning related to `httpx` usage.

## Wishlist Items (one-round feasible)

## W-01 — Finalize demo fallback runbook

- Why: The live demo script still has a human-input placeholder for failure mode.
- Scope:
  - Fill fallback section in `demo/demo-script.md` with a truthful, no-fabrication
    backup flow (pre-recorded run + artifact reveal + health endpoint proof).
  - Add exact operator steps and speaker lines.
- Acceptance:
  - No `[SECTION INCOMPLETE` markers remain in `demo/demo-script.md`.
  - A presenter can run fallback without ad-libbing.

## W-02 — Complete slide-outline placeholders

- Why: Pitch deck narrative still has three incomplete sections.
- Scope:
  - Fill Slide 2 (Problem), Slide 6 (AMD Ecosystem Usage), Slide 8 (Startup/Roadmap)
    in `presentation/slides-outline.md` using only already-supported claims.
- Acceptance:
  - No `[SECTION INCOMPLETE` markers remain in `presentation/slides-outline.md`.
  - Every claim is traceable to existing repo artifacts.

## W-03 — Add deterministic demo-run launcher

- Why: Rehearsal consistency improves if prompts and run order are scripted.
- Scope:
  - Add `demo/demo_prompts.json` with the confirmed software-first prompts.
  - Add `demo/run_demo_sequence.py` to execute or stage runs in a fixed order.
  - Emit timestamps and output locations for quick presenter lookup.
- Acceptance:
  - Single command prepares demo inputs deterministically.
  - Run metadata is printed and saved for handoff.

## W-04 — Strengthen e2e evidence packaging

- Why: Judges benefit from compact, auditable proof artifacts.
- Scope:
  - Add `reports/e2e/README.md` describing what e2e proves and what it does not.
  - Save a small post-run summary (`reports/e2e/summary.md`) from JUnit XML.
- Acceptance:
  - Evidence folder clearly communicates status and limits.
  - Summary references exact test counts and pass/fail values.

## W-05 — Resolve or suppress known deprecation warning safely

- Why: Warning noise can hide real regressions during final validation.
- Scope:
  - Investigate `fastapi.testclient`/Starlette warning path from current tests.
  - Prefer dependency-compatible fix; only use explicit warning filter if a safe
    upgrade path is unavailable this round.
- Acceptance:
  - Test logs are warning-clean, or warning is narrowly documented and filtered
    with justification.

## W-06 — Add pre-demo regression command

- Why: A single command lowers go-live risk before recording/presentation.
- Scope:
  - Add script target or helper command that runs:
    `ruff`, `mypy`, `bandit`, `pip-audit`, `pytest tests`, `pytest tests/e2e`.
  - Print concise PASS/FAIL table with exit status.
- Acceptance:
  - Presenter can run one command and get an explicit go/no-go result.

## Recommended One-Round Cut

Prioritize `W-01`, `W-02`, `W-03`, and `W-06` first. Add `W-04` and `W-05`
only if schedule allows after those four complete.
