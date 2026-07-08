---
title: "PLAN — Playwright Integration for Engineering Studio AI Webapp Demonstration"
author: "Hadrian Hu"
date: "2026-07-07"
version: "2026.1.1.0"
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
browser testing/demonstration against the command-and-control webapp
(engineering_studio.webapp.app, mounted as FastAPI + SSE + vanilla-JS
frontend/ — NOT the retired Jinja2 webapp this plan originally described).
WHY: The user asked to "plan for the latter of how to integrate playwright"
— explicitly a planning request, not an implementation request. No
Playwright test files, fixtures, or CI jobs are added yet. This revision
(2026.1.1.0) updates the plan after a same-day architecture reconciliation
merge replaced the synchronous Jinja2 webapp with a teammate's async
SSE + JS-frontend implementation (see markdowns/chats/ for that session's
full record) — every reference to "form submission" / "result page" /
`create_app()` below is now stale relative to the OLD architecture and has
been corrected to the new run-then-stream contract.
HOW: This document is the artifact a future EXECUTE-phase session
consumes to actually add the described tests/fixtures/CI job.
-->

# PLAN — Playwright Integration

## 1. Scope and Non-Goals

**In scope (this document):** a concrete, reviewable plan for adding
Playwright-driven browser tests/demonstration scripts against the
command-and-control webapp.

**Explicitly out of scope (not done this session):** installing the
`playwright` Python package, writing any `test_*.py` Playwright test
file, adding a Playwright CI job, or recording any demo video/GIF. Per
the user's own framing ("just plan"), none of that is implemented yet.

## 2. Why Playwright, Against What Target

The project's real, testable browser-facing surface is
`engineering_studio.webapp` — a single FastAPI app
([`src/engineering_studio/webapp/app.py`](../src/engineering_studio/webapp/app.py))
that mounts `/api/health` and `/api/runs/*` (see
[`src/engineering_studio/api/runs.py`](../src/engineering_studio/api/runs.py))
plus a static, vanilla-JS/HTML/CSS dashboard
([`frontend/`](../frontend/)) that POSTs a product brief, then opens a
Server-Sent-Events connection (`GET /api/runs/{run_id}/stream`) to render
each pipeline stage's status live as it transitions
running → done/error. Playwright is the natural fit for the user's
stated goal — "a few prompts for testing that will call the entire
project later on, and see the prototype develop its recommendations...
in action" — because it drives a *real* rendered, live-updating browser
page, not just a single HTTP response body, which is what "seeing it
happen" requires for a live demo recording of an async/streaming UI.

## 3. Two Integration Modes (both grounded in what already exists)

### 3.1. Mode A — Playwright against a live `uvicorn` process (real demo mode)

Start the real ASGI server (`uvicorn engineering_studio.webapp:app`) as a
subprocess, point Playwright's browser at `http://127.0.0.1:<port>/`,
submit a brief through the actual dashboard form, and let Playwright
wait on the live SSE-driven DOM updates (e.g. `page.wait_for_selector`
on a stage's "done" status element) through to pipeline completion —
including the actual `fireworks_client` model calls (not mocked) — this
is the mode for the **actual recorded demo** (live, model calls hit the
real backend, per live-data-honesty: no mocked "demo" claiming to be
real).

### 3.2. Mode B — Playwright against an in-process ASGI app (CI-safe test mode)

Playwright's Python bindings can also drive a page against a server
started specifically for the test (still a real `uvicorn` process bound
to a random free port, torn down after) — this is what would run in CI
as an actual `tests/e2e/test_webapp_playwright.py`-style suite, but with
`engineering_studio.runs.run_pipeline` monkeypatched to a fast, fully
deterministic fake stage-emitter (matching the pattern already used in
this session's `tests/test_api.py` and `tests/test_runs.py` unit
suites) — no real network/model call in CI, so it verifies the
browser rendering/SSE-consumption contract without depending on the
Fireworks backend being reachable from a CI runner.

**Grounded distinction:** Mode A is for the actual hackathon demo
recording (real model calls); Mode B is for a repeatable, offline CI
gate (mocked pipeline, same monkeypatch-`run_pipeline` pattern already
used in `tests/test_api.py`/`tests/test_runs.py`). They are not the same
suite and must not be conflated — a CI-green Mode B run is not evidence
the real Fireworks integration works; only Mode A (or the existing
`fireworks_client` smoke path) is.

## 4. Proposed File Additions (future EXECUTE session)

| File | Purpose |
| :--- | :--- |
| `tests/e2e/__init__.py` | New `e2e` test package, separate from `tests/` unit suite (per `pyrightconfig`/coverage config — e2e tests should NOT count toward the 100% unit-coverage gate; they exercise a running server, not importable statements). |
| `tests/e2e/conftest.py` | Pytest fixture: starts `uvicorn` bound to `127.0.0.1:0` (OS-assigned free port) as a subprocess serving `engineering_studio.webapp.app:app` with `engineering_studio.runs.run_pipeline` monkeypatched (Mode B); yields the base URL; tears the process down. |
| `tests/e2e/test_webapp_playwright.py` | Playwright test(s): navigate to `/`, fill the brief input, submit, then assert the SSE-driven dashboard renders each stage transitioning to "done" and the final artifact list — using `sync_playwright()`'s `chromium` (headless). |
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
      - run: pip install -e ".[e2e]"
      - run: playwright install --with-deps chromium
      - run: pytest tests/e2e -v --tb=short
```

`needs: test` ensures the fast unit/lint/security gate runs first; the
slower browser-based job only runs if that passes, per standard CI
layering (fast gates first, slow gates second).

**[NEEDS CONFIRMATION]** — an earlier WIP edit to this section proposed
`python-version: "3.14.6"` instead of `"3.11"`. `pyproject.toml` declares
`requires-python = ">=3.11"` and every other CI job in this repo pins
`"3.11"`, so `"3.11"` is what's written above for consistency; flagging
this explicitly since the discrepancy was never confirmed with the user
and this repo's Python-version policy (per user memory) is "3.14.4 x64
for new venvs" specifically, not 3.14.6 — a future session should
confirm the intended CI Python version before implementing this job.

## 7. Demo-Prompt Set (draft — for user confirmation before recording)

The user asked for "a few prompts for testing that will call the entire
project... and see the prototype develop its recommendations... in
action." Two candidate sets exist from prior drafting; the user
subsequently indicated software-first prompts are preferred (easiest to
demo live in a hackathon setting) and self-confirmed that set below —
still marked NEEDS CONFIRMATION here since that confirmation was
recorded mid-edit, not through an explicit turn in this conversation.

**Original draft (hardware-oriented, superseded):**

1. "Design a small autonomous warehouse inventory robot."
2. "Build a low-cost weather station for a community garden."
3. "Design a modular desk-mounted robotic arm for light assembly tasks."

**Software-first set (preferred for the live demo):**

1. "Create a Python script that automates the backup of important files to a cloud storage service."
2. "Develop a simple web application that allows users to track their daily habits and visualize their progress over time."
3. "Write a command-line tool that analyzes text files and generates a summary report of word frequency and sentiment."

**[NEEDS CONFIRMATION]** — the user should give one final explicit
confirmation of the software-first list above (or replace it) before
any Mode A recording session, since each prompt will trigger a real
Fireworks AI model call once Mode A is actually executed. A prior WIP
edit to this file recorded a self-confirmation ("I, as user, confirm
this is sufficient for demo purposes") — carried forward here as
context, not as a substitute for that final go-ahead.

## 8. Aesthetic Compliance for the Recording

The webapp already renders exclusively from `utils.palette.PALETTE_B`
(background `#000000`, foreground `#FFAEC9`, accent `#B76E79` — see the
2026-07-07 deviation note in
[`utils/palette.py`](../src/engineering_studio/utils/palette.py)), so no
additional palette work is needed for the Playwright recording itself —
it captures whatever the webapp already renders.

