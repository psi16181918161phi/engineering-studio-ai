---
title: "Engineering Studio AI — Full Team Scaffolding & Ownership Zones"
author: Hadrian Hu
date: 2026-07-05
version: "0.2.0"
keywords:
  - ci-cd
  - color-palette
  - engineering-studio-ai
  - merge-conflict-avoidance
  - ownership-zones
  - scaffolding
  - team-onboarding
status: "Draft"
changelog:
  - version: "0.2.0"
    date: "2026-07-05"
    author: "Hadrian Hu"
    description: "Scaffolded README.md + barebones __init__.py for the eight new Role 3 subpackages (api, cli, decorators, exceptions, models, sdk, utils, webapp) under src/engineering_studio/; updated SS3.3."
  - version: "0.1.0"
    date: "2026-07-05"
    author: "Hadrian Hu"
    description: "Initial full-team scaffolding guide: per-role starter folders/files and ownership-zone table to minimize merge conflicts."
---
# Engineering Studio AI — Full Team Scaffolding & Ownership Zones

> **Start here.** This is the single "what do I actually create, and where"
> guide for every role. It complements — and does not replace —
> [`docs/RESPONSIBILITIES.md`](docs/RESPONSIBILITIES.md) (role definitions),
> [`docs/task-specs.md`](docs/task-specs.md) (Task Specification blocks),
> [`docs/TEAM_QA.md`](docs/TEAM_QA.md) (Q&A, palette, testing bar, phasing),
> and [`AGENTS.md`](AGENTS.md) (condensed engineering standards). Read this
> file first, then jump to your role's starter folder below.

---

## Table of Contents

