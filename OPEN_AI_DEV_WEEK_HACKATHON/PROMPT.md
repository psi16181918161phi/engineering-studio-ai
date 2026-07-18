---
title: "PROMPT — Execution Task Specifications for a Lower-Intelligence Executor Model"
author: "Hadrian Hu"
date: "2026-07-17"
version: "0.1.0"
keywords: ["prompt", "task-spec", "playwright", "e2e", "deployment", "openai-hackathon"]
status: "Draft"
---
<!--
WHAT: Copy-paste-ready Task Specification blocks, one per PLAN.md phase,
written for a SMALLER/cheaper model to execute later — maximally explicit,
zero inferred context, every SCOPE field spelled out (AGENTS.md §3).
WHY: The investigation/planning above assumed a strong model; execution
should not require re-deriving any of that reasoning. Each block below is
self-contained: a lower-intelligence model should be able to execute it
correctly using ONLY the block's own text plus the literal file paths
named in it.
HOW: Same Task Specification shape as
`prompts/agents/mdap/mdap-14-amd-lablab-hackathon-task-specs.md` (allowed
files / forbidden files / acceptance criteria / output format), adapted
for this repo's PLAN.md phases.
-->

# PROMPT — Execution Task Specifications

> Read this entire file before starting any task. Execute tasks in the
> numbered order below unless told otherwise. After each task, run the
> "Cross-task acceptance gate" commands (Section 8) before moving on —
> if any of them fail, stop and report the failure; do not proceed to the
> next task and do not "fix" the gate by lowering a threshold.

## Task 1 — `config_management/` agent file (PLAN.md Phase 1)

- **Allowed files:** create exactly one new file:
  `.github/agents/config_management/openai-config-specialist.agent.md`.
  You may also create `.github/agents/config_management/README.md` if one
  does not already exist.
- **Forbidden files:** do not touch any file outside
  `.github/agents/config_management/`.
