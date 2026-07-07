---
title: "PLAN — Playwright Integration for Engineering Studio AI Webapp Demonstration"
author: "Hadrian Hu"
date: "2026-07-07"
version: "2026.1.0.0"
status: "PLANNING_ONLY — not yet implemented"
keywords:
  - engineering-studio-ai
  - playwright
  - e2e
  - webapp
  - demo-automation
  - plan
---

<!--
WHAT: A planning-only document for integrating Playwright end-to-end
browser testing/demonstration against the W6a webapp (engineering_studio.webapp).
WHY: The user asked to "plan for the latter of how to integrate playwright"
— explicitly a planning request, not an implementation request, this
session. No Playwright test files, fixtures, or CI jobs are added yet.
HOW: This document is the artifact a future EXECUTE-phase session
consumes to actually add the described tests/fixtures/CI job.
-->

# PLAN — Playwright Integration

## 1. Scope and Non-Goals

**In scope (this document):** a concrete, reviewable plan for adding
Playwright-driven browser tests/demonstration scripts against the W6a
webapp.

**Explicitly out of scope (not done this session):** installing the
`playwright` Python package, writing any `test_*.py` Playwright test
file, adding a Playwright CI job, or recording any demo video/GIF. Per
the user's own framing ("just plan"), none of that is implemented yet.

## 2. Why Playwright, Against What Target

The project already has a real, testable browser-facing surface as of
this session: `engineering_studio.webapp` (W6a — FastAPI + Jinja2,
[`src/engineering_studio/webapp/__init__.py`](../src/engineering_studio/webapp/__init__.py)).
Playwright is the natural fit for the user's stated goal — "a few
prompts for testing that will call the entire project later on, and see
the prototype develop its recommendations... in action" — because it
drives a *real* rendered browser page, not just an HTTP response body,
which is what "seeing it happen" requires for a live demo recording.

## 3. Two Integration Modes (both grounded in what already exists)

### 3.1. Mode A — Playwright against a live `uvicorn` process (real demo mode)

Start the real ASGI server (`uvicorn engineering_studio.webapp:app`) as a
subprocess, point Playwright's browser at `http://127.0.0.1:<port>/`,
and drive the actual form submission end-to-end, including the actual
`fireworks_client` model calls (not mocked) — this is the mode for the
**actual recorded demo** (live, model calls hit the real backend, per
live-data-honesty: no mocked "demo" claiming to be real).

### 3.2. Mode B — Playwright against an in-process ASGI app (CI-safe test mode)

Playwright's Python bindings can also drive a page against a server
started specifically for the test (still a real `uvicorn`/`hypercorn`
process bound to a random free port, torn down after) — this is what
would run in CI as an actual `tests/e2e/test_webapp_playwright.py`-style
suite, but **with `sdk.run_pipeline` monkeypatched** (matching every
existing test in this project's suite — no real network/model call in
CI), so it verifies the browser rendering/interaction contract without
depending on the Fireworks backend being reachable from a CI runner.

**Grounded distinction:** Mode A is for the actual hackathon demo
recording (real model calls); Mode B is for a repeatable, offline CI
gate (mocked pipeline, same monkeypatch pattern already used in
`tests/test_webapp.py`). They are not the same suite and must not be
conflated — a CI-green Mode B run is not evidence the real Fireworks
integration works; only Mode A (or the existing `fireworks_client`
smoke path) is.

## 4. Proposed File Additions (future EXECUTE session)

| File | Purpose |
| :--- | :--- |
| `tests/e2e/__init__.py` | New `e2e` test package, separate from `tests/` unit suite (per `pyrightconfig`/coverage config — e2e tests should NOT count toward the 100% unit-coverage gate; they exercise a running server, not importable statements). |
| `tests/e2e/conftest.py` | Pytest fixture: starts `uvicorn` bound to `127.0.0.1:0` (OS-assigned free port) as a subprocess pointed at a `create_app()` instance with `sdk.run_pipeline` monkeypatched (Mode B); yields the base URL; tears the process down. |
| `tests/e2e/test_webapp_playwright.py` | Playwright test(s): navigate to `/`, fill the brief textarea, click "Run pipeline", assert the result page renders the expected artifact list — using `sync_playwright()`'s `chromium` (headless). |
| `demo/playwright_demo_script.py` | A **Mode A** script (not a pytest test) — launches the real `uvicorn` server pointed at the real `fireworks_client`, drives Playwright with `--video` recording enabled, submits 2-3 pre-agreed demo prompts in sequence, and saves each page screenshot/video under `demo/recordings/` for the actual hackathon submission. |

## 5. Proposed `pyproject.toml` Changes (future EXECUTE session)

```toml
[project.optional-dependencies]
e2e = [
    "playwright>=1.45",
]
```

Plus a one-time `playwright install chromium` (downloads the browser
binary; this is NOT a pip dependency and must be documented as a
separate CI/dev-setup step, since `pip install playwright` alone does
not fetch the browser).

## 6. Proposed CI Changes (future EXECUTE session)

A **separate** CI job (not folded into the existing `test` job in
[`ci.yml`](../.github/workflows/ci.yml)), gated so a Playwright
regression never blocks the fast unit-test gate:

```yaml
  e2e:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[webapp,e2e]"
      - run: playwright install --with-deps chromium
      - run: pytest tests/e2e -v --tb=short
```

`needs: test` ensures the fast unit/lint/security gate runs first; the
slower browser-based job only runs if that passes, per standard CI
layering (fast gates first, slow gates second).

## 7. Demo-Prompt Set (draft — for user confirmation before recording)

The user asked for "a few prompts for testing that will call the entire
project... and see the prototype develop its recommendations... in
action." Draft candidates, to be confirmed (not yet run against a real
model — these are proposed prompts, not verified outputs):

1. "Design a small autonomous warehouse inventory robot."
2. "Build a low-cost weather station for a community garden."
3. "Design a modular desk-mounted robotic arm for light assembly tasks."

**[NEEDS CONFIRMATION]** — the user should confirm or replace this list
before any Mode A recording session, since each prompt will trigger a
real Fireworks AI model call once Mode A is actually executed.

## 8. Aesthetic Compliance for the Recording

The webapp already renders exclusively from `utils.palette.PALETTE_B`
(background `#000000`, foreground `#FFAEC9`, accent `#B76E79` — see the
2026-07-07 deviation note in
[`utils/palette.py`](../src/engineering_studio/utils/palette.py)), so no
additional palette work is needed for the Playwright recording itself —
it captures whatever the webapp already renders.

## 9. Sequencing

This plan is intentionally NOT executed this session. A future session
should: (1) get user confirmation on the demo-prompt set (Section 7),
(2) add the `e2e` optional-dependency group and `tests/e2e/` package,
(3) implement Mode B first (CI-safe, mocked) and get it green, (4) only
then implement Mode A (real model calls) as a manually-triggered
recording script, never as an automatic CI job (it would make live
model calls on every push, which is costly and non-deterministic).

## Changelog

| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 2026.1.0.0 | 2026-07-07 | Hadrian Hu | Initial Playwright integration plan (planning only, per explicit user request). |
