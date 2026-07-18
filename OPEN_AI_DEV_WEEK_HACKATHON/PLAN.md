---
title: "PLAN — OpenAI Hackathon Narrow-Scope Implementation Plan"
author: "Hadrian Hu"
date: "2026-07-18"
version: "2026.0.2.0"
keywords: ["plan", "openai-hackathon", "tasks", "engineering-studio-ai"]
status: "In Progress"
---
<!--
WHAT: Concrete, ordered task breakdown implementing INVESTIGATE.md /
PREPLAN.md. Each task states allowed files, forbidden files, and
acceptance criteria (AGENTS.md §3 SCOPE contract) so it can be handed to
PROMPT.md's lower-intelligence executor without ambiguity.
WHY: Separates "what to build" (this file) from "how a smaller model
should be told to build it" (PROMPT.md) — same Function/Workflow-position
separation the parent MDAP catalog uses between planning and task-spec
artifacts.
HOW: Phased; each phase is independently completable and independently
testable, so a failed/blocked phase does not stall the others.
-->

# PLAN — OpenAI Hackathon Narrow-Scope Implementation

## Phase 0 — Preconditions (must be confirmed or defaulted before Phase 2+)

- Resolve PREPLAN.md Q1-Q4, or explicitly proceed on stated defaults.
- Confirm no in-flight AMD-hackathon-judging window would be disrupted by
  new root-level files (`INVESTIGATE.md`, `PREPLAN.md`, `PLAN.md`,
  `PROMPT.md`, `README_OPENAI_JUDGES.md` are purely additive — no
  existing file's content changes in this phase).

## Phase 1 — `config_management/` (highest leverage, do first)

**Allowed files:** `.github/agents/config_management/*.agent.md`,
`.github/agents/config_management/README.md`.
**Forbidden files:** any file outside this folder.
**Acceptance criteria:** one file, `openai-config-specialist.agent.md`,
documenting: (a) the new `OPENAI_API_KEY` / `OPENAI_BASE_URL` /
`OPENAI_MODEL_ORCHESTRATOR` / `OPENAI_MODEL_SPECIALIST` /
`OPENAI_MODEL_RESEARCH` env var names (values left blank — Q1 default),
(b) that they follow the identical Section 12.3 Model Routing Layer
pattern already used by `FIREWORKS_*`, (c) a one-line pointer to
`.env.example` as the single source of truth for the actual values.

## Phase 2 — `.env.example` update (code-adjacent, not agent-md)

**Allowed files:** `.env.example` only.
**Forbidden files:** any `.py` file (config wiring code is Phase 4).
**Acceptance criteria:**

1. Fix the stray `=======` merge-conflict-looking marker (PREPLAN.md Q4
   default: yes).
2. Add a clearly-commented new block:

   ```
   # OpenAI Hackathon provider profile (optional; additive to Fireworks) —
   # model IDs left blank pending hackathon kickoff (see INVESTIGATE.md §4).
   OPENAI_API_KEY=
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL_ORCHESTRATOR=
   OPENAI_MODEL_SPECIALIST=
   OPENAI_MODEL_RESEARCH=
   ```

3. Existing `FIREWORKS_*` rows are untouched (no line removed/reordered
   beyond the conflict-marker fix).

## Phase 3 — `software_supply_chain/`

**Allowed files:** `.github/agents/software_supply_chain/*.agent.md`,
`.github/agents/software_supply_chain/README.md`.
**Acceptance criteria:** one file,
`dependency-hygiene-specialist.agent.md`, scoped to: run `pip-audit` +
license check whenever a new dependency (e.g. an `openai` package, if
Phase 4/Q2 resolves to "yes, SDK required") is proposed; explicitly
Never-Touches existing `challenge-division/security-specialist`'s
adversarial review role (cross-link, don't duplicate).

## Phase 4 — SDK / API / CLI / TUI narrow additions — **Complete (2026-07-18)**

Only proceed with the sub-items whose Phase 0 question resolved
favorably; each is independently gated.

4.1 **SDK** (`src/engineering_studio/sdk/`):

- **Allowed:** `sdk/__init__.py`, one new `sdk/providers.py` (or
  equivalent single new module), matching test file under `tests/`.
- **Acceptance:** `ModelClient` importable from `engineering_studio.sdk`
  unchanged; a thin factory (e.g. `build_model_client(provider: str, role: str) -> ModelClient`) reads either `FIREWORKS_*` or `OPENAI_*`
  env vars based on `provider`. 100% coverage on the new module.

4.2 **API** (`src/engineering_studio/api/`):

- **Allowed:** one new route module or an addition to an existing
  route file, matching test file under `tests/`.
- **Acceptance:** `GET /api/models` (or equivalent) returns, per known
  pipeline role, the currently-configured provider+model id (never the
  API key). Mocked in tests — no live network call in CI.

4.3 **CLI** (`src/engineering_studio/cli/commands.py`):

- **Allowed:** additions to `commands.py` only, matching test file.
- **Acceptance:** `models list` subcommand prints the same
  role->provider->model mapping as 4.2, sourced from the same
  factory (no duplicated logic).

4.4 **TUI** (`src/engineering_studio/gui/`):

- **Allowed:** additions inside `gui/` only.
- **Acceptance:** existing TUI screen gains a read-only model-info
  panel reusing 4.1's factory; no new screen/framework.

## Phase 5 — `testing/` split

**Allowed files:** `.github/agents/testing/*.agent.md`,
`.github/agents/testing/README.md`.
**Acceptance criteria:** 3-4 files narrowing `testing.agent.md`: `unit- testing-specialist.agent.md`, `integration-testing-specialist.agent.md`,
`contract-testing-specialist.agent.md` (mocked-`ModelClient` fixture
focus), `e2e-testing-specialist.agent.md` (Playwright, screenshots/video —
hands off directly to PROMPT.md Task 3). Parent `testing.agent.md` gets
exactly one added cross-link line, never rewritten wholesale.

## Phase 6 — `artifacts_management/`

**Allowed files:** `.github/agents/artifacts_management/*.agent.md`,
`.github/agents/artifacts_management/README.md`.
**Acceptance criteria:** one file, `artifact-provenance-specialist.agent.md`,
documenting a provenance record shape (run id, stage, provider, model id,
output file path, timestamp) attached to each produced artifact — this is
documentation/contract only in this phase; wiring it into `runs.py`'s
actual artifact-write path is an explicitly separate, future task (not
in this narrow scope) unless the user confirms otherwise.

## Phase 7 — `domain-specialists/*` narrow splits

Order by existing-owner confidence (INVESTIGATE.md §3.1):

1. `electrical/`, `firmware/`, `mechanical/`, `systems/` — split existing
   flat files (highest confidence, do first).
2. `electronics/` — split from the same electrical-electronics flat file.
3. `software/` — new API-contract + SDK-surface specialists, directly
   supporting Phase 4.
4. `hardware/`, `middleware/`, `scripting/` — exactly **one** narrowly
   justified new file each (PREPLAN.md non-goals §2); do not pad further.

Each new file: house style (frontmatter, Requires:, Mission, Never
Touches, Operating Flow, Output Format, Changelog), "Condensed from" line
citing the parent flat file or the closest MDAP source if genuinely new.

## Phase 8 — Testing, E2E evidence, deployment (hand off to PROMPT.md)

This phase is executed via `PROMPT.md`'s Task Specifications, not
described further here — see that file for the exact instructions a
lower-intelligence model should follow for: unit/integration tests,
Playwright E2E (screenshots + video), and redeployment verification
(`docker compose` health check, per `docs/E2E_EVIDENCE.md` precedent).

## Phase 9 — Judges' doc + session archive

- Author `README_OPENAI_JUDGES.md` (this session, see companion file).
- Confirm `CHATS/` archive of this session exists at repo root.

## Cross-phase acceptance gate (must hold after every phase)

`ruff check .`, `mypy --strict .` (or `mypy src` per current pytest
config), `bandit -r src -ll`, `pip-audit`, and `pytest --cov=engineering_studio --cov-fail-under=100` all pass before a phase is marked complete.

## Changelog

| Version    | Date       | Author     | Description                                         |
| :--------- | :--------- | :--------- | :-------------------------------------------------- || 2026.0.2.0 | 2026-07-18 | Hadrian Hu | Phase 4 (SDK/API/CLI/TUI provider-swap code + 100%-coverage tests) marked complete; all four sub-items (4.1-4.4) landed and gate-verified (ruff/mypy/bandit clean, pytest 130/130 at 100% coverage). || 2026.0.1.0 | 2026-07-17 | Hadrian Hu | Initial phased plan from INVESTIGATE.md/PREPLAN.md. |
