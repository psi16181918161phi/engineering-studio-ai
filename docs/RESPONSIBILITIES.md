
---
title: "AI Engineering Studio — AMD Hackathon Team Roles & Responsibilities"
author: "Hadrian Hu"
date: "2026-07-09"
version: "2026.1.2.0"
keywords: ["agent-collaboration", "engineering-studio", "hackathon", "responsibilities", "roles", "team-organization", "workflow"]
status: "Draft"
project_lead: "Hadrian [psi16181918161phi]"
repository: "engineering-studio-ai"
changelog:
  - version: "2026.1.2.0"
    date: "2026-07-10"
    author: "Hadrian Hu"
    description: "Final-sprint-freeze pass: merged teammate PRs #9/#10, Docker rework (build+run verified), fresh regression re-verified, docs/JUDGES_GUIDE.md added, meta-project security propagation checkbox closed."
  - version: "2026.1.1.0"
    date: "2026-07-09"
    author: "Hadrian Hu"
    description: "Completed WISHLIST_2026-07-09_demo-one-more-round (W-01 through W-06); added presentation/slides.html; confirmed full green regression."
  - version: "2026.1.0.0"
    date: "2026-07-05"
    author: "Hadrian Hu"
    description: "Restructured document to conform to markdown documentation standards (front matter, TOC, Abstract, Keywords, Executive Summary, Changelog)."
  - version: "1.0.0"
    date: "2026-07-04"
    author: "Hadrian Hu"
    description: "Initial draft of team roles and responsibilities."
---

# AI Engineering Studio — AMD Hackathon Team Roles & Responsibilities

---

## Table of Contents

