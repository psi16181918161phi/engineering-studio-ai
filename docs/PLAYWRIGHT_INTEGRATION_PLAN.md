---
title: "PLAN — Playwright Integration for Engineering Studio AI Webapp Demonstration"
author: "Hadrian Hu"
date: "2026-07-07"
version: "2026.1.3.0"
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
          python-version: "3.14.4"
      - run: pip install -e ".[e2e]"
      - run: playwright install --with-deps chromium
      - run: pytest tests/e2e -v --tb=short
```

`needs: test` ensures the fast unit/lint/security gate runs first; the
slower browser-based job only runs if that passes, per standard CI
layering (fast gates first, slow gates second).

**Resolved (2026-07-08):** the project's `requires-python`, `ci.yml`'s
existing `test` job, and the local dev venv were all upgraded to Python
3.14.4 this session (user confirmed, after verifying 3.14.4 — not the
originally proposed 3.14.6 — is what's actually installed locally). The
future e2e job above is now consistent with the rest of the project;
no open version discrepancy remains.

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

**Confirmed (2026-07-08)** — the user gave explicit final confirmation
of the software-first list above during this session. It is now the
agreed prompt set for any future Mode A recording session; each prompt
will trigger a real Fireworks AI model call once Mode A is actually
executed.

## 8. Aesthetic Compliance for the Recording

**Superseded 2026-07-08:** the statement below ("no additional palette
work is needed") is now stale. `frontend/styles/theme.css` and
`frontend/app.js` were updated this session to add a **Light Mode /
Dark Mode toggle** (`#theme-toggle` button in the topbar), matching the
promotional poster pair `promotions/X_STUDIO_X.png` (light: pink bg,
black fg) and `promotions/X_STUDIO_X_ALT.png` (dark: black bg, pink
fg) — both reuse the exact same 3 locked hex values
(`--brand-pink #FFAEC9`, `--brand-black #000000`, `--brand-accent
#B76E79`), only the fg/bg role assignment swaps. Any future Playwright
recording (Mode A or Mode B) must now capture **both** themes, not just
one — see the new Section 11 below for the concrete steps.

**Naming collision, disclosed (do not conflate):**
`src/engineering_studio/utils/palette.py` independently defines its own
"Variant A"/"Variant B" terminology, but on a *different axis entirely*
— Variant A = Plot/Data Surface, Variant B = Interface Surface, and
**both of those are black-background** (`aesthetic_standards.txt` §1.2
surface-*kind* split, not a light/dark split). The webapp's new toggle
deliberately uses "Light Mode"/"Dark Mode" instead of "Variant A/B" to
avoid overloading that already-taken name. Any future contributor
reading both files side-by-side needs this disclosed distinction, not a
silent rename of one or the other — flagged for the user's awareness
rather than resolved unilaterally.

