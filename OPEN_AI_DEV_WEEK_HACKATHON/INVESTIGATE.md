---
title: "INVESTIGATE — OpenAI Hackathon Scope for New .github/agents Subdirectories"
author: "Hadrian Hu"
date: "2026-07-17"
version: "0.1.0"
keywords: ["investigate", "openai-hackathon", "gpt-5.6", "sol", "terra", "luna", "agents", "scope", "engineering-studio-ai"]
status: "Draft"
---
<!--
WHAT: Investigation-only report (no code/agent files created yet) scoping
the 12 newly-created EMPTY subdirectories under `.github/agents/` and how
an OpenAI-Hackathon-specific model tier (GPT-5.6 "Sol"/"Terra"/"Luna",
per user instruction) should be wired through this repo's UI/API/CLI/SDK/
TUI surfaces.
WHY: This repo already shipped a curated ~30-file agent roster for the AMD
LabLabAI Hackathon (`.github/agents/README.md`). The user has now created
new empty folders signaling a second, narrower pivot (OpenAI Hackathon)
and asked for investigation BEFORE any file creation, per this repo's own
SCOPE discipline (`AGENTS.md` §3 — declare allowed files, forbidden files,
acceptance criteria before acting).
HOW: Grounded entirely in files that exist on disk today (read via
`list_dir`/`read_file`), the existing Model Routing Layer pattern already
implemented in `src/engineering_studio/fireworks_client.py`, and the
existing UI/API/CLI/SDK/TUI surfaces already present under
`src/engineering_studio/`. Every claim below is either (a) verified
against a specific file path, or (b) explicitly flagged as an assumption
requiring the user's confirmation.
-->

# INVESTIGATE — OpenAI Hackathon Scope

## Table of Contents

