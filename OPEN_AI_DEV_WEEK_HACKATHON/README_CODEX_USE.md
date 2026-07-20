---
title: "README (Codex Execution Handoff) — Engineering Studio AI OpenAI Hackathon"
author: "Hadrian Hu"
date: "2026-07-18"
version: "2026.0.2.0"
status: "In Progress"
keywords:
  - engineering-studio-ai
  - openai-hackathon
  - codex
  - execution-handoff
  - prompt-md
---

<!--
WHAT: Operator's guide for running OpenAI Codex (or any comparably-sized
"lower-intelligence executor model", per PROMPT.md's own terminology) as
the agent that finishes the still-pending work in this folder.
WHY: INVESTIGATE.md / PREPLAN.md / PLAN.md were authored by a stronger
model in an investigate-then-plan pass; PROMPT.md was deliberately
written so a smaller/cheaper model (e.g. Codex) could execute it without
re-deriving any planning context. This file is the missing piece: how to
actually point Codex at PROMPT.md, in what order, with what guardrails,
and how to know when it is done.
HOW: Condenses the current status of every PLAN.md phase (cross-checked
against `README_OPENAI_JUDGES.md` §2a and §6's Evidence Index, and repo
memory, as of 2026-07-18), then gives copy-paste-ready operator
instructions. Does not restate PROMPT.md's Task Specifications
themselves — this file only tells you how to hand PROMPT.md to Codex.
-->

# README (Codex Execution Handoff) — Engineering Studio AI

## 1. Purpose of this file

This is **not** another planning or judging document. `INVESTIGATE.md`,
`PREPLAN.md`, and `PLAN.md` already answer "what to build". `PROMPT.md`
already answers "the exact task specs a smaller model should follow".
This file answers the one question those don't: **how do I actually run
Codex against this repo to finish the remaining work?**

Read `PROMPT.md` in full before starting a Codex session — this file
assumes you have.

## 2. Status snapshot (as of 2026-07-18 — verify before trusting)

| PLAN.md phase | Content | Status | Owner of the pending part |
| :--- | :--- | :--- | :--- |
| Phase 1 | `config_management/` agent file | Complete (21-file roster landed) | — |
| Phase 2 | `.env.example` `OPENAI_*` block + stray `=======` fix | Complete | — |
| Phase 3 | `software_supply_chain/` agent file | Complete | — |
| Phase 4 | SDK/API/CLI/TUI provider-swap code + 100%-coverage tests | Complete (2026-07-18 — `sdk/providers.py`, `GET /api/models`, CLI `models` subcommand, TUI model-routing panel; ruff/mypy/bandit clean; `pytest --cov=engineering_studio --cov-fail-under=100` passes at 130/130) | — |
| Phase 5 | `testing/` split (4 specialist files) | Complete | — |
| Phase 6 | `artifacts_management/` agent file | Complete | — |
| Phase 7 | `domain-specialists/*` narrow splits | Complete | — |
| Phase 8 | Playwright E2E evidence + deployment re-verification | **Pending** | Codex (this handoff) |
| Phase 9 | Judges' doc + session archive | Complete (`README_OPENAI_JUDGES.md`, `CHATS/`) | — |

Only **Phase 8** remains. In `PROMPT.md` terms, that means **Task 4
through Task 6** are what Codex should run this session (Tasks 1-3 are
already done — do not re-run them; Codex should verify this via git
status / file existence first, not take this table on faith, per the
grounding rule in Section 4 below).

Phase 8's Task 4 (live OpenAI provider run) is still explicitly
**gated**: `PREPLAN.md` §4 Q1 (real OpenAI model IDs for
"Sol/Terra/Luna") is still unconfirmed as of this writing. Codex must
not fabricate model ID strings to unblock itself — see Section 5. Task 5
(Playwright evidence in the deterministic fake-pipeline mode) and Task 6
(deployment re-verification) do not depend on that confirmation and can
proceed regardless.

## 3. How to invoke Codex for this handoff

1. Open a Codex session (CLI or IDE integration) with this repository as
   its working directory (`engineering-studio-ai/`, not the parent
   `CodingStandardsRef` workspace root).
2. Give Codex, in order, exactly these three files as context before any
   instruction: `AGENTS.md`, `OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md`,
   `OPEN_AI_DEV_WEEK_HACKATHON/PROMPT.md`. Do not paraphrase them into the
   prompt — attach/reference the files directly so Codex reads the exact
   SCOPE contracts (allowed files / forbidden files / acceptance
   criteria) verbatim.
