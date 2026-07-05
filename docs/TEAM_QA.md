---
title: "Engineering Studio AI — Team Q&A, Standards Emphasis & Phased Timeline"
author: Hadrian Hu
date: 2026-07-05
version: "0.2.0"
keywords:
  - api-key-hygiene
  - color-palette
  - engineering-studio-ai
  - hackathon-phasing
  - qa-reference
  - secdevops
  - team-roles
  - testing-standards
status: "Draft"
changelog:
  - version: "0.2.0"
    date: "2026-07-05"
    author: "Hadrian Hu"
    description: "Initial public Team Q&A reference: Role 2 clarification, per-role Q&A, mandatory color palette, 100%-coverage testing standard, SecDevOps/API-key hygiene, and a 4.5-day phased timeline."
---
# Engineering Studio AI — Team Q&A, Standards Emphasis & Phased Timeline

> **Read this before pinging the team lead.** This document exists so that
> every teammate can self-serve answers about deliverables, standards, and
> the schedule. If your question isn't answered here, ask in GitHub
> Discussions/Issues so the answer can be added back into this file for
> everyone else.

---

## Table of Contents

- [Abstract](#abstract)
- [Keywords](#keywords)
- [Executive Summary](#executive-summary)
- [1. How To Use This Document](#1-how-to-use-this-document)
- [2. Role 2 Clarification — AI Research &amp; Prompt Engineering](#2-role-2-clarification--ai-research--prompt-engineering)
- [3. Per-Role Q&amp;A](#3-per-role-qa)
  - [3.1 Role 1 — Project Architect &amp; Technical Lead](#31-role-1--project-architect--technical-lead)
  - [3.2 Role 2 — AI Research &amp; Prompt Engineering](#32-role-2--ai-research--prompt-engineering)
  - [3.3 Role 3 — AI Pipeline &amp; Backend Engineering](#33-role-3--ai-pipeline--backend-engineering)
  - [3.4 Role 4 — Software Quality, Security &amp; DevOps](#34-role-4--software-quality-security--devops)
  - [3.5 Role 5 — Frontend, Visualization &amp; Demonstration](#35-role-5--frontend-visualization--demonstration)
  - [3.6 Role 6 — Documentation, Paper &amp; Presentation](#36-role-6--documentation-paper--presentation)
- [4. Mandatory Color Palette (Frontend / Visualization)](#4-mandatory-color-palette-frontend--visualization)
- [5. Testing Standard — 100% Coverage, 100% Pass, No Hallucinations](#5-testing-standard--100-coverage-100-pass-no-hallucinations)
- [6. Security, SecDevOps &amp; API Key Hygiene](#6-security-secdevops--api-key-hygiene)
- [7. Clean Code Hygiene](#7-clean-code-hygiene)
- [8. Recommended Phased Timeline (5-Day Hackathon, 4.5-Day Active Build)](#8-recommended-phased-timeline-5-day-hackathon-45-day-active-build)
- [9. Answers Pulled From the Formal Paper](#9-answers-pulled-from-the-formal-paper)
- [10. Standards Reference Index](#10-standards-reference-index)
- [Changelog](#changelog)

---

## Abstract

This document is the single public Q&A reference for the Engineering
Studio AI hackathon team, created to reduce synchronous back-and-forth
during a time-constrained, five-day build. It clarifies the exact
deliverables for each of the six team roles defined in
`docs/RESPONSIBILITIES.md` — most immediately, Role 2 (AI Research &
Prompt Engineering) — enumerates the mandatory visual color palette for
any frontend or visualization surface, restates the project's testing bar
(100% coverage, 100% pass, end-to-end security validation, zero
hallucinated results), and lays out API-key hygiene and general
SecDevOps hygiene expected of every role. It closes with a 4.5-day active
build schedule (of the 5-day hackathon window) broken down per role, with
the remaining half day reserved as buffer for validation, verification,
approvals, and final presentation. Answers are grounded in
`docs/RESPONSIBILITIES.md`, `docs/task-specs.md`, `AGENTS.md`, and the
project's internal formal paper (`paper/engineering_studio_ai_paper.tex`).
No new commitments are invented beyond what those source documents already
establish; anywhere a firm answer isn't yet decided, this document says so
explicitly rather than guessing.

---

## Keywords

api-key-hygiene, color-palette, engineering-studio-ai, hackathon-phasing,
qa-reference, secdevops, team-roles, testing-standards

---

## Executive Summary

**Objective:** Give every team member a single, authoritative,
self-service place to find deliverable definitions, standards, and
schedule — instead of asking the team lead individually.

**Approach:** Answer Role 2's specific clarification question first
(research deliverables are not "Markdown-only" — implementation-adjacent
artifacts are also in scope), then provide a full per-role Q&A table,
restate the mandatory `#FFAEC9` / `#000000` / `#B76E79` color palette for
any visual surface, restate the project's testing bar in full (unit,
integration, sub-system, performance, correctness, security, and
vulnerability testing, with 100% coverage and 100% pass required, and the
whole running program validated end-to-end for security — not just unit
level), and restate SecDevOps/API-key hygiene rules. A 4.5-day phased
timeline (of the 5-day hackathon) is proposed per role, with a reserved
half day for validation, verification, sign-off, and presentation
rehearsal.

**Outcome:** A durable, linkable reference (`docs/TEAM_QA.md`) that
answers the recurring questions once, in public, for the whole team.

**Recommendations:** Every role should read Sections 3-7 fully before
Day 1 kickoff, set up and verify their own API key locally per Section 6
before writing any code that calls Fireworks AI, and treat the Section 8
timeline as a target to adapt — not a rigid mandate — while keeping the
team lead informed of any slippage as early as possible.

---

## 1. How To Use This Document

1. Search this file (Ctrl+F / Cmd+F) for your role name or your question's
   keyword before asking in chat.
2. If your question isn't answered here, open a GitHub Issue or
   Discussion — the answer, once given, should be added back into this
   file (any teammate may open a PR to do so).
3. This document does not replace `docs/RESPONSIBILITIES.md` (canonical
   role definitions), `docs/task-specs.md` (exact Task Specification
   blocks each agent call uses), or `AGENTS.md` (condensed engineering
   standards) — it cross-references all three and adds the answers that
   were previously only given verbally.

---

## 2. Role 2 Clarification — AI Research & Prompt Engineering

**Question asked:** *"Will Role 2 mainly work on Markdown/text files
(`research-findings.md`, prompt files), or are there other files and
implementation tasks involved?"*

**Answer:** Both. Role 2's **primary** deliverables are text/Markdown, but
the role is not limited to prose:

| Deliverable            | File(s)                                       | Format                                                                                                                                                                                                                                                                                                                                                     |
| :--------------------- | :-------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Research findings      | `research/` (e.g. `research-findings.md`) | Markdown, per the Task Specification in`docs/task-specs.md` §2 (Research Problem-Analysis Pass): every claim tagged `verified`/`unverified` with a `confidence` score — never stated as fact without a source                                                                                                                                    |
| Technology comparisons | `research/`                                 | Markdown tables (AMD hardware/software options, model choices, agent frameworks, benchmarking notes)                                                                                                                                                                                                                                                       |
| Prompt templates       | `prompts/` and `docs/task-specs.md`       | Markdown files containing the actual Task Specification blocks consumed at runtime by`engineering_studio/task_specs.py` — **this is code-adjacent**, not free-form prose: the exact heading structure, `Allowed Files`, `Forbidden Files`, `Expected Outputs`, and `SCOPE Declaration` fields must be preserved or Role 3's parser breaks |
| Design recommendations | `research/` or inline in an Issue           | Markdown                                                                                                                                                                                                                                                                                                                                                   |

**Is there implementation work?** Yes, in two forms:

1. **Prompt-engineering-as-code.** Every prompt template Role 2 writes is
   parsed programmatically (`task_specs.py`). Getting the Markdown
   structure exactly right (heading levels, fenced code block, required
   fields) *is* an implementation task, even though the artifact is a
   `.md` file — a malformed heading breaks the pipeline for every other
   role.
2. **Optional light Python.** If time allows and Role 2 is comfortable,
   writing or reviewing the small parsing/validation logic in
   `src/engineering_studio/task_specs.py` (e.g. adding a schema check that
   a Task Specification block has all required fields) is welcome and
   falls naturally out of owning the prompt templates it parses — but it
   is **not required**; Role 3 owns that file by default.

**Bottom line:** expect to spend most of your time in Markdown, but treat
your prompt template files as a contract with the backend, not casual
notes — malformed structure is a shipped bug, not a documentation nit.

---

## 3. Per-Role Q&A

### 3.1 Role 1 — Project Architect & Technical Lead

| Q                             | A                                                                                                                                            |
| :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| Do I write code?              | Optional/as-needed. Primary job is architecture decisions, PR review, final merge approval, and keeping the team on schedule (Section 8).    |
| What's my Definition of Done? | Every merged PR meets`docs/RESPONSIBILITIES.md` §Definition of Done; the repository stays in a demoable state at every `develop` merge. |
| Do I set up CI?               | You own the decision of*what* CI enforces; Role 4 implements the pipeline itself.                                                          |

### 3.2 Role 2 — AI Research & Prompt Engineering

See [Section 2](#2-role-2-clarification--ai-research--prompt-engineering)
above for the full answer.

| Q                                         | A                                                                                                                                                              |
| :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do I need to write tests?                 | Not test*code*, but every factual/benchmark claim in `research-findings.md` needs a source or an explicit `unverified` tag — that IS your quality gate. |
| Who consumes my prompt templates?         | Role 3's backend (`task_specs.py` parses `docs/task-specs.md` at runtime) and every specialist agent call.                                                 |
| Can I suggest AMD-specific optimizations? | Yes — that is explicitly in scope ("AMD technologies" in`docs/RESPONSIBILITIES.md` §Role 2).                                                               |

### 3.3 Role 3 — AI Pipeline & Backend Engineering

| Q                                         | A                                                                                                                                                                                                                                              |
| :---------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What's the artifact-write contract?       | Each specialist agent writes**only** to its own `src/engineering_studio/artifacts/<discipline>/` folder — see `AGENTS.md` §3 (SCOPE control) and §2 (ACID-lite for artifact writes: write-to-temp-then-rename, no partial files). |
| Which model provider?                     | Fireworks AI (`fireworks_client.py`), with a local-llama fallback per `AGENTS.md` §2 ("model routing, never single-vendor hard-coded").                                                                                                   |
| Do I need live network calls in tests?    | No — tests use a mocked Fireworks client (`tests/test_fireworks_client.py` pattern); no live network calls in CI.                                                                                                                           |
| Where do I get the exact prompts to send? | `docs/task-specs.md`, authored/maintained with Role 2.                                                                                                                                                                                       |

### 3.4 Role 4 — Software Quality, Security & DevOps

| Q                                                   | A                                                                                                                                                                                                                               |
| :-------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| What coverage bar do I enforce?                     | 100% coverage, 100% pass — see[Section 5](#5-testing-standard--100-coverage-100-pass-no-hallucinations). This is non-negotiable for the final submission commit.                                                                |
| What security scans are required?                   | Static analysis (lint/type-check), dependency vulnerability scan (`pip-audit` or equivalent per `AGENTS.md` §8), and a secrets scan before every push (see [Section 6](#6-security-secdevops--api-key-hygiene)).            |
| Do I test the whole running program, or just units? | Both — see[Section 5](#5-testing-standard--100-coverage-100-pass-no-hallucinations): unit, integration, sub-system, performance, correctness, security, and vulnerability testing, plus an end-to-end run of the full pipeline. |
| Where does CI live?                                 | `.github/workflows/ci.yml`.                                                                                                                                                                                                   |

### 3.5 Role 5 — Frontend, Visualization & Demonstration

| Q                                     | A                                                                                                                                                           |
| :------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What colors am I allowed to use?      | **Only** `#FFAEC9`, `#000000`, `#B76E79` — see [Section 4](#4-mandatory-color-palette-frontend--visualization). No other inline color literals. |
| Where do palette values live in code? | A single centralized palette/config module (constants only) — never hard-coded per-component.                                                              |
| What about contrast/accessibility?    | WCAG 2.1 AA contrast is mandatory for every foreground/background pairing you use from this palette (verify before shipping a screen).                      |
| Can I add a 4th color?                | Not without team-lead approval — the palette is intentionally locked for visual consistency across the whole demo.                                         |

### 3.6 Role 6 — Documentation, Paper & Presentation

| Q                                                        | A                                                                                                                                                                                                                                                                                                                  |
| :------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What format do docs follow?                              | `coding_stds/documentation/markdown_standards.txt` conventions: YAML front matter, TOC, Abstract, Keywords, Executive Summary, body, Changelog — this very document follows that format.                                                                                                                        |
| Is the LaTeX paper still being worked on?                | Yes —`paper/engineering_studio_ai_paper.tex` is a formal model/proofs paper (see [Section 9](#9-answers-pulled-from-the-formal-paper)).                                                                                                                                                                          |
| Do I need to understand the math proofs to present them? | At a summary level, yes — you don't need to re-derive the proofs, but you should be able to state the four proved properties (acyclicity, bounded rework termination, minimum agent multiplicity, trust-tier safety) and that a fifth (token/cost convergence) is an explicitly labeled sketch, not a full proof. |

---

## 4. Mandatory Color Palette (Frontend / Visualization)

Per `coding_stds/visualization/aesthetic_standards.txt` (this project's
single source of truth for all visual surfaces), the palette for this
hackathon build is **locked** to exactly three colors:

| Constant                    | Hex         | Use                                                       |
| :-------------------------- | :---------- | :-------------------------------------------------------- |
| `PALETTE_PRIMARY_PINK`    | `#FFAEC9` | Foreground **or** background — soft rose pink     |
| `PALETTE_BASE_BLACK`      | `#000000` | Background**or** foreground — near-black           |
| `PALETTE_ACCENT_ROSEGOLD` | `#B76E79` | Accent elements only (highlights, active states, borders) |

Rules:

1. **No inline hex/RGB/named-color literals** in any component, plot
   function, or stylesheet — reference the three named constants above
   from a single centralized palette module.
2. **Pick one role per color per surface** and stay consistent: e.g. if a
   given screen uses black background + pink foreground text, don't flip
   the pairing mid-screen.
3. **Contrast is mandatory, not optional.** Verify WCAG 2.1 AA contrast
   for whichever foreground/background pairing you choose before treating
   a screen as done — pink-on-black and black-on-pink both need a
   contrast check, they are not automatically compliant just because
   they're on the approved list.
4. **Rose gold (`#B76E79`) is accent-only** — do not use it as a primary
   background or as body text color; it is for borders, active-state
   highlights, icons, or small accent details.
5. Applies to: any web UI, dashboard, exported chart/diagram, CLI color
   output (where the terminal supports it), and any embedded
   visualization in the documentation/paper/presentation.

---

## 5. Testing Standard — 100% Coverage, 100% Pass, No Hallucinations

The project's testing bar is deliberately strict for a hackathon
submission, because the demo is judged on more than "it ran once":

1. **Coverage: 100%.** Every module under `src/engineering_studio/` must
   reach full statement/branch coverage before the final submission
   commit. Partial coverage is treated as an unfinished task, not "good
   enough."
2. **Pass rate: 100%.** No skipped, `xfail`, or flaky tests in the final
   suite. A flaky test is a bug in the test (or the code under test), not
   something to silence with a retry loop.
3. **Test layers required — not just unit tests:**
   - **Unit tests** — every function/class in isolation, mocked
     dependencies (no live Fireworks calls).
   - **Integration tests** — specialist agents writing to their real
     artifact folders end-to-end through the orchestrator.
   - **Sub-system tests** — each major subsystem (backend orchestration,
     frontend dashboard, CLI) validated as a unit, not just its parts.
   - **Performance tests** — the full pipeline run against a
     representative product brief, with a stated acceptable latency
     budget.
   - **Correctness tests** — output artifacts match the Task
     Specification's `Expected Outputs` contract exactly (right files, in
     the right folders, with the right required fields).
   - **Security tests** — see below; not optional, not "if time allows."
   - **Vulnerability testing** — dependency CVE scanning
     (`pip-audit`/equivalent) and, for anything web-facing (Role 5), basic
     input-sanitization checks.
4. **The entire running program must be validated end-to-end for
   security** — not merely its individual units. This means: run the full
   CLI/pipeline against representative and adversarial inputs (e.g. a
   product brief attempting prompt injection, a malformed Task
   Specification) and confirm the system fails safely (explicit error,
   never silent fabrication, never a leaked secret in logs or output).
5. **No hallucinations.** Any AI-agent-produced claim (a benchmark number,
   a vendor part number, a legal/compliance statement) must either be
   sourced/verified or explicitly flagged `unverified`/
   `requires_human_review: true`. This applies to Role 2's research notes,
   Role 3's specialist outputs, and Role 6's paper/presentation content
   equally.
6. **Relevant standards (private corpus, names only — see
   `coding_stds/testing/`):** `test_coverage_100_pct_standards.txt`,
   `unit_testing_standards.txt`, `integration_testing_standards.txt`,
   `end_to_end_testing_standards.txt`, `performance_profiling_standards.txt`,
   `security_testing_standards.txt`, `vulnerability_testing_standards.txt`,
   `regression_testing_standards.txt`, `test_automation_standards.txt`.
   These are internal references for the team lead/Role 4 — this repo's
   public `AGENTS.md` restates only what applies here, per the existing
   condensation convention.

---

## 6. Security, SecDevOps & API Key Hygiene

**Reminder to every role, frontend, backend, and otherwise:**

1. **Set up your own local API key before Day 1 coding starts.**
   - Copy `.env.example` to `.env` and fill in your own
     `FIREWORKS_API_KEY` locally.
   - `.env` is gitignored — **never** commit it, never paste a real key
     into an Issue, PR description, commit message, chat log, or this
     Q&A document.
   - Before every `git add`/commit, visually confirm `.env` and any
     personal credential file are not staged (`git status`); Role 4 should
     also run a secrets scan before merge (see
     `coding_stds/artifacts_cve_security_protection/ gitguardian_check_before_git_actions_standards.txt` — internal
     reference; a GitGuardian-style pre-push secret scan is the practical
     takeaway).
   - If a key is ever accidentally committed: **rotate it immediately**
     (regenerate in the Fireworks dashboard) and notify the team lead —
     do not just delete the commit and assume the key is safe, since it
     may already be in the remote history.
2. **Clean code hygiene** (see [Section 7](#7-clean-code-hygiene) for the
   full list) applies to every role, not just backend.
3. **SecDevOps fundamentals for this project:**
   - **Shift-left security** — run lint/type-check/security scans locally
     before pushing, not only in CI.
   - **Least privilege** — don't request repo/API scopes broader than the
     task needs.
   - **Dependency pinning** — pin versions in `requirements.txt`; run
     `pip-audit` (or equivalent) before the final submission commit.
   - **No secrets in source, ever** — this includes example configs;
     `.env.example` must only ever contain placeholder/empty values.
   - **Input validation** — any user-supplied text (the product brief,
     any web form field on the frontend) is sanitized/validated before it
     is interpolated into a prompt template or rendered in the UI (basic
     injection hygiene, both prompt-injection and XSS-style).
   - **Fail safely and loudly** — a failed/rate-limited Fireworks AI call
     must surface as an explicit error, never a silently fabricated
     "success."
4. This applies equally to **frontend** (Role 5 — never leak an API key
   into client-side JS or a public build artifact), **backend** (Role 3 —
   never log the key, never echo it in an error message), and **DevOps**
   (Role 4 — CI secrets go in GitHub Actions encrypted secrets, never in
   the workflow YAML itself).

---

## 7. Clean Code Hygiene

Restated for every role (from `AGENTS.md` §1-§4, condensed further here):

1. **Small, single-purpose modules** — one specialist/component per file.
2. **SOLID** applied pragmatically: one responsibility per module, extend
   via new files rather than rewriting shared dispatch logic, deterministic
   and mockable glue code.
3. **WHAT / WHY / HOW** in every non-trivial docstring — what it does, why
   it exists, how it's implemented at a reviewable level.
4. **No dead code, no commented-out blocks left in a merged PR.**
5. **Keep PRs small and frequent** — easier to review under a hackathon
   deadline than one giant end-of-day PR.
6. **Structured logging** (JSON lines: `level`, `agent`, `task_id`,
   `message`, `timestamp`) for anything running unattended during the
   demo — never a bare `print()` for anything you'd need to debug later.

---

## 8. Recommended Phased Timeline (5-Day Hackathon, 4.5-Day Active Build)

The hackathon window is **5 days**. To leave a real buffer for final
integration issues, validation/verification, sign-off, and presentation
rehearsal, active build work is compressed to **4.5 days**, with the
remaining **0.5 day** reserved as buffer (Day 5 afternoon).

| Phase                                          | Timing                      | Role 1 (Architect)                                                                      | Role 2 (Research)                                                                   | Role 3 (Backend)                                                          | Role 4 (QA/Security/DevOps)                                                                                                          | Role 5 (Frontend)                                                                  | Role 6 (Docs/Paper)                                                             |
| :--------------------------------------------- | :-------------------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- | :------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **Phase 0 — Kickoff & Setup**           | Day 1 AM (0.5d)             | Finalize architecture, create Issues, confirm role table in`docs/RESPONSIBILITIES.md` | Set up local API key; draft initial technology comparison outline                   | Set up local API key; scaffold repo/venv; confirm CI skeleton runs        | Set up CI skeleton (`ci.yml`); confirm secrets scanning locally                                                                    | Set up local dev environment; confirm palette constants module stub                | Set up doc scaffolding; confirm this Q&A +`RESPONSIBILITIES.md` are current   |
| **Phase 1 — Research & Scaffolding**    | Day 1 PM – Day 2 AM (1d)   | Review incoming research; unblock architecture questions                                | Deliver`research-findings.md` (v1) + first Task Specification prompt drafts       | Scaffold orchestrator + specialist base class + Fireworks client (mocked) | Write first unit test scaffolds; confirm coverage tooling wired up                                                                   | Scaffold dashboard shell using the mandatory palette; no real data yet             | Draft README/architecture doc updates; outline paper sections                   |
| **Phase 2 — Core Implementation**       | Day 2 PM – Day 3 PM (1.5d) | Review PRs continuously; resolve integration conflicts                                  | Finalize prompt templates for all specialists; support Role 3 on parsing edge cases | Implement full orchestration + all specialist agent calls end-to-end      | Write integration + sub-system tests as features land; run security scans continuously                                               | Wire dashboard to real backend outputs; implement visualizations per palette rules | Draft demo script; continue paper formalization; document each finished feature |
| **Phase 3 — Integration & Hardening**   | Day 4 (1d)                  | Approve final integration PRs; confirm demoable state on`develop`                     | Verify all research claims are sourced/flagged; final technology comparison pass    | Fix integration bugs from Role 4's findings; performance pass             | Run full test matrix (unit/integration/sub-system/performance/correctness/security/vulnerability); drive to 100% coverage, 100% pass | Polish UI/UX, accessibility contrast check, finalize demo flow                     | Finalize README, paper draft, presentation outline                              |
| **Phase 4 — Final Validation & Buffer** | Day 5 AM (0.5d)             | Final go/no-go review; confirm every Definition of Done item                            | Final fact-check pass on research/paper claims                                      | Final bug triage only — no new features                                  | Final CI green run; final secrets scan; sign off on 100%/100% bar                                                                    | Final demo dry run on target hardware/screen                                       | Finalize presentation slides + demo script                                      |
| **Buffer — Reserved**                   | Day 5 PM (0.5d)             | Contingency for any last-minute blocker; final submission                               | —                                                                                  | —                                                                        | On-call for any last-minute CI break                                                                                                 | On-call for any last-minute UI break                                               | Submit final package; present                                                   |

Notes:

- This table is a **recommendation**, not a rigid mandate — adapt as
  actual progress dictates, but raise slippage to Role 1 as early as
  possible so the buffer is used deliberately, not consumed by surprise.
- The 0.5-day buffer (Day 5 PM) is explicitly reserved for validation,
  verification, approvals, and presentation — do not schedule new feature
  work into it.
- Every role should treat Phase 3 (Day 4) test/security results as a hard
  gate: known-failing tests or unresolved security findings block
  Phase 4 sign-off, not just a "nice to fix."

---

## 9. Answers Pulled From the Formal Paper

From `paper/engineering_studio_ai_paper.tex` (the internal formal
model/proofs paper — relevant for Role 6 and anyone asked to explain the
architecture's rigor to judges):

1. **What is formally proved?** Four properties, each a full proof: (1)
   **Acyclicity** of the nominal workflow graph, (2) **Bounded rework
   termination** (any run reaches `Approved` or an explicit
   circuit-breaker escalation within a bounded number of steps), (3)
   **Minimum agent-instance multiplicity** (at least 4 distinct agent
   instances are required to cover the four mandatory, mutually
   conflicting functions on one artifact — proved tight via a matching
   construction), and (4) **Trust-tier safety invariant preservation**
   (subagent-returned content stays untrusted, T-3, unless and until an
   explicit Quality Gate `Approved` certificate is issued for it).
2. **What is explicitly a sketch, not a full proof?** A fifth property —
   **token/cost invocation-count convergence** — is disclosed as a
   non-constructive sketch because a full proof would require inventing a
   per-agent token-cost probability distribution not specified anywhere
   in the governing documents; the paper deliberately does not fabricate
   that distribution.
3. **What grounds every definition/proof?** Five internal vision
   documents plus the `coding_stds/` corpus (SOLID, JPL/NASA Power of Ten,
   ACID, and the mathematical proof-structure standard itself) — no
   invented axioms.
4. **Why does this matter for the demo?** It gives Role 6 a rigorous,
   citable answer if a judge asks "how do you know this multi-agent
   system won't loop forever or silently trust a compromised sub-agent
   output" — the paper's Theorems 1, 2, and 4 answer exactly that.
5. **Scope disclaimer to repeat if asked:** the AMD LabLabAI hackathon
   instantiation is **simulation/emulation only** for any hardware
   discipline (Mechanical/Electrical/Firmware/Simulation) — no physical
   fabrication is claimed, since no physical hardware access is available
   in this environment.

---

## 10. Standards Reference Index

This repo's public `AGENTS.md` is the condensed, self-contained standards
reference for contributors — read it first. The private corpus names
below are cited for the team lead/Role 4's benefit (internal repo access
only); this public repo does not reproduce their full text, consistent
with the existing condensation approach described in `AGENTS.md` §"Why
this repo is separate from our standards corpus."

| Topic                       | Public reference (this repo)                                             | Internal reference (private corpus, name only)                                                                                                                                                                                  |
| :-------------------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Code structure / SOLID / FP | `AGENTS.md` §1-2                                                      | `coding_stds/documentation/markdown_standards.txt`, general SOLID/JPL sources                                                                                                                                                 |
| SCOPE control               | `AGENTS.md` §3                                                        | `docs/task-specs.md` Task Specification blocks                                                                                                                                                                                |
| Documentation format        | This file's own front matter/TOC/Abstract structure                      | `coding_stds/documentation/markdown_standards.txt`                                                                                                                                                                            |
| Aesthetics / color palette  | [Section 4](#4-mandatory-color-palette-frontend--visualization)           | `coding_stds/visualization/aesthetic_standards.txt`                                                                                                                                                                           |
| Testing (100% bar)          | [Section 5](#5-testing-standard--100-coverage-100-pass-no-hallucinations) | `coding_stds/testing/test_coverage_100_pct_standards.txt` and the full `coding_stds/testing/` catalog                                                                                                                       |
| Security / SecDevOps        | [Section 6](#6-security-secdevops--api-key-hygiene)                       | `coding_stds/devops/security_devsecops_standards.txt`, `coding_stds/devops/shift_left_security_standards.txt`, `coding_stds/devops/secrets_credentials_standards.txt`, `coding_stds/artifacts_cve_security_protection/` |
| Logging & observability     | `AGENTS.md` §7                                                        | `coding_stds/operations/logging_observability_standards.txt`                                                                                                                                                                  |

---

## Changelog

Caption: Table — Document Revision History

| Version | Date       | Author     | Description                                                                                                                                                                                                                                                                                                                                                            |
| :------ | :--------- | :--------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.0   | 2026-07-05 | Hadrian Hu | Initial public Team Q&A: Role 2 clarification, full per-role Q&A, mandatory`#FFAEC9`/`#000000`/`#B76E79` palette, 100%-coverage/100%-pass testing standard with end-to-end security validation, API-key hygiene and SecDevOps reminders, clean-code hygiene, 4.5-day phased timeline with 0.5-day buffer, and a summary of the formal paper's proved properties. |