- [Abstract](#abstract)
- [Keywords](#keywords)
- [Executive Summary](#executive-summary)
- [1. Why This Document Exists](#1-why-this-document-exists)
- [2. Ownership Zones (Merge-Conflict Avoidance)](#2-ownership-zones-merge-conflict-avoidance)
- [3. Per-Role Starter Scaffolding](#3-per-role-starter-scaffolding)
  - [3.1 Role 1 — Project Architect &amp; Technical Lead](#31-role-1--project-architect--technical-lead)
  - [3.2 Role 2 — AI Research &amp; Prompt Engineering](#32-role-2--ai-research--prompt-engineering)
  - [3.3 Role 3 — AI Pipeline &amp; Backend Engineering](#33-role-3--ai-pipeline--backend-engineering)
  - [3.4 Role 4 — Software Quality, Security &amp; DevOps](#34-role-4--software-quality-security--devops)
  - [3.5 Role 5 — Frontend, Visualization &amp; Demonstration](#35-role-5--frontend-visualization--demonstration)
  - [3.6 Role 6 — Documentation, Paper &amp; Presentation](#36-role-6--documentation-paper--presentation)
- [4. Shared-File Coordination Protocol](#4-shared-file-coordination-protocol)
- [5. Definition of Ready (Before You Open a PR)](#5-definition-of-ready-before-you-open-a-pr)
- [6. Standards Cross-Reference Index](#6-standards-cross-reference-index)
- [Changelog](#changelog)

---

## Abstract

This document scaffolds every remaining empty directory in the
`engineering-studio-ai` repository (`research/`, `frontend/`, `backend/`,
`deployment/`, `presentation/`, `demo/`, `agents/`) with a `README.md` and,
where safe to assume without over-committing to a framework choice,
starter files — so each of the six hackathon roles has a concrete,
non-empty folder to open on Day 0 instead of a blank page. It also
formalizes an **ownership-zone table**: which paths each role creates and
edits by default, which paths are shared and require a lightweight
coordination protocol, and which paths are read-only references for a
given role. The goal is to let six people work in parallel for a 5-day
hackathon with minimal merge conflicts, since each role's primary work
happens in its own directory.

## Keywords

ci-cd, color-palette, engineering-studio-ai, merge-conflict-avoidance,
ownership-zones, scaffolding, team-onboarding

## Executive Summary

**Objective:** Eliminate "what do I actually create?" as a blocker on Day
0 of the hackathon, and reduce merge conflicts by giving every role its
own directory to work in.

**Approach:** Map the six roles from `docs/RESPONSIBILITIES.md` onto the
repository's directory tree, fill every currently-empty top-level folder
with a `README.md` (ownership, expected deliverables, starter file list)
plus safe starter files (e.g. the locked color palette as CSS custom
properties for Role 5, a filled `research-findings.md` template for Role
2), and define a short shared-file coordination protocol for the small
number of files two roles must both touch (`docs/task-specs.md`,
`README.md`, `pyproject.toml`).

**Outcome:** Every role has a non-empty starting point and a documented
ownership zone; the number of files edited by more than one role is
reduced to three, each with an explicit coordination rule.

**Recommendations:** Read [Section 2](#2-ownership-zones-merge-conflict-avoidance)
before writing your first file. Keep PRs scoped to your own zone. If you
must touch a shared file, follow [Section 4](#4-shared-file-coordination-protocol).

---

## 1. Why This Document Exists

`docs/RESPONSIBILITIES.md` defines *who does what*. `SCAFFOLDING.md`
(this file) defines *where exactly the files go and what starter content
already exists*, so nobody has to guess a folder layout under time
pressure, and two people don't independently invent two different
structures for the same deliverable.

---

## 2. Ownership Zones (Merge-Conflict Avoidance)

| Zone (path)                                                         | Primary Owner                        | Notes                                                                                              |
| :------------------------------------------------------------------ | :----------------------------------- | :------------------------------------------------------------------------------------------------- |
| `research/`                                                       | Role 2 (Research)                    | Free to restructure internally; no other role writes here.                                         |
| `src/engineering_studio/`                                         | Role 3 (Backend)                     | Code lives here, not in root`backend/` or `agents/` (see §3.3, §3.6 notes below).            |
| `backend/`                                                        | Role 3 (Backend)                     | Reserved for optional additional services (e.g. a REST wrapper); empty is a valid end state.       |
| `agents/` (root)                                                  | Role 1 + Role 2 (design)             | Non-code agent**design notes** only — canonical code is `src/engineering_studio/agents/`. |
| `tests/`                                                          | Role 4 (QA/Security/DevOps)          | Role 3 may add tests for code they write; Role 4 owns coverage/CI enforcement.                     |
| `.github/workflows/`, `deployment/`                             | Role 4 (QA/Security/DevOps)          | CI pipeline + container/deploy manifests.                                                          |
| `frontend/`, `demo/`                                            | Role 5 (Frontend)                    | UI, dashboard, visualization, and the live demo script.                                            |
| `docs/` (except `task-specs.md`), `paper/`, `presentation/` | Role 6 (Docs/Paper)                  | README/wiki-equivalents, LaTeX paper, slide outline.                                               |
| `docs/task-specs.md`                                              | **Shared** Role 2 + Role 3     | See[§4](#4-shared-file-coordination-protocol) — heading-scoped edits only.                        |
| `docs/TEAM_QA.md`                                                 | **Shared** (any role adds Q&A) | Append-only additions under your own role's subsection; don't reformat other sections.             |
| Root`README.md`, `AGENTS.md`, `SCAFFOLDING.md`                | **Shared**, Role 1 approves    | Any role may propose an edit; Role 1 merges to avoid conflicting rewrites.                         |
| `pyproject.toml`, `requirements*.txt`                           | **Shared**, Role 4 approves    | Add your own dependency on its own line; Role 4 resolves conflicts/pins versions.                  |

**Rule of thumb:** if your change is entirely inside your zone, open a PR
without waiting for anyone. If it touches a shared file, follow §4 first.

---

## 3. Per-Role Starter Scaffolding

### 3.1 Role 1 — Project Architect & Technical Lead

No new folder — your workspace is the whole repo, plus PR review. Start
by reading `docs/RESPONSIBILITIES.md` §Definition of Done and this file's
§2 ownership table; keep both current as the team's structure evolves
(new file → append a row, never silently restructure someone else's zone).

### 3.2 Role 2 — AI Research & Prompt Engineering

Starter folder: [`research/`](research/README.md) — already contains a
`README.md`, a filled `research-findings.md` template, and a
`technology-comparisons.md` template. Fill in the `[SECTION INCOMPLETE — REQUIRES HUMAN INPUT]` placeholders; keep every claim tagged
`verified`/`unverified` with a `confidence` score per `docs/task-specs.md`
§2. Prompt templates you draft/iterate go in `research/prompt-drafts/`
first; once stable, promote the exact heading structure into
`docs/task-specs.md` per §4 below.

### 3.3 Role 3 — AI Pipeline & Backend Engineering

Code lives in `src/engineering_studio/` (already scaffolded: `agents/`,
`artifacts/`, `cli/`, `fireworks_client.py`, `task_specs.py`) — see
`README.md` §Repository layout. Root [`backend/`](backend/README.md) is
reserved for optional additional services only (e.g. a thin REST API
wrapper if the demo needs one) — do not duplicate `src/` content there.
Root [`agents/`](agents/README.md) is for non-code design notes, not
implementation.

Additional reserved subpackages have each been scaffolded with a
`README.md` + barebones `__init__.py` so they are non-empty starting
points (all currently placeholders — populate only what the demo needs):
[`api/`](src/engineering_studio/api/README.md) (HTTP/WebSocket routes),
[`cli/`](src/engineering_studio/cli/README.md) (future CLI subcommands),
[`decorators/`](src/engineering_studio/decorators/README.md)
(retry/timing/logging decorators),
[`exceptions/`](src/engineering_studio/exceptions/README.md) (shared
error hierarchy), [`models/`](src/engineering_studio/models/README.md)
(`pydantic` schemas), [`sdk/`](src/engineering_studio/sdk/README.md)
(in-process programmatic client), [`utils/`](src/engineering_studio/utils/README.md)
(pure helper functions), and [`webapp/`](src/engineering_studio/webapp/README.md)
(app instance mounting `api/` routes). Each folder's `README.md` states
why it's currently empty being a valid end state, and what it should
contain if populated — do not leave a populated file without updating
its folder's `README.md` "current status" note.

### 3.4 Role 4 — Software Quality, Security & DevOps

Starter folders: `tests/` (already has 3 test files — add more following
the same mocked-client pattern), `.github/workflows/ci.yml` (already
runs ruff/mypy/pytest — extend with coverage gate and `pip-audit`/bandit
per `docs/TEAM_QA.md` §5), and the new
[`deployment/`](deployment/README.md) folder (starter `Dockerfile` and
`docker-compose.yml` provided).

### 3.5 Role 5 — Frontend, Visualization & Demonstration

Starter folder: [`frontend/`](frontend/README.md) — contains a
`styles/theme.css` with the three **locked** colors (`#FFAEC9`,
`#000000`, `#B76E79`) as CSS custom properties, ready to import into
whatever framework you choose (framework choice is intentionally left to
you — not prescribed here). [`demo/`](demo/README.md) has a
`demo-script.md` template mapped to the Demo Flow sequence diagram in the
project vision doc.

### 3.6 Role 6 — Documentation, Paper & Presentation

`docs/` (this file, `RESPONSIBILITIES.md`, `TEAM_QA.md`, `task-specs.md`)
and `paper/engineering_studio_ai_paper.tex` already exist. New starter
folders: [`presentation/`](presentation/README.md) (slide outline
template) and `demo/demo-script.md` (co-owned with Role 5 — you write the
narration, Role 5 wires the live actions).

---

## 4. Shared-File Coordination Protocol

Only three files are genuinely shared. For each:

1. **`docs/task-specs.md`** — Role 2 and Role 3 both edit this file, but
   only within the `## N. <Stage Title>` block they own. Never reformat
   another stage's block. Adding a brand-new stage = a brand-new `## N.`
   heading appended at the end, never inserted mid-file (avoids line-shift
   diff conflicts).
2. **`docs/TEAM_QA.md`** — any role may add a new row to their own
   `### 3.x Role N` table, or a new numbered section at the end. Don't
   rewrite another role's existing rows.
3. **Root `README.md` / `AGENTS.md` / `SCAFFOLDING.md`** — propose edits
   via PR; Role 1 merges. If two PRs touch the same table, the second one
   rebases rather than force-pushing over the first.

For `pyproject.toml`/`requirements*.txt`: add your dependency on its own
line, in alphabetical order within its section, and let Role 4 resolve
any version conflicts in one follow-up commit rather than everyone
editing pins independently.

---

## 5. Definition of Ready (Before You Open a PR)

- [ ] Change is entirely inside your ownership zone, OR followed the §4
  protocol for a shared file.
- [ ] No secrets committed (`.env` stays gitignored — see `AGENTS.md` §8).
- [ ] New Markdown files follow the front-matter/TOC/Abstract/Keywords/
  Executive-Summary/Changelog structure (see any file in this repo as
  a template, e.g. this one).
- [ ] New Python files have WHAT/WHY/HOW docstrings (`AGENTS.md` §4) and
  pass `ruff check` / `mypy` locally.
- [ ] Commit message is small and descriptive (`docs/RESPONSIBILITIES.md`
  §GitHub Workflow).

---

## 6. Standards Cross-Reference Index

| Topic                                     | Source                                                                                          |
| :---------------------------------------- | :---------------------------------------------------------------------------------------------- |
| Role definitions, Definition of Done      | `docs/RESPONSIBILITIES.md`                                                                    |
| Task Specification blocks (exact prompts) | `docs/task-specs.md`                                                                          |
| Per-role Q&A, color palette, testing bar  | `docs/TEAM_QA.md`                                                                             |
| Condensed engineering standards           | `AGENTS.md`                                                                                   |
| Full internal standards corpus (private)  | `coding_stds/` in the parent `CodingStandardsRef` repo (team members only, not public)      |
| Original hackathon vision/rationale       | `VISION_AMD_LABLAB_HACKATHON_ENGINEERING_STUDIO.md` (private repo, linked from `README.md`) |

---

## Changelog

| Version | Date       | Author     | Description                                                                                                                                                                              |
| :------ | :--------- | :--------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.0   | 2026-07-05 | Hadrian Hu | Scaffolded README.md + barebones `__init__.py` for the eight new Role 3 subpackages (`api`, `cli`, `decorators`, `exceptions`, `models`, `sdk`, `utils`, `webapp`) under `src/engineering_studio/`; updated §3.3. |
| 0.1.0   | 2026-07-05 | Hadrian Hu | Initial full-team scaffolding guide and ownership-zone table.                                                                                                                            |