Additional recording and UI constraints carried forward from a prior
WIP note on this file, restated here cleanly:

- Record **both** video and screenshots; save each under its own
  subdirectory, separated further into `screenshots/` and `video/`
  (e.g. `demo/recordings/screenshots/`, `demo/recordings/video/`).
- Only capture the relevant application window(s) — never a user's
  personal desktop, other applications, or unrelated development
  environments, on any OS.
- Every pipeline stage transition the agents perform must be visibly
  explicit in the recorded UI (this is already satisfied by the SSE
  dashboard's per-stage status list — no additional work needed here,
  just confirmed as a recording requirement).
- Per SOLID/ACID/NASA-JPL "Power of Ten" style single-responsibility
  guidance: no single HTML/JS page or component in `frontend/` should
  grow to "do too much" — keep the dashboard's stage list, artifact
  viewer, and brief-submission form as separable concerns (this is
  already true of the current `frontend/app.js` structure and must be
  preserved as teammates add their own specialized frontend pieces —
  see Section 10).

## 9. Sequencing

This plan is intentionally NOT executed this session. A future session
should: (1) get user confirmation on the demo-prompt set (Section 7),
(2) add the `e2e` optional-dependency group and `tests/e2e/` package,
(3) implement Mode B first (CI-safe, mocked) and get it green, (4) only
then implement Mode A (real model calls) as a manually-triggered
recording script, never as an automatic CI job (it would make live
model calls on every push, which is costly and non-deterministic).

## 10. Coordination With In-Flight Teammate Work

Per the user's explicit note: other team members are independently
building more specialized agents (documentation, testing, scaffolding,
etc.) surfaced under `.github/` in this same repository, and a previous
same-day merge already showed how easily two people can independently
build an overlapping web surface without cross-visibility (see
markdowns/chats/ for that reconciliation). Before implementing this
plan:

- Re-check `git log --graph --all` and `git diff HEAD..origin/main --stat`
  for `frontend/`, `tests/e2e/`, and `.github/` changes immediately
  before starting Section 9's future session — not just before opening
  a PR.
- Keep any new Playwright fixtures/tests in their own narrowly-scoped
  files (`tests/e2e/conftest.py`, `tests/e2e/test_webapp_playwright.py`)
  rather than one large e2e module, so a teammate's own testing-focused
  agent can add further `tests/e2e/test_*.py` files without touching
  these.

## Changelog

| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 2026.1.0.0 | 2026-07-07 | Hadrian Hu | Initial Playwright integration plan (planning only, per explicit user request). |
| 2026.1.1.0 | 2026-07-07 | Hadrian Hu | Updated all architecture references from the retired synchronous Jinja2 webapp to the adopted async SSE + JS-frontend implementation following the same-day reconciliation merge; cleaned up malformed tables from a WIP edit; flagged the CI Python-version and demo-prompt confirmations as still open; added Section 10 on coordinating with in-flight teammate agent work. |
