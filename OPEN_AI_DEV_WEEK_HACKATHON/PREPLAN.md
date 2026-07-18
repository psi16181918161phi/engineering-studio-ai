---
title: "PREPLAN — OpenAI Hackathon Narrow-Scope Bridge"
author: "Hadrian Hu"
date: "2026-07-17"
version: "0.1.0"
keywords: ["preplan", "openai-hackathon", "scope", "engineering-studio-ai"]
status: "Draft"
---
<!--
WHAT: Bridges INVESTIGATE.md's findings into a plannable shape — goals,
non-goals, constraints, success criteria, open questions requiring the
user before PLAN.md's tasks can be executed.
WHY: PLAN.md should not be written against unresolved unknowns (Section 4
of INVESTIGATE.md). This file makes those unknowns explicit and proposes
a default/fallback so a lower-intelligence executor is never blocked.
HOW: Every open question has a stated default. If the user never answers,
PLAN.md/PROMPT.md proceed with the default and disclose that they did.
-->

# PREPLAN — OpenAI Hackathon Narrow-Scope Bridge

## 1. Goal (single sentence)

Fill the 12 empty `.github/agents/` subdirectories with a small, narrowly
scoped set of new agent files, and wire a second (OpenAI-provider) model
routing profile through the existing API/UI/CLI/SDK/TUI surfaces — without
disturbing the AMD LabLabAI Hackathon submission already in place.

## 2. Non-goals (explicit, to keep scope narrow)

- Do **not** rewrite `docs/JUDGES_GUIDE.md`, `README.md`, `paper/`, or
  `presentation/` (AMD-hackathon-owned artifacts).
- Do **not** remove Fireworks AI support — both providers coexist.
- Do **not** attempt to fill `domain-specialists/{hardware,middleware, scripting,software}/` with more than one narrowly-justified file each
  (Section 6 of INVESTIGATE.md flagged these as ungrounded-owner folders;
  padding them further would violate the grounding invariant).
- Do **not** introduce a new web/CLI/TUI framework — extend `api/`,
  `cli/`, `sdk/`, `gui/` as they exist today.

## 3. Constraints inherited from this repo

- `pyproject.toml`: `--cov-fail-under=100` for `src/engineering_studio` —
  any new Python code (API route, SDK export, CLI flag) needs matching
  tests in the same change.
- `mypy --strict`, `ruff check .`, `bandit -r src -ll`, `pip-audit` must
  all stay clean (per `docs/E2E_EVIDENCE.md`'s "last verified run" bar).
- New agent `.md` files follow the exact house style already used by
  `testing.agent.md` / `mechanical-engineering-specialist.agent.md`
  (YAML frontmatter, "Requires:" line, Mission, Never Touches, Operating
  Flow, Output Format JSON block, Changelog) — condensed originals citing
  a source, never verbatim corpus copy.
- SCOPE contract discipline (`AGENTS.md` §3): every dispatched task states
  allowed files, forbidden files, acceptance criteria — carried into
  PROMPT.md verbatim.

## 4. Open questions and their default (do not block on these)

| #  | Question                                                                                                                            | Default if unanswered                                                                                                                                                                                                     |
| :- | :---------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Q1 | Exact OpenAI API model ID(s) for "Sol/Terra/Luna"                                                                                   | Treat as 3 env-var placeholders (`OPENAI_MODEL_ORCHESTRATOR/_SPECIALIST/_RESEARCH`, mirroring the existing Fireworks 3-way split), left blank in `.env.example` with a comment marking them TBD-at-kickoff.           |
| Q2 | Does the OpenAI Hackathon require the official`openai` Python SDK, or is a REST call via the existing `ModelClient` acceptable? | Default: reuse existing`requests`-based `ModelClient` pointed at `https://api.openai.com/v1` (zero new runtime dependency, zero new supply-chain surface) unless the user confirms the SDK is a judged requirement. |
| Q3 | Is a demo required to call all three tiers (Sol/Terra/Luna) in one run, or is one tier acceptable?                                  | Default: reuse the existing 3-way routing split (orchestrator/specialist/research) so all three are exercised in one full pipeline run, matching "proper use... to some degree."                                          |
| Q4 | Should the`.env.example` merge-conflict marker (INVESTIGATE.md §6) be fixed as part of this work?                                | Default: yes, fix it opportunistically the moment a new row is added to that file (cheap, in-scope-adjacent), disclosed in that change's commit message.                                                                  |

## 5. Success criteria

1. `INVESTIGATE.md`, `PREPLAN.md`, `PLAN.md`, `PROMPT.md`,
   `README_OPENAI_JUDGES.md` all exist at `engineering-studio-ai/` root.
2. Every one of the 12 empty folders has at least one file (Section 3 of
   PLAN.md), each following house style and citing a grounding source.
3. `config_management/` folder's file documents the OpenAI provider env
   vars added to `.env.example`.
4. `sdk/`, `cli/`, `api/` each have one narrow, tested addition
   demonstrating provider-swap capability (not necessarily a live OpenAI
   call in CI — mocked, per this repo's existing testing convention).
5. Full suite (`pytest`, `ruff`, `mypy --strict`, `bandit`) stays green.
6. Playwright e2e evidence (screenshots + video) captured for any UI
   change, following `docs/E2E_EVIDENCE.md`'s existing format.
7. `README_OPENAI_JUDGES.md` lets an OpenAI judge start-to-finish without
   ever needing to read the AMD-hackathon judges' guide.

## 6. Stakeholders

- **OpenAI Hackathon judges** — primary new audience; time-constrained,
  need a narrow entry point (Section 7 of this doc's companion PLAN).
- **Existing AMD-hackathon judges/reviewers** — must see zero regression
  in their existing evidence trail.
- **Lower-intelligence executor model** — the actual consumer of
  `PROMPT.md`; needs explicit, unambiguous, single-file-scoped tasks.

## Changelog

| Version    | Date       | Author     | Description                                         |
| :--------- | :--------- | :--------- | :-------------------------------------------------- |
| 2026.0.1.0 | 2026-07-17 | Hadrian Hu | Initial preplan bridging INVESTIGATE.md to PLAN.md. |