- [Abstract](#abstract)
- [Keywords](#keywords)
- [Executive Summary](#executive-summary)
- [Project Overview](#project-overview)
    - [Project Vision](#project-vision)
    - [Team Organization](#team-organization)
- [Team Roles](#team-roles)
    - [Role 1 — Project Architect & Technical Lead](#role-1--project-architect--technical-lead)
    - [Role 2 — AI Research & Prompt Engineering](#role-2--ai-research--prompt-engineering)
    - [Role 3 — AI Pipeline & Backend Engineering](#role-3--ai-pipeline--backend-engineering)
    - [Role 4 — Software Quality, Security & DevOps](#role-4--software-quality-security--devops)
    - [Role 5 — Frontend, Visualization & Demonstration](#role-5--frontend-visualization--demonstration)
    - [Role 6 — Documentation, Paper & Presentation](#role-6--documentation-paper--presentation)
- [Workflow and Collaboration](#workflow-and-collaboration)
    - [GitHub Workflow](#github-workflow)
    - [Repository Structure](#repository-structure)
    - [Communication](#communication)
    - [Daily Coordination](#daily-coordination)
- [Standards and Deliverables](#standards-and-deliverables)
    - [Coding Standards](#coding-standards)
    - [Definition of Done](#definition-of-done)
- [Role Assignments](#role-assignments)
- [Collaboration Principles](#collaboration-principles)
- [Final Goal](#final-goal)
- [Changelog](#changelog)

---

## Abstract

This document defines the team organization, role responsibilities, workflow
conventions, and quality expectations for the **AI Engineering Studio**
hackathon submission. The problem addressed is the coordination of six team
members across research, backend orchestration, quality assurance,
front-end demonstration, and documentation disciplines within a compressed
hackathon timeline. The methodology applied assigns one primary ownership
area per member — Project Architecture, AI Research, Backend Engineering,
Quality/Security/DevOps, Frontend/Visualization, and Documentation — while
encouraging cross-team collaboration on shared deliverables. A lightweight
GitHub branching workflow (`main` → `develop` → `feature/<name>`) and a
Definition of Done checklist are established to keep contributions
consistent and reviewable. The expected outcome is a working demonstration
of an AI Engineering Studio capable of turning a natural-language project
description into a partially or fully engineered solution through
multi-agent collaboration. The conclusion is that clear role ownership,
lightweight process, and a shared Definition of Done are sufficient to
coordinate a six-person team through research, implementation, testing,
security review, and presentation within the hackathon timeframe.

---

## Keywords

agent-collaboration, engineering-studio, hackathon, responsibilities, roles,
team-organization, workflow

---

## Executive Summary

**Objective:** Establish clear ownership and coordination rules so a
six-person team can deliver a working **AI Engineering Studio** demonstration
for the AMD hackathon — a system that turns a natural-language software or
hardware idea into a partially or fully engineered solution through
collaborating AI agents.

**Approach:** The team is organized around six primary ownership areas —
Project Architecture & Technical Lead, AI Research & Prompt Engineering, AI
Pipeline & Backend Engineering, Software Quality/Security/DevOps, Frontend &
Visualization, and Documentation/Paper/Presentation — while every member is
encouraged to contribute outside their primary area. Work is coordinated
through a `main`/`develop`/`feature/<name>` GitHub branching strategy, GitHub
Issues/Discussions for task tracking, and a daily check-in → work → push →
pull request → evening integration cadence.

**Outcome:** A defined role structure, repository layout, and Definition of
Done checklist that keeps the team aligned on scope, reduces duplicate work,
and ensures every delivered feature is functional, tested, documented, and
reviewed before merge.

**Recommendations:** Team members should fill in the [Role Assignments](#role-assignments)
table once roles are finalized, keep pull requests small and frequent, raise
blockers early via GitHub Issues, and prioritize a polished, working
demonstration over an overly ambitious feature set.

---

## Project Overview

### Project Vision

The objective of this project is to build an **AI Engineering Studio** capable of transforming a high-level software or hardware idea into a partially or fully engineered solution through the collaboration of multiple AI agents.

The envisioned workflow includes:

- Research
- Requirements gathering
- Architecture generation
- Code scaffolding
- Coding standards enforcement
- Testing
- Verification & Validation
- Software Supply Chain Security
- Documentation
- Deployment
- Demonstration
- Technical Paper generation
- Presentation generation

Ultimately, a user should be able to describe an application using natural language, after which specialized AI agents collaborate to engineer the solution.

### Team Organization

We currently have **6 team members**.

To maximize productivity during the hackathon, each member should primarily own one area while collaborating across the repository.

Everyone is encouraged to help others whenever possible.

---

## Team Roles

### Role 1 — Project Architect & Technical Lead

#### Responsibilities

- Overall project vision
- Scope definition
- Task coordination
- Architecture decisions
- Integration planning
- GitHub management
- Pull Request reviews
- Final approval before merges
- Ensure project stays on schedule

#### Deliverables

- Architecture document
- Task assignments
- Repository organization
- Milestone planning
- Final integration

---

### Role 2 — AI Research & Prompt Engineering

#### Responsibilities

Research the technologies needed.

Possible topics include:

- AMD technologies
- AI models
- Agent frameworks
- Prompt engineering
- Existing research
- Open-source tools
- Benchmarking
- Similar projects

Create prompts used throughout the system.

#### Deliverables

- Research notes
- Technology comparisons
- Prompt templates
- Design recommendations

---

### Role 3 — AI Pipeline & Backend Engineering

#### Responsibilities

Develop the backend that connects the AI agents.

Possible work includes:

- Agent orchestration
- APIs
- Workflow execution
- Backend services
- AI model integration
- Database integration
- Logging infrastructure

#### Deliverables

- Backend implementation
- AI orchestration
- APIs
- Workflow engine

---

### Role 4 — Software Quality, Security & DevOps

#### Responsibilities

Ensure the project is stable, secure and maintainable.

Possible work includes:

- Testing
- Unit tests
- Integration tests
- CI/CD
- Dependency management
- Software Supply Chain Security
- Static analysis
- Coding standards
- Code reviews

#### Deliverables

- Test suites
- GitHub Actions
- Security checks
- Quality reports
- CI pipeline

#### Current Todos (as of the W1/W2/W3/W7 implementation pass)

The following became relevant to Role 4 once `exceptions/`, `decorators/`,
`models/`, `utils/palette.py`, and `sdk/` were populated with real code
(previously empty stub packages) and a strict coverage gate was enabled:

- [x] `pyproject.toml` now enforces `--cov-fail-under=100` via
  `[tool.pytest.ini_options]` — `.github/workflows/ci.yml`'s existing
  `pytest tests -v --tb=short` step picks this up automatically (no
  workflow change needed; `requirements-dev.txt` already installs
  `pytest-cov`). Verify on the next CI run that the gate actually fires
  in the hosted runner, not just locally.
- [ ] Security review of `decorators.requires_env` and
  `exceptions.ConfigurationError`: confirm no code path logs the
  *value* of an environment variable (only its name) — `log_call` in
  `decorators/__init__.py` was written to log only `func.__qualname__`,
  never argument values, specifically to avoid leaking a product brief
  or credential into aggregated logs; audit this holds as new call
  sites adopt the decorator.
- [ ] When `api/` (W5) and `webapp/` (W6a) are implemented in a future
  session, run `bandit -r src` (OWASP-relevant static analysis) against
  the new HTTP-facing code before merge — none of this session's work
  (`exceptions/`, `decorators/`, `models/`, `utils/palette.py`, `sdk/`)
  is network- or web-facing, so it was not in scope for that scan yet.
- [ ] `gui/` (W6b, `textual`) will be a new runtime dependency under a
  `gui` optional-dependency extra, not yet added to `pyproject.toml` —
  run `pip-audit`/dependency review on it once W6b lands.
- [ ] Confirm the `feat/full-sdk-cli-api-webapp-gui` branch's PR (once
  opened) targets `main` per the team's actual observed practice (not
  the stale local `develop`), and that branch protection / required
  checks still apply to it.

#### Current Todos (as of the W4 CLI-subcommand / CI-hardening pass, 2026-07-07)

- [x] **`ci.yml` bug fixed**: the `Lint (ruff)` step ran `ruff check .`
  (whole repo) while `Type check (mypy)` only ran `mypy src` — a scope
  mismatch. This wasn't a false positive: `run_scripts/` (a real,
  intentional part of the repo, not excluded anywhere) had 17 genuine
  ruff violations (12× `F541` extraneous `f`-string prefix, 5× `E402` on
  a documented, intentional `sys.path` guard pattern in
  `run_scripts/__main__.py`). Fixed by auto-fixing the `F541`s and adding
  targeted `# noqa: E402` on the justified late imports — `ruff check .`
  now passes clean; no scope was narrowed/excluded to hide the problem.
- [x] **CVE/security scanning baked into CI**: added `bandit -r src -ll`
  (OWASP-relevant static analysis, per this Role's own earlier todo
  above) and `pip-audit` (dependency CVE audit) as blocking CI steps,
  plus a `pip install --upgrade pip setuptools wheel` step before them
  (the local venv's bundled pip 24.0/setuptools 65.5.0 had 10 known,
  unrelated CVEs — upgrading first, as GitHub-hosted runners' own
  base image already does more consistently, avoids a flaky gate on
  base tooling rather than the project's own declared dependencies,
  which audited clean). Both tools added to `requirements-dev.txt`.
- [x] **W4 delivered**: `cli/commands.py` (`cmd_run`/`cmd_status`/
  `cmd_artifacts`) built on `sdk.EngineeringStudioClient` per the plan;
  `cli/__init__.py` now dispatches `run`/`status`/`artifacts`
  subcommands plus an optional `--artifacts-root PATH`, preserving the
  pre-W4 bare-brief invocation as an implicit `run` for backward
  compatibility. 100% coverage maintained (67 tests).
- [x] **Real bug found and fixed while closing W4's coverage gap**:
  `fireworks_client.ModelUnavailableError` and
  `exceptions.ModelUnavailableError` were two distinct sibling classes
  (both inheriting `EngineeringStudioError` directly, but not each
  other) — so `sdk.EngineeringStudioClient.run()`'s
  `except ModelUnavailableError: raise` special-case, and the CLI's own
  `except ModelUnavailableError` branch, could never actually match a
  *real* pipeline failure (only ones constructed from `exceptions`
  directly, as in `test_sdk.py`). Every genuine model-unavailable error
  from `agents.orchestrator.run_pipeline` was silently falling through
  to the generic `PipelineExecutionError` wrap instead, losing its
  specific identity. Fixed by re-exporting
  `exceptions.ModelUnavailableError` from `fireworks_client` (same
  class, not a new subclass) — import path and class name unchanged for
  callers, but `isinstance` now actually holds.
- [ ] **Merge safety check requested by the user**: reviewed
  `84a818c` (`Merge pull request #1 from Umaima-Mughal/feature/research-role2`)
  — diff-only touches `research/research-findings.md` (+87/-9 lines),
  no code/CI/dependency files changed. Confirmed low-risk. No other
  merged PRs exist on `main` as of this session (`git log --oneline`
  shows only this one merge commit plus direct commits). Re-check this
  item once additional PRs from other team members land.
- [ ] W5 (`api/`, FastAPI), W6a (`webapp/`), W6b (`gui/`, `textual`) are
  still not implemented — each needs a new runtime dependency added to
  `pyproject.toml` (`fastapi`+`uvicorn`(+`httpx` for tests) for W5/W6a,
  `textual` for W6b) and its own `pip-audit`/`bandit` pass before merge,
  per this Role's standing todos above.

#### Current Todos (as of the W5/W6a/W6b/W8 acceleration pass, 2026-07-07 continuation)

- [x] **W5 delivered**: `api/__init__.py` — `create_app()` FastAPI
  factory exposing `GET /health`, `POST /pipeline/run`,
  `GET /pipeline/{id}`, built on `sdk.EngineeringStudioClient`. Job
  registry is in-memory only (disclosed limitation, not a fabricated
  durable store). 100% coverage (`tests/test_api.py`).
- [x] **W6a delivered**: `webapp/__init__.py` — FastAPI + Jinja2
  server-rendered pages (`GET /`, `POST /run`, `GET /pipeline/{id}`)
  consuming the W5 app in-process via `httpx.AsyncClient` +
  `httpx.ASGITransport` (no real socket). 100% coverage
  (`tests/test_webapp.py`).
- [x] **W6b delivered**: `gui/__init__.py` — `textual` TUI
  (`EngineeringStudioApp`), consuming the SDK directly. 100% coverage
  via `textual`'s headless `Pilot` API, run under `anyio`'s pytest
  plugin (no `pytest-asyncio` dependency needed) (`tests/test_gui.py`).
- [x] **W8 (branch/dependency resync)**: confirmed no new commits landed
  on `main` since the prior session (`git log origin/main..origin/feat/...`
  empty) — no additional merge-safety review was needed this pass.
  `pyproject.toml` gained `api`/`webapp`/`gui` optional-dependency
  groups (`fastapi`, `uvicorn`, `jinja2`, `python-multipart`,
  `textual`) plus `httpx` under `dev` (for `TestClient`/`AsyncClient` in
  tests); `requirements.txt`/`requirements-dev.txt` and `ci.yml`'s
  install step updated to match (`pip install -e ".[api,webapp,gui]"`).
- [x] **Coverage-tooling finding**: a FastAPI async route's branch body
  (the `if response.status_code >= 400:` arm in `webapp/__init__.py`)
  showed as uncovered by `coverage.py` even when a passing test
  demonstrably exercised it (verified via a standalone reproduction
  script) — traced to the branch living directly in the coroutine's
  post-`await` continuation when driven through
  `starlette.testclient.TestClient`'s background event-loop portal.
  Fixed by extracting the branch into an ordinary (non-async) helper
  function (`_render_api_response()`) called as the sole statement after
  each `await`, rather than adding a blind `# pragma: no cover`. Verified
  fix: `100%` on `webapp/__init__.py` before and after is a genuine
  measurement, not a suppressed gap.
- [x] **Palette deviation, explicitly disclosed**: the 2026-07-06 plan's
  chosen foreground values (`#E8A0A8`/`#F5E6E8`, inside the standard's
  recommended range) were superseded this session by the user's own
  explicit, twice-repeated hex directive — `#FFAEC9`
  (foreground/background), `#000000` (background/foreground), shared
  `#B76E79` accent. `#FFAEC9` sits slightly outside
  `aesthetic_standards.txt` Table R.1's recommended reference range;
  the deviation is recorded in `utils/palette.py`'s module docstring
  per the grounding-disclosure rule (explicit repeated user instruction
  on the project's own scheme supersedes a non-binding recommended
  range).
- [x] **Playwright integration — planning only, per explicit user
  request**: `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` documents two modes
  (Mode A: live demo recording against a real `uvicorn` process/real
  model calls; Mode B: CI-safe mocked E2E tests) plus proposed files,
  `pyproject.toml`/`ci.yml` changes, and a draft demo-prompt set
  flagged `[NEEDS CONFIRMATION]`. No Playwright package, test file, or
  CI job was added this session — planning artifact only.
- [ ] Full lint/mypy --strict/bandit/pip-audit/pytest(100% coverage,
  86 tests) all pass locally as of this session's end; still pending:
  opening the actual PR to `main` for this branch (git commit made
  locally; no push performed — pushing requires explicit user
  confirmation per this platform's Tier-3 authorization rule).
- [ ] W7 (closing coverage gaps on already-real modules) — no gaps found
  this pass; all pre-existing modules remained at 100% throughout.

#### Current Todos (as of the teammate-integration / Playwright-readiness pass, 2026-07-08)

- [x] **Merged `origin/main`** (3 commits: `feature/prompt-drafts` #4,
  `domain-specialist-agents` #5, `research-business-agents` #6, all
  `Umaima-Mughal`) into `feat/full-sdk-cli-api-webapp-gui` — clean merge,
  no conflicts. Re-verified 102/102 tests, 100.00% coverage, `ruff check .`
  clean both before and after.
- [x] **Reconciled `research/prompt-drafts/` (22 files) into
  `.github/agents/`**: upgraded 8 existing roster files with richer
  Operating-Flow/Evaluation-Criteria content (and corrected
  `systems-engineering-specialist.agent.md`'s scope to cross-domain-
  integration-only, since Firmware/Simulation are separately-dispatched
  code stages); created 6 new roster files
  (`firmware-specialist.agent.md`, `simulation-specialist.agent.md`,
  `product-strategy-specialist.agent.md`, `benchmarking-specialist.agent.md`,
  `technology-scout-specialist.agent.md`,
  `challenge-division/engineering-cross-domain-review.agent.md`). Every
  file cites its `research/prompt-drafts/...` source + PR number.
- [x] **Built a real Light Mode / Dark Mode toggle** for the webapp
  (`#theme-toggle` in `frontend/index.html`, `initTheme()`/`applyTheme()`
  in `frontend/app.js`, semantic fg/bg swap in `frontend/styles/theme.css`
  — zero changes needed to `app.css`). Matches the promotional poster
  pair (`promotions/X_STUDIO_X.png` = light, `X_STUDIO_X_ALT.png` = dark).
  **Naming-collision disclosure**: this is unrelated to
  `utils/palette.py`'s own "Variant A/B" (Plot vs. Interface Surface,
  both black-bg) — deliberately named "Light/Dark Mode" instead to avoid
  overloading that name; documented in both files.
- [x] **Extended `docs/PLAYWRIGHT_INTEGRATION_PLAN.md`** (now v2026.1.3.0)
  with §11 (theme-aware screen-recording/screen-capture execution steps)
  and §12 (modularized `tests/e2e/` file table + frontend-modularization
  guidance) — still planning-only, no `playwright` package/test/CI job
  added.
- [x] **Investigate -> Preplan -> Plan -> Prompt docs written**: see
  `markdowns/investigations/INVESTIGATE_2026-07-08_...md`,
  `markdowns/preplans/PREPLAN_2026-07-08_...md`,
  `markdowns/plans/PLAN_2026-07-08_...md`,
  `markdowns/plans/PROMPT_2026-07-08_...md` (the literal next-session
  task spec for the deferred `docs/task-specs.md` upgrade + real
  Playwright implementation).
- [ ] **Not done this session (deferred, see PROMPT doc)**: upgrading
  `docs/task-specs.md`'s per-discipline content from the reconciled
  roster; installing `playwright`/writing real test files; recording any
  demo video/screenshot; posting the drafted (unposted) teammate
  coordination note to GitHub; pushing this session's commits to
  `origin` (all Tier-2/3 actions pending explicit user confirmation).

#### Current Todos (as of the private_prompt_3 follow-up pass, 2026-07-09)

- [x] **CI failure root cause fixed in code**: `src/engineering_studio/fireworks_client.py`
  now normalizes `base_url` through a typed intermediate (`resolved_base_url`)
  before `.rstrip("/")`, removing a strict-mypy `union-attr` error that could
  fail the CI `mypy src` gate.
- [x] **Local CI-equivalent validation rerun** after the fix:
  `ruff check .` clean, `mypy src` clean, `bandit -r src -ll` clean,
  `pip-audit` clean (with the expected local-package skip note), and
  project tests at 100% coverage (`111 passed`, gate met).
- [x] **Merge-safety re-check on last-night teammate pushes** completed:
  PR #8 lineage commits (`728d609`, `a264f3d`, merge `91a3b50`) touch
  `.dockerignore` only; no application runtime code, dependency manifests,
  or workflow logic changed in those teammate commits. Classified low risk.
- [x] **Project-level CVE/security gates remain baked into CI** and were
  revalidated in this pass: `bandit` (static scan) + `pip-audit`
  (dependency CVEs) are active and green.
- [ ] **Meta-project security propagation check** (outside this submodule)
  remains a coordination task: mirror equivalent CVE/static-analysis gate
  enforcement in parent-repo workflows where not already present.
- [x] **Human-content placeholders resolved** (non-code):
  `presentation/slides-outline.md` and `demo/demo-script.md` placeholders
  were filled in the 2026-07-09 "demo one more round" pass below.

#### Current Todos (as of the WISHLIST_2026-07-09_demo-one-more-round completion pass, 2026-07-09)

- [x] **W-01 — `demo/demo-script.md` fallback plan written**: replaced the
  `[SECTION INCOMPLETE]` placeholder with a full 5-step truthful fallback
  flow (disclose the failure, prove `/api/health`, play pre-recorded
  Mode-B recordings, reveal a completed artifact set via CLI/dashboard,
  optionally retry live) plus a "Preparation checklist" subsection.
- [x] **W-02 — `presentation/slides-outline.md` placeholders filled**:
  Slide 2 (Problem), Slide 6 (AMD Ecosystem Usage — Fireworks AI live,
  MI300X/ROCm/vLLM disclosed-but-not-provisioned fallback), and Slide 8
  (Startup Potential/Roadmap, with an explicit no-market-validation
  caveat) all written with grounded citations, no fabricated claims.
- [x] **W-03 — demo rehearsal tooling added**: `demo/demo_prompts.json`
  (single source of truth for the 3 confirmed demo prompts) and
  `demo/run_demo_sequence.py` (CLI-only, no-browser rehearsal launcher
  that runs all 3 prompts through the pipeline and writes a timestamped
  `manifest.json`) — both lint/type clean, manually verified working.
- [x] **W-04 — e2e evidence doc added at `docs/E2E_EVIDENCE.md`**
  (relocated from the WISHLIST's literal `reports/e2e/README.md` path,
  since `reports/` is fully gitignored per `.gitignore`'s
  `[Rr][Ee][Pp][Oo][Rr][Tt][Ss]/` pattern — deviation disclosed inline in
  the new doc itself). States what the e2e suite proves and does NOT
  prove (Mode B only, no live Fireworks call), with exact last-verified
  counts (111 unit tests / 100% coverage; 17 e2e tests, 0 failures/errors).
- [x] **W-05 — Starlette/httpx2 deprecation warning resolved**: added a
  narrow `[tool.pytest.ini_options] filterwarnings` entry in
  `pyproject.toml` scoped to the exact
  `starlette.exceptions.StarletteDeprecationWarning` category and message
  prefix (not a blanket `DeprecationWarning` silence — verified that class
  actually subclasses `UserWarning`, not `DeprecationWarning`). Decision:
  do NOT migrate to `httpx2` this hackathon round — confirmed real
  (Pydantic's httpx continuation, released 2026-06-25) but migrating the
  whole test suite mid-hackathon is out of scope; documented as a
  disclosed, narrow suppression with rationale inline in `pyproject.toml`.
- [x] **W-06 — pre-demo regression script added**: `scripts/pre_demo_check.py`
  runs ruff, mypy --strict, bandit, pip-audit, the unit suite, and the
  e2e suite (same order as `.github/workflows/ci.yml`), then prints a
  PASS/FAIL summary table and a GO/NO-GO verdict with a non-zero exit
  code on any failure. Lint/type clean; individually verified each
  underlying check green (all-in-one combined run was flaky in this
  environment's terminal tool for very long chained commands — see
  session memory `testing-conventions.md` for the workaround).
- [x] **`presentation/slides.html` built**: self-contained, dependency-free
  9-slide HTML deck styled to match `promotions/X_STUDIO_X.png` /
  `X_STUDIO_X_ALT.png` (Variant A pink-bg/black-text, Variant B
  black-bg/pink-text, rose-gold `#B76E79` borders), sourced directly from
  `presentation/slides-outline.md`'s content, plain-JS keyboard/click
  navigation, no external dependencies.
- [x] **Final regression confirmed green**: 111 unit/integration tests
  passed (100.00% coverage, 640/640 statements, 0 warnings), 17 e2e tests
  passed (0 failures, 0 errors, 25.25s), ruff/mypy --strict/bandit/
  pip-audit all clean.
- [x] **Meta-project security propagation check** — CLOSED 2026-07-10.
  Investigated the parent `CodingStandardsRef` repo's own
  `.github/workflows/ci-security.yml`/`ci-cve-check.yml`: both are
  intentionally scoped to the parent repo's own `scripts/` tree (its
  internal CVE-tracking system, per `coding_stds/artifacts_cve_security_protection/`)
  and are unrelated to this submodule's Python package — no change
  needed there. This submodule already has its own complete,
  independently-triggered `.github/workflows/ci.yml` (ruff, mypy
  --strict, bandit, pip-audit, 111 unit tests, 17 e2e tests) that runs
  on every push/PR to `psi16181918161phi/engineering-studio-ai` — verified
  via `gh run list` to be genuinely green on GitHub (not just locally) as
  of the PR #9/#10 merges today. Security propagation is real and
  already fully wired; no further action required.

#### Current Todos (as of the final-sprint-freeze pass, 2026-07-10)

- [x] Merged teammate PR #9 (`paper/README.md`, Git LFS pointer-file
  documentation) and PR #10 (Variant B presentation CSS selector fix).
- [x] Rewrote `deployment/Dockerfile`/`docker-compose.yml`/`README.md` to
  cover all three runnable surfaces (dashboard/webapp+API, CLI, GUI),
  cross-platform (Windows/macOS/Linux via Docker Desktop/Engine).
- [x] **Docker build + run genuinely verified** (not just config-reviewed):
  `docker compose build dashboard` succeeded, container started, and
  `GET /api/health` returned `{"status":"ok"}`.
- [x] Re-verified full regression fresh today: 111 unit tests / 100%
  coverage, 17 e2e tests, ruff/mypy/bandit/pip-audit all clean — see
  updated `docs/E2E_EVIDENCE.md`.
- [x] Created `docs/JUDGES_GUIDE.md` — a standalone entry point linking
  the paper, whitepaper, slides, recorded screenshots/video, and test
  evidence, and linked it from the root `README.md`.
- [x] Closed the meta-project security propagation checkbox (see above).



### Role 5 — Frontend, Visualization & Demonstration

#### Responsibilities

Develop the user experience.

Possible work includes:

- Web UI
- Dashboard
- Visualization
- Simulation
- Logging viewer
- Deployment
- Demonstration environment

#### Deliverables

- Frontend
- Dashboard
- Visualizations
- Live demo

---

### Role 6 — Documentation, Paper & Presentation

#### Responsibilities

Produce all written and presentation materials.

Possible work includes:

- README
- Documentation
- Wiki
- LaTeX paper
- Presentation slides
- Demo script
- Demo video
- Submission materials

#### Deliverables

- README
- Technical paper
- Presentation
- Demo video
- Final submission package

---

## Workflow and Collaboration

### GitHub Workflow

Recommended branching strategy:

```
main
│
develop
│
feature/<feature-name>
```

Guidelines:

- Do not commit directly to `main`.
- Create feature branches.
- Open Pull Requests.
- Keep commits small and descriptive.
- Review before merging.

---

### Repository Structure

```
/
├── agents/
├── backend/
├── frontend/
├── docs/
├── prompts/
├── research/
├── security/
├── tests/
├── deployment/
├── demo/
├── scripts/
├── paper/
├── presentation/
└── README.md
```

---

### Communication

Recommended communication channels:

- GitHub Issues
- GitHub Discussions
- Discord


Use Issues for:

- Bugs
- Tasks
- Features
- Questions

---

### Daily Coordination

Suggested workflow:

1. Morning check-in
2. Pick issues
3. Work independently
4. Push frequently
5. Open Pull Requests
6. Evening integration

---

## Standards and Deliverables

### Coding Standards

Please:

- Write readable code.
- Document major functions.
- Keep modules small.
- Avoid unnecessary complexity.
- Test before pushing.
- Follow existing project conventions.

---

### Definition of Done

A task is considered complete when:

- Functionality works.
- Code builds successfully.
- Tests pass.
- Documentation is updated.
- Pull Request is approved.
- No known critical issues remain.

---

## Role Assignments

Please edit this table after selecting a role.

| Team Member | Selected Role |
|:------------|:--------------|
| Hadrian     | Orchestrator  |
| Member 2    |               |
| Member 3    |               |
| Member 4    |               |
| Member 5    |               |
| Member 6    |               |

Caption: Table 1 — Team Member Role Assignments

---

## Collaboration Principles

- Communicate early.
- Ask questions.
- Review each other's work.
- Keep commits frequent.
- Avoid duplicate work.
- Respect everyone's contributions.
- Focus on delivering a polished demonstration rather than an overly ambitious feature set.

---

## Final Goal

Build a compelling demonstration of an **AI Engineering Studio** that showcases collaborative AI-assisted engineering from concept to implementation, while demonstrating sound software engineering practices, documentation, testing, security, and presentation.

Let's build something we're proud to submit.

---

## Changelog

Caption: Table 2 — Document Revision History

| Version    | Date       | Author     | Description                                                                                              |
|:-----------|:-----------|:-----------|:----------------------------------------------------------------------------------------------------------|
| 2026.1.1.0 | 2026-07-09 | Hadrian Hu | Completed WISHLIST_2026-07-09_demo-one-more-round (W-01 through W-06): filled demo-script.md fallback plan and slides-outline.md placeholders; added demo rehearsal tooling, e2e evidence doc, a disclosed deprecation-warning filter, and a pre-demo regression script; built presentation/slides.html; confirmed full green regression (111 unit tests/100% coverage, 17 e2e tests/0 failures). |
| 2026.1.0.0 | 2026-07-05 | Hadrian Hu | Restructured document to conform to markdown documentation standards (front matter, TOC, Abstract, Keywords, Executive Summary, Changelog); fixed malformed Role Assignments table row. |
| 1.0.0      | 2026-07-04 | Hadrian Hu | Initial draft of team roles and responsibilities.                                                        |