- [1. Framing: this is a second, narrower pivot](#1-framing-this-is-a-second-narrower-pivot)
- [2. Current-state audit](#2-current-state-audit)
- [3. Scope of each new empty subdirectory](#3-scope-of-each-new-empty-subdirectory)
- [4. The &#34;GPT-5.6 Sol / Terra / Luna&#34; model question — grounding gap, flagged](#4-the-gpt-56-sol--terra--luna-model-question--grounding-gap-flagged)
- [5. Surface-by-surface incorporation: UI, API, CLI, SDK, TUI](#5-surface-by-surface-incorporation-ui-api-cli-sdk-tui)
- [6. Risks and defects discovered incidentally](#6-risks-and-defects-discovered-incidentally)
- [7. Recommendation summary](#7-recommendation-summary)
- [Changelog](#changelog)

---

## 1. Framing: this is a second, narrower pivot

This repository's `.github/agents/README.md` (v0.2.0) and `AGENTS.md`
document a curated agent roster built for the **AMD LabLabAI Hackathon**
(Fireworks-AI-hosted open models: `gpt-oss-120b`, Llama, Qwen, DeepSeek —
see `.env.example`). The user's new instruction is for a **separate,
explicitly narrow** submission to an **OpenAI Hackathon**, requiring
"proper use of GPT models like GPT 5.6 Sol, Terra, Luna to some degree."

Two things follow directly from "the scope this time is VERY NARROW":

1. This is **not** a request to re-run the full ~30-file AMD roster
   exercise again. It is a request to identify a **small, targeted set**
   of new fine-grained agents that plug into 12 already-created empty
   folders, plus the minimum surface wiring needed to demo GPT-tier model
   usage to OpenAI judges specifically.
2. The existing AMD-hackathon assets (paper, slides, `JUDGES_GUIDE.md`,
   `docs/E2E_EVIDENCE.md`) should **not** be overwritten — OpenAI judges
   need their **own** judges' doc (Section 5, Section 7 below), not a
   rewritten AMD one.

## 2. Current-state audit

Verified via direct directory listing on 2026-07-17:

| Path                                               | State                 | Notes                                                                                                                          |
| :------------------------------------------------- | :-------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `.github/agents/artifacts_management/`           | **Empty** (new) | No sibling flat file exists at this name today.                                                                                |
| `.github/agents/config_management/`              | **Empty** (new) | No sibling flat file exists at this name today.                                                                                |
| `.github/agents/software_supply_chain/`          | **Empty** (new) | No sibling flat file exists at this name today.                                                                                |
| `.github/agents/testing/`                        | **Empty** (new) | Sibling**flat file** `testing.agent.md` already exists at the parent level.                                            |
| `.github/agents/domain-specialists/electrical/`  | **Empty** (new) | Sibling flat file`electrical-electronics-engineering-specialist.agent.md` exists.                                            |
| `.github/agents/domain-specialists/electronics/` | **Empty** (new) | Currently folded into the same electrical-electronics flat file above.                                                         |
| `.github/agents/domain-specialists/firmware/`    | **Empty** (new) | Sibling flat file`firmware-specialist.agent.md` exists.                                                                      |
| `.github/agents/domain-specialists/hardware/`    | **Empty** (new) | No dedicated flat file exists today (closest:`simulation-specialist.agent.md`).                                              |
| `.github/agents/domain-specialists/mechanical/`  | **Empty** (new) | Sibling flat file`mechanical-engineering-specialist.agent.md` exists.                                                        |
| `.github/agents/domain-specialists/middleware/`  | **Empty** (new) | No dedicated flat file exists today.                                                                                           |
| `.github/agents/domain-specialists/scripting/`   | **Empty** (new) | No dedicated flat file exists today.                                                                                           |
| `.github/agents/domain-specialists/software/`    | **Empty** (new) | No dedicated flat file exists today (closest:`simulation-specialist.agent.md`, `systems-engineering-specialist.agent.md`). |
| `.github/agents/domain-specialists/systems/`     | **Empty** (new) | Sibling flat file`systems-engineering-specialist.agent.md` exists.                                                           |

This "empty subfolder sitting next to an existing flat file with the same
subject" pattern **exactly matches** a precedent already executed once in
the private parent repo's MDAP catalog ("MDAP Extension Pack Round 3":
13 pre-created empty `micro-specialists/` folders later filled 1:1 with
finer-grained per-topic files, without touching the pre-existing grouped
file). The correct read of the user's intent is therefore: **each new
folder is a container for splitting a broad flat-file specialist into
several narrower, independently-dispatchable micro-specialists** — not a
folder to be deleted or merged back into the flat file.

Confirmed existing UI/API/CLI/SDK/TUI surfaces (`src/engineering_studio/`):

| Surface       | Path                                     | Status                                                            |
| :------------ | :--------------------------------------- | :---------------------------------------------------------------- |
| API           | `api/`                                 | FastAPI + SSE (`runs.py`, per repo memory)                      |
| Web UI        | `webapp/`, `frontend/`               | Vanilla-JS + SSE dashboard (Light/Dark themes)                    |
| CLI           | `cli/commands.py`, `cli/__main__.py` | Present, has its own README                                       |
| SDK           | `sdk/`                                 | Present, currently a thin package (`__init__.py` only)          |
| TUI           | `gui/`                                 | Present (`textual` optional dependency, per `pyproject.toml`) |
| Model routing | `fireworks_client.py::ModelClient`     | Provider-agnostic by construction — see §4                      |

## 3. Scope of each new empty subdirectory

Each row below is a **recommendation of focus**, not yet an authored
file. Every entry keeps the existing flat-file/`STANDARDS_SUMMARY.md`
cross-linking convention (`Condensed from ...` provenance line, no
verbatim corpus copy).

### 3.1 `domain-specialists/{electrical,electronics,firmware,hardware,mechanical,middleware,scripting,software,systems}/`

WHAT: Nine folders splitting the current 5 flat-file domain specialists
into narrower, OpenAI-judge-legible micro-roles. WHY narrow: OpenAI
Hackathon judges reward clearly demonstrable, individually-testable model
calls more than one monolithic "Mechanical Engineer" prompt — splitting
increases the number of distinct GPT-tier calls a demo run can show in
its trace/log (directly supporting "proper use of GPT models... to some
degree").

Recommended narrow split (only what plugs into an already-existing
pipeline stage — see `agents.orchestrator.PARALLEL_DISCIPLINES` per repo
memory — no invented new pipeline stages):

- `electrical/` — power-budget specialist, wiring-harness specialist (both narrow `electrical-electronics-engineering-specialist.agent.md`).
- `electronics/` — component-selection/BOM-line specialist, PCB-footprint-note specialist.
- `firmware/` — RTOS-task-skeleton specialist, sensor-driver-stub specialist (both narrow `firmware-specialist.agent.md`).
- `hardware/` — enclosure/thermal specialist (net-new; currently unowned — flagged, not fabricated, in §6).
- `mechanical/` — structural-frame specialist, tolerance-stackup specialist (narrow `mechanical-engineering-specialist.agent.md`).
- `middleware/` — inter-service message-contract specialist (net-new; ties to `runs.py` pub/sub — closest existing owner is none, flagged).
- `scripting/` — build/automation-script specialist (net-new; closest existing owner is `scaffolding/`, flagged as adjacent, not duplicate).
- `software/` — API-contract specialist, SDK-surface specialist (net-new; directly relevant to §5 below).
- `systems/` — integration/cross-domain specialist (already the stated scope of `systems-engineering-specialist.agent.md` per repo memory's 2026-07-08 correction — this folder should **narrow that file's existing corrected scope**, not re-litigate it).

### 3.2 `artifacts_management/`

WHAT: Owns the lifecycle of files the pipeline produces (BOM, wiring
notes, firmware skeleton, sim config, cost estimate, doc export) **after**
a specialist writes them: naming/versioning convention, provenance
(which run + which model produced which file), retention, and the
download-link wiring already visible in the dashboard (per repo memory,
`test_pipeline_stream.py` verifies "download links becoming available").
WHY as its own folder rather than folded into `documentation.agent.md`:
documentation compiles a **final package**; artifacts management owns the
**intermediate** per-stage files feeding that compilation, including
provenance metadata OpenAI judges would want for auditability (which
model — Sol/Terra/Luna — produced which artifact).

### 3.3 `config_management/`

WHAT: Owns the schema and validation of environment-driven configuration:
model-routing env vars (`FIREWORKS_MODEL_*` today, an `OPENAI_MODEL_*`
family to be added per §4), feature flags (`ENGINEERING_STUDIO_FAKE_PIPELINE`
per repo memory), and `.env.example` itself. WHY its own folder: this is
the **single highest-leverage** new folder for the OpenAI pivot — every
other new agent's ability to call a GPT-tier model routes through
whatever this folder's specialist defines as the config contract.

### 3.4 `software_supply_chain/`

WHAT: Owns SBOM/dependency-pinning/license/CVE posture specifically for
whatever new SDK dependency an OpenAI-model integration introduces (e.g.
an `openai` Python package, if the user's OpenAI Hackathon track requires
using OpenAI's own SDK rather than an OpenAI-compatible REST call through
the existing `requests`-based `ModelClient`). WHY its own folder rather
than reusing the existing `challenge-division/security-specialist`: that
existing role is adversarial/reactive (red-team review); this one is
proactive dependency hygiene — matches the parent MDAP catalog's existing
Function-axis distinction between "challenge" and "utility" roles.

### 3.5 `testing/`

WHAT: Splits the existing single `testing.agent.md` (currently: "Run/
author unit, integration, and contract tests... using a mocked Fireworks
AI client fixture") into narrower per-tier files: unit, integration,
contract (mocked-model-client), and end-to-end (Playwright, per
`docs/PLAYWRIGHT_INTEGRATION_PLAN.md` + `docs/E2E_EVIDENCE.md`
conventions already in this repo). WHY: PROMPT.md (Section 4 of this
report's companion PLAN) hands **screenshot/video-producing E2E work**
to a lower-intelligence executor model — that executor needs one
narrowly-scoped file to follow, not the whole `testing.agent.md`
covering three tiers at once.

## 4. The "GPT-5.6 Sol / Terra / Luna" model question — grounding gap, flagged

**Grounding check (required by this repo's own AGENTS.md §5 and the
global MDAP constitution's G=1.0 rule): I have no verified knowledge of
"GPT-5.6", "Sol", "Terra", or "Luna" as real, currently-documented OpenAI
model identifiers.** I am treating this exactly as the user's stated
requirement (T-2 trust tier — the verified user's own instruction) and
am **not** fabricating API model-ID strings, context-window sizes,
pricing, or capability claims for them. Two concrete follow-ups are
needed before any code references a literal model string:

1. Confirm the **exact API model ID(s)** issued for hackathon
   participants (likely supplied at kickoff via an API key + model
   allow-list, the same pattern already used for
   `FIREWORKS_MODEL_ORCHESTRATOR` etc.).
2. Confirm whether "Sol / Terra / Luna" map to **three distinct model
   tiers** (e.g. small/medium/large, analogous to this repo's existing
   `FIREWORKS_MODEL_ORCHESTRATOR` / `_SPECIALIST` / `_RESEARCH` 3-way
   split) or to three **separate named models** the judges specifically
   want exercised in one run.

**What is NOT a gap — the existing architecture already generalizes
cleanly to this:** `fireworks_client.py::ModelClient` already takes
`base_url`, `api_key`, and `model` as constructor args read from
environment variables, exactly the "Model Routing Layer" pattern
(`VISION_MULTIMODAL_DEPLOYABLE_AGENTS_CLEAN.md` §12.3) the class's own
docstring cites. Since OpenAI's chat-completions API is
OpenAI-compatible-by-definition (it *is* the reference implementation
that "OpenAI-compatible" means), pointing this same client at
`https://api.openai.com/v1` with a new `OPENAI_API_KEY` and
`OPENAI_MODEL_*` env vars is a **config-only change**, not an
architecture change — the class needs zero code modification, only (a)
an optional `Authorization` header already implemented, and (b) new
`.env.example` rows. This should be validated (not assumed) once real
model IDs are confirmed, because OpenAI's endpoint may require
provider-specific request fields (e.g. `reasoning_effort` naming, or a
`/v1/responses` vs `/v1/chat/completions` path difference) that Fireworks
does not.

## 5. Surface-by-surface incorporation: UI, API, CLI, SDK, TUI

| Surface                                   | Existing hook                                         | Minimum narrow addition for OpenAI-model demo legibility                                                                                                                                                                                                                                                                                                |
| :---------------------------------------- | :---------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **API** (`api/`)                  | `runs.py` SSE pub/sub                               | Add a read-only`GET /api/models` (or extend an existing health/status route) that reports, per pipeline stage, which model ID actually answered — surfaces Sol/Terra/Luna usage to any UI consumer without new pipeline logic.                                                                                                                       |
| **UI** (`webapp/`, `frontend/`) | Existing per-stage SSE cards (Light/Dark themes)      | Render a small "model" badge per stage card, sourced from the API addition above — a judge watching the live dashboard visibly sees which GPT tier ran which stage.                                                                                                                                                                                    |
| **CLI** (`cli/commands.py`)       | Existing command surface                              | Add a`--model-tier {sol,terra,luna}` (placeholder names, pending §4 confirmation) override flag and a `models list` subcommand mirroring `.env.example`'s routing rows.                                                                                                                                                                          |
| **SDK** (`sdk/`)                  | Currently a near-empty package (`__init__.py` only) | Export`ModelClient` and a small `OpenAIModelClient` (or a `provider="openai"` constructor branch) publicly, so a third-party judge/dev integrating against this repo's SDK can swap providers in one line — this is the most natural home for "proper use of GPT models" to be demonstrably reusable, not just hard-wired into the orchestrator. |
| **TUI** (`gui/`, `textual`)     | Present but thin (`__main__.py` only observed)      | Add a model-picker panel reusing the same config surface as the CLI flag above — no separate config path.                                                                                                                                                                                                                                              |

Narrow-scope note: none of the five surfaces need **new** infrastructure
(no new web framework, no new CLI framework, no new TUI framework) — every
addition above is an extension of an already-present, already-tested
surface, consistent with "VERY NARROW."

## 6. Risks and defects discovered incidentally

- **`.env.example` contains a literal, uncommitted-looking Git merge
  conflict marker** (`=======` on its own line, between the active
  `FIREWORKS_MODEL_*` rows and a commented-out alternate-model block).
  This was not introduced by this investigation and is **not fixed
  here** (out of this task's declared scope) — flagged for the user to
  confirm whether it is intentional (e.g. a deliberate divider) or a
  leftover unresolved conflict, since PLAN.md/PROMPT.md will add new rows
  to this same file.
- **"hardware", "middleware", "scripting", "software" domain-specialist
  folders have no existing flat-file owner to narrow** — filling them
  requires *new* role definitions, not splits of existing ones. This is
  flagged rather than silently treated the same as the 5 folders that DO
  have an existing owner, per the Round-3 "honest-shortfall" precedent
  in repo memory (do not pad with ungrounded roles).
- **Coverage/CI impact is zero for `.github/agents/**/*.md` additions** —
  these are prompt/documentation files, not importable Python under
  `src/engineering_studio/`, so the `--cov-fail-under=100` gate
  (`pyproject.toml`) is unaffected by Section 3's additions. Only the
  Section 5 surface additions (API route, SDK export, CLI flag) touch
  code paths that DO fall under the 100% gate — PLAN.md must budget test
  additions accordingly.
- **Two hackathons, one repo** — without a clearly separate judges' doc
  (Section 7 companion `README_OPENAI_JUDGES.md`), an OpenAI judge
  landing on the existing root `README.md`/`docs/JUDGES_GUIDE.md` will
  read exclusively AMD-LabLab-hackathon framing. This is a real
  first-impression risk, addressed structurally (new doc, not a rewrite)
  in the companion plan.

## 7. Recommendation summary

1. Treat this as an **additive, narrow** pass: fill the 12 empty folders
   with a small number of genuinely new, narrowly-scoped files (Section 3),
   do not touch existing flat-file specialists beyond an optional
   cross-link line (same discipline as the parent MDAP catalog's
   "extend, never rewrite" rule, `mdap-00-constitution.instructions.md`
   Rule 2).
2. Do not invent OpenAI model ID strings, context windows, or pricing —
   wire the config surface (`config_management/`) to accept them as
   environment variables once confirmed (Section 4).
3. Reuse, don't replace, the existing `ModelClient` — the Model Routing
   Layer pattern already supports this pivot; only add a second
   provider profile.
4. Ship a **separate** `README_OPENAI_JUDGES.md` (not a rewrite of
   `docs/JUDGES_GUIDE.md`) so the two hackathon submissions never
   collide.
5. Proceed next to `PREPLAN.md` -> `PLAN.md` -> `PROMPT.md` (this
   session's remaining deliverables) before any file under
   `.github/agents/` or `src/engineering_studio/` is actually written.

## Changelog

| Version    | Date       | Author     | Description                                                    |
| :--------- | :--------- | :--------- | :------------------------------------------------------------- |
| 2026.0.1.0 | 2026-07-17 | Hadrian Hu | Initial investigation report; no agent/code files created yet. |