(Original 2026-07-07 note, now superseded, kept for history: "The
webapp already renders exclusively from `utils.palette.PALETTE_B`... so
no additional palette work is needed for the Playwright recording
itself — it captures whatever the webapp already renders.")

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
(2) add the `e2e` optional-dependency group and `tests/e2e/` package
per the Section 12.1 modularized file layout, (3) implement Mode B
first (CI-safe, mocked) and get it green, (4) only then implement Mode
A (real model calls) as a manually-triggered recording script per
Section 11, never as an automatic CI job (it would make live model
calls on every push, which is costly and non-deterministic).

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

## 11. Screen-Recording / Screen-Capture Execution Plan (both themes)

Added 2026-07-08 per explicit user request: "prepare for integration of
Playwright for useful screen recordings and screen captures of the
various examples we want to demo (software cases)." Still planning
only — no `playwright` package installed, no script executed yet.

### 11.1. Directory layout (future EXECUTE session)

```
demo/
  recordings/
    screenshots/
      light/   # one PNG per pipeline stage transition, Light Mode
      dark/    # one PNG per pipeline stage transition, Dark Mode
    video/
      light/   # one .webm per demo prompt, Light Mode
      dark/    # one .webm per demo prompt, Dark Mode
```

Kept separate by theme subfolder (not by filename suffix) so a future
`demo/playwright_demo_script.py` run can be pointed at one theme at a
time (`--theme light|dark`) without overwriting the other's output.

### 11.2. Per-theme capture sequence (for each of the 3 confirmed demo prompts, Section 7)

1. Launch the real `uvicorn` server (Mode A, Section 3.1).
2. Playwright navigates to `/`, and — **before** submitting any brief —
   clicks `#theme-toggle` if the desired theme does not match the
   toggle's default (Dark Mode is the default per `initTheme()`), then
   waits for `document.documentElement.dataset.theme` to reflect the
   target value.
3. Take a "before" screenshot of the empty dashboard
   (`pipeline-empty` state) — confirms the chosen theme rendered
   correctly before any pipeline activity starts.
4. Fill `#brief-input` with the demo prompt, submit, and start video
   recording (Playwright's built-in per-page video capture, enabled via
   `browser.new_context(record_video_dir=...)`).
5. For each of the 8 `STAGE_ORDER` stages, `page.wait_for_selector` on
   that stage card's `[data-state="done"]` (or `"error"`) transition,
   taking one incremental screenshot per transition — this directly
   satisfies Section 8's "every pipeline stage transition must be
   visibly explicit" recording requirement, now doubled for both
   themes.
6. On `quality_gate` reaching a terminal state, take a final
   full-dashboard screenshot, stop the video recording, and save both
   under the theme-specific subfolder from Section 11.1.
7. Repeat steps 2-6 for the other theme, then the next demo prompt.

### 11.3. Naming convention for captured files

`demo/recordings/screenshots/<light|dark>/<prompt-slug>_<stage-id>.png`
and `demo/recordings/video/<light|dark>/<prompt-slug>.webm` — e.g.
`demo/recordings/screenshots/light/backup-automation-script_electrical.png`.
`<prompt-slug>` is a short kebab-case derivation of each Section 7 demo
prompt, fixed once (in the future implementation) so file names stay
stable across re-recordings.

### 11.4. Validation criteria before a capture is considered "good"

- Every stage's status icon/text/border-style is legible against the
  active theme's background (WCAG "use of color" — already enforced by
  `app.css`'s icon+text+border triple-encoding, Section 8).
- No literal hex color appears anywhere except `theme.css`'s `:root`
  block (grep the rendered page's computed styles, or simply grep
  `frontend/**/*.css`/`frontend/**/*.js` for `#` followed by 3/6 hex
  digits outside `theme.css`).
- The captured window contains only the dashboard — no OS chrome,
  browser tab bar bleed, or other application content (Section 8, 3rd
  bullet), consistent across both themes.

## 12. Modularized Test & Page Structure (both themes, complete coverage)

Added 2026-07-08 per explicit user request for "complete tests, and
modularized tests and equally modularized html and css and other pages
as needed." Still planning only.

### 12.1. Test modularization (future `tests/e2e/`)

| File | Scope |
| :--- | :--- |
| `tests/e2e/conftest.py` | Shared `live_server` fixture (Mode B, Section 4) + a `theme` pytest fixture parametrized `["light", "dark"]` so every test below runs once per theme automatically. |
| `tests/e2e/test_theme_toggle.py` | Toggle button behavior only: default state, click-to-switch, `localStorage` persistence across a reload — independent of any pipeline run. |
| `tests/e2e/test_dashboard_render.py` | Static-render assertions per theme: topbar, launch panel, empty-state message — no run submitted. |
| `tests/e2e/test_pipeline_stream.py` | Full run-submission + SSE stage-transition assertions (the Section 11.2 sequence), parametrized by theme and by each Section 7 demo prompt. |
| `tests/e2e/test_webapp_playwright.py` | Superseded by the 3 files above once they exist — kept in the table from Section 4 only as the original single-file placeholder; the future EXECUTE session should split it into the 3 files above rather than grow one large file (Section 8's SOLID/Power-of-Ten guidance applied to tests as well as app code). |

### 12.2. Frontend modularization (future `frontend/`)

The current `frontend/` is already reasonably separated
(`index.html` / `app.js` / `styles/theme.css` / `styles/app.css`); the
only structural gap this plan identifies is the theme-toggle logic
added this session living inline in `app.js` alongside pipeline/SSE
logic. A future EXECUTE session, **only if/when the file grows further**
(YAGNI — not a change to make preemptively for a ~20-line toggle),
should consider splitting into:

- `frontend/theme-toggle.js` — the `initTheme()`/`applyTheme()` pair,
  imported as a `<script>` before `app.js`.
- Leave `index.html`, `styles/theme.css`, `styles/app.css` as single
  files — none of them currently exhibit the size/SRP pressure that
  would justify a split, per the implementation-discipline rule against
  over-engineering ahead of actual need.

## Changelog

| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 2026.1.0.0 | 2026-07-07 | Hadrian Hu | Initial Playwright integration plan (planning only, per explicit user request). |
| 2026.1.1.0 | 2026-07-07 | Hadrian Hu | Updated all architecture references from the retired synchronous Jinja2 webapp to the adopted async SSE + JS-frontend implementation following the same-day reconciliation merge; cleaned up malformed tables from a WIP edit; flagged the CI Python-version and demo-prompt confirmations as still open; added Section 10 on coordinating with in-flight teammate agent work. |
| 2026.1.2.0 | 2026-07-08 | Hadrian Hu | User confirmed the software-first demo-prompt set as final; resolved the CI Python-version question by confirming project-wide upgrade to 3.14.4 (verified installed locally; user's originally-requested 3.14.6 is not available on this machine). |
| 2026.1.3.0 | 2026-07-08 | Hadrian Hu | Added Section 11 (theme-aware screen-recording/screen-capture execution plan, both Light/Dark modes) and Section 12 (modularized test-file table + frontend modularization guidance) per explicit user request; updated Section 8 to flag the new webapp Light/Dark toggle and disclose its naming collision with `utils/palette.py`'s unrelated Variant A/B (Plot vs Interface Surface) terminology. |