- **Content requirements:** YAML frontmatter (title, author, date,
  version "0.1.0", keywords, status "Active"); a "Requires:" line citing
  `STANDARDS_SUMMARY.md` and `AGENTS.md` §3; a Mission section stating
  this role owns the OpenAI-provider environment-variable contract
  (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_ORCHESTRATOR`,
  `OPENAI_MODEL_SPECIALIST`, `OPENAI_MODEL_RESEARCH`); a "Never Touches"
  section stating it never hard-codes a real API key or model ID value
  into any tracked file; an Operating Flow section; an Output Format JSON
  block matching the style of the existing `testing.agent.md` file
  (read that file first as your style template — do not invent a new
  style).
- **Acceptance criteria:** file exists, follows the style of
  `.github/agents/testing.agent.md`, and does not duplicate content from
  `AGENTS.md` (cross-link instead of repeating).

## Task 2 — `.env.example` update (PLAN.md Phase 2)

- **Allowed files:** `.env.example` only.
- **Forbidden files:** every other file in the repository.
- **Steps:**

  1. Open `.env.example` and find the line containing only `=======`.
     Remove that single line (it is a stray merge-conflict-style marker,
     not intentional content) — do not remove or reorder any other line
     around it.
  2. Append this exact new block at the end of the file:

     ```
     # OpenAI Hackathon provider profile (optional; additive to Fireworks) —
     # model IDs left blank pending hackathon kickoff.
     OPENAI_API_KEY=
     OPENAI_BASE_URL=https://api.openai.com/v1
     OPENAI_MODEL_ORCHESTRATOR=
     OPENAI_MODEL_SPECIALIST=
     OPENAI_MODEL_RESEARCH=
     ```

- **Acceptance criteria:** `.env.example` has zero occurrences of a
  bare `=======` line; the new block is present verbatim; every
  pre-existing `FIREWORKS_*` line is still present, unchanged, in its
  original relative order.

## Task 3 — Unit/integration tests for any new Python code (PLAN.md Phase 4)

Only run this task if Task 4 (SDK/API/CLI additions) was actually
performed in this session — if PLAN.md Phase 4 was skipped (Phase 0
questions unresolved), skip this task too and say so.

- **Allowed files:** the same modules touched in Phase 4, plus new test
  files under `tests/unit/` or `tests/integration/` (mirror the existing
  test directory layout — inspect `tests/` first to find the matching
  pattern for the module you're testing).
- **Forbidden files:** do not modify any test's `--cov-fail-under`
  threshold in `pyproject.toml`.
- **Steps:**
  1. Run `pytest --cov=engineering_studio --cov-report=term-missing --cov-fail-under=100 -v` and read the coverage report.
  2. For every new line introduced in Phase 4 that shows as uncovered,
     add a test exercising it. Mock any network call — never call a real
     OpenAI or Fireworks endpoint from a test.
  3. Re-run the same command until it passes at 100%.
- **Acceptance criteria:** the exact command in step 1 exits 0 with
  "100.00%" coverage reported, and `ruff check .` / `mypy --strict .`
  (or `mypy src` if that is what the project's own task runs) also exit 0.

## Task 4 — Playwright end-to-end evidence: screenshots + video (PLAN.md Phase 8)

- **Allowed files:** new/updated files under `tests/e2e/` only, plus new
  output files under a `docs/`-adjacent evidence location matching the
  existing convention (inspect `docs/E2E_EVIDENCE.md` and
  `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` FIRST and follow their exact
  Mode-B/deterministic-pipeline convention — do not invent a different
  test harness).
- **Forbidden files:** do not modify `docs/E2E_EVIDENCE.md` itself in
  this task — that update happens in Task 5, after evidence exists.
- **Steps:**
  1. Confirm Playwright is installed (`pip install -e .[e2e]` or
     equivalent already used by this repo — check `pyproject.toml`'s
     `[project.optional-dependencies].e2e` group first).
  2. Set `ENGINEERING_STUDIO_FAKE_PIPELINE=1` (Mode B — deterministic,
     no live API call) exactly as the existing e2e suite already does.
  3. For any NEW UI element added in Phase 4 (e.g. a model-info badge or
     panel), add a Playwright test that: navigates to the dashboard,
     waits for the element to be visible, takes a screenshot via
     `page.screenshot(path=...)` into the same output convention already
     used by this repo's existing e2e tests (grep `tests/e2e/` for the
     current screenshot-path pattern and match it exactly), and records
     video (Playwright's built-in `record_video_dir` context option — set
     it the same way the existing e2e fixtures do, if they already do;
     otherwise add it consistent with Playwright's standard API, do not
     invent a custom video pipeline).
  4. Run `pytest tests/e2e -v --tb=short --no-cov --junitxml=reports/e2e-junit.xml`.
- **Acceptance criteria:** the new test(s) pass; a screenshot file and a
  video file both exist on disk at the conventional path; report the
  exact file paths produced in your final message.

## Task 5 — Update `docs/E2E_EVIDENCE.md` with the new run (PLAN.md Phase 8/9)

- **Allowed files:** `docs/E2E_EVIDENCE.md` only.
- **Forbidden files:** every other file.
- **Steps:** add one new row to the existing "Last verified run" table
  (do not delete or edit any existing row) describing the new Playwright
  run from Task 4: suite name, exact command used, result (N passed/failed),
  and today's date/timestamp. Match the table's existing column format
  exactly.
- **Acceptance criteria:** table has exactly one new row appended; every
  pre-existing row is byte-identical to before this task.

## Task 6 — Deployment re-verification (PLAN.md Phase 8)

- **Allowed files:** none (read-only verification task — do not edit
  `deployment/` files unless a build genuinely fails and the fix is a
  one-line, obviously-correct config value).
- **Steps:**
  1. `docker compose -f deployment/docker-compose.yml build dashboard`
  2. `docker compose -f deployment/docker-compose.yml up -d`
  3. `curl http://localhost:8000/api/health` (or the project's actual
     health route — check `api/` if this path differs) and confirm a
     `{"status": "ok"}`-shaped response.
  4. `docker compose -f deployment/docker-compose.yml down`
- **Acceptance criteria:** build succeeds, health check returns success,
  containers are torn down cleanly afterward (no orphaned containers).
  Report the exact output of step 3.

## Task 7 — Report back (always do this last, every session)

Produce a short final report with, at minimum: which tasks above were
completed vs. skipped (and why, if skipped), the exact commands run, and
their pass/fail results. Do not claim a task succeeded without having
actually run its acceptance-criteria command in this session.

## 8. Cross-task acceptance gate (run after EVERY task above)

```
ruff check .
mypy --strict .
bandit -r src -ll
pip-audit
pytest --cov=engineering_studio --cov-report=term-missing --cov-fail-under=100 -v
```

If any command fails, stop, do not proceed to the next task, and report
the exact failure output. Never edit a threshold/config to make a
failing gate pass.

## Changelog

| Version    | Date       | Author     | Description                                           |
| :--------- | :--------- | :--------- | :---------------------------------------------------- |
| 2026.0.1.0 | 2026-07-17 | Hadrian Hu | Initial task specifications for downstream execution. |