3. Tell Codex explicitly: *"Only Task 3 through Task 7 of PROMPT.md
   remain (see `README_CODEX_USE.md` §2 for why). Confirm Tasks 1-2 are
   already done by checking the relevant files yourself before skipping
   them. Execute Task 3 through Task 7 in order. Run the Section 8
   cross-task acceptance gate after each task. Stop and report if any
   gate command fails — do not lower a threshold to make it pass."*
4. Phase 4's SDK/API/CLI/TUI code (`sdk/providers.py`, `GET /api/models`,
   CLI `models` subcommand, TUI model-routing panel) already exists and
   is fully tested — do not re-write it. Point Codex directly at Phase
   8 / Task 4-6 of `PROMPT.md`, using env-var **names** only (never
   fabricated model ID values — Section 5) for the live-provider task.
5. After Codex reports back (Task 7 in `PROMPT.md`), review its final
   report against the Section 8 gate commands yourself before treating
   the phase as closed — do not close Phase 4/8 on Codex's self-report
   alone; re-run at minimum `pytest --cov=engineering_studio --cov-fail-under=100` and the Playwright suite locally or in CI.

## 4. Guardrails Codex must follow (non-negotiable, restated from AGENTS.md/PROMPT.md)

1. **SCOPE discipline** (`AGENTS.md` §3): Codex must state allowed files,
   forbidden files, and acceptance criteria before editing — `PROMPT.md`
   already provides these per task; Codex must not expand scope beyond
   what a task specifies, even if it seems like an "obvious" adjacent fix.
2. **No fabricated model IDs**: `OPENAI_MODEL_ORCHESTRATOR` /
   `OPENAI_MODEL_SPECIALIST` / `OPENAI_MODEL_RESEARCH` stay blank (or
   read from a real `.env` the operator supplies out-of-band) until the
   real "Sol/Terra/Luna" API identifiers are confirmed. Do not let Codex
   invent a plausible-looking model string to make a demo "look done".
3. **Mocked network calls in tests**: per `PROMPT.md` Task 3, every new
   test mocks `ModelClient` — no test may call a live OpenAI or
   Fireworks endpoint, in CI or locally.
4. **100% coverage gate stays 100%**: Codex must not edit
   `--cov-fail-under` in `pyproject.toml` to make a failing gate pass
   (`PROMPT.md` Task 3's explicit forbidden-files rule).
5. **Deterministic E2E mode**: Phase 8 Playwright work runs with
   `ENGINEERING_STUDIO_FAKE_PIPELINE=1` (Mode B), matching the existing
   e2e suite's convention — never point new E2E tests at a live API key.
6. **Never touch AMD-hackathon-owned files**: `README.md`,
   `docs/JUDGES_GUIDE.md`, `paper/`, `presentation/` are out of scope for
   every task in this folder (`PREPLAN.md` §2 non-goals).
7. **Report honestly**: `PROMPT.md` Task 7 requires Codex to state which
   tasks were completed vs. skipped and why — a task must not be marked
   done without having actually run its acceptance-criteria command in
   that same session.

## 5. Preconditions to check before starting

- Confirm whether the real OpenAI model IDs for "Sol/Terra/Luna" have
  been supplied since `PREPLAN.md` was written (check with the user
  first — do not assume; see `PREPLAN.md` §4 Q1). If still unconfirmed,
  proceed with Q1's stated default (env-var names only, values blank).
- Confirm `pyproject.toml`'s `[project.optional-dependencies].e2e` group
  is installed (`pip install -e .[e2e]` or the repo's documented
  equivalent) before Task 4.
- Confirm Docker is available locally before Task 6 (deployment
  re-verification) — if not, tell Codex to skip Task 6 and report why,
  rather than fabricating a passing health-check result.

## 6. When this handoff is complete

Phase 8 in the Section 2 table shows "Complete", and
`README_OPENAI_JUDGES.md` §2a/§6 have been updated to match (that update
itself is a small follow-up task — not part of `PROMPT.md`'s numbered
tasks — and should be done by whichever model closes out this handoff,
citing the exact commands/results Codex reported in Task 7).

## Changelog

| Version    | Date       | Author     | Description                                                                 |
| :--------- | :--------- | :--------- | :---------------------------------------------------------------------------- |
| 2026.0.2.0 | 2026-07-18 | Hadrian Hu | PLAN.md Phase 4 (SDK/API/CLI/TUI code + 100%-coverage tests) marked complete; status table, §3, §6 updated so only Phase 8 remains. |
| 2026.0.1.0 | 2026-07-18 | Hadrian Hu | Initial Codex execution handoff guide, cross-checked against PLAN.md/PROMPT.md status and README_OPENAI_JUDGES.md §2a/§6. |
