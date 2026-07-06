---
title: "Standards Summary — Engineering Studio AI Agent Roster"
author: "Hadrian Hu"
date: "2026-07-06"
version: "2026.0.1.0"
keywords: ["standards", "jpl", "solid", "acid", "aria", "semver", "testing", "scaffolding", "venv", "ux", "documentation"]
status: "Active"
---
# Standards Summary — Engineering Studio AI Agent Roster

WHAT: A condensed, in-our-own-words reference to the key engineering standards
every agent under `.github/agents/` must comply with, for standards not already
covered by the repo-root `AGENTS.md`.
WHY: `AGENTS.md` already condenses SOLID/ACID/SCOPE/grounding/injection/
token-efficiency/aesthetics/logging/security/SemVer. This file fills the
remaining gaps the hackathon roster needs (JPL Power-of-Ten, accessibility/
ARIA specifics, strict enumeration, testing taxonomy, project scaffolding,
virtual environments, UI/UX, documentation structure) without ever copying the
private `CodingStandardsRef/coding_stds/` corpus verbatim — only the
well-known public definition or an original condensed restatement is used.
HOW: Every agent file cross-links this document (`../STANDARDS_SUMMARY.md` or
`STANDARDS_SUMMARY.md` depending on depth) instead of restating these rules.

## 1. NASA/JPL "Power of Ten" (safety-critical code discipline)

Applied here as 10 pragmatic rules for any generated firmware/simulation/
backend code, not just C:

1. Keep control flow simple — no `goto`, minimal recursion depth, bounded
   loops (every loop must have a provable upper iteration bound).
2. No dynamic memory allocation after initialization where avoidable; if a
   language requires it (Python), prefer fixed-size/pre-allocated structures
   in hot paths.
3. No function longer than fits on one screen (~60 lines); split by
   responsibility (ties into SOLID SRP in `AGENTS.md` §2).
4. Assertion density: validate preconditions/postconditions on any function
   crossing a specialist-agent artifact boundary.
5. Declare data objects at the smallest possible scope.
6. Check the return value of every function call that can fail; never
   silently swallow an error (ties into `AGENTS.md` §5 live-data honesty).
7. Limit the preprocessor/metaprogramming surface — prefer explicit code
   over dynamic code generation for anything safety- or cost-relevant
   (e.g. BOM totals, cost estimates).
8. Restrict pointer/reference indirection to one level where practical;
   avoid deeply nested object graphs for artifact models.
9. Compile/lint with all warnings enabled and treat warnings as errors in CI.
10. Code must be unit-testable, simulatable, and verifiable — testability is
    a first-class design constraint, not an afterthought (see §5 below).

## 2. Strict / absolute enumeration

Numbered lists in specs, standards, and generated documents use strict
hierarchical decimal enumeration (`1.`, `1.1.`, `1.1.1.`) — never bare
bullets for anything that expresses an ordered rule set, a requirement list,
or an acceptance-criteria list. Bullets (`-`) are reserved for unordered,
non-normative context (examples, notes). This applies to every `.agent.md`,
spec, and task-breakdown file in this repo.

## 3. Testing standards (condensed taxonomy)

Minimum bar for any generated code before a Testing agent signs off:

1. **Unit tests** — pure-function-level, no network/filesystem, deterministic.
2. **Integration tests** — cross-module (e.g. Orchestrator to a specialist's
   artifact writer), using a mocked Fireworks AI client fixture (never a
   live network call in CI).
3. **Contract tests** — verify each specialist's Output Format JSON schema
   (see every `.agent.md`'s "Output Format" block) before a downstream agent
   consumes it.
4. **Regression tests** — pin a known-good Task Specification + fixture
   response pair; re-run on every change to the orchestration/dispatch code.
5. **Coverage gate** — this repo enforces `--cov-fail-under=80` (see
   `pyproject.toml`/CI); do not lower it to make a failing change pass.
6. **Accessibility tests** (§4) and **load/chaos tests** are out of scope for
   the hackathon timebox unless a demo surface is public-facing.

## 4. Accessibility — WCAG / ARIA (UI-facing surfaces only)

Applies to any web/CLI viewer surface produced by the Documentation or
Business/Cost agents:

1. Every interactive control has an accessible name (`aria-label` or visible
   label) and a correct ARIA role only when no native HTML element already
   conveys that semantic (prefer native `<button>`/`<input>` over
   `role="button"` on a `<div>`).
2. Color contrast ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large
   text/graphical objects (WCAG 2.1 AA).
3. All functionality operable by keyboard alone; no keyboard traps.
4. Color is never the sole channel conveying information in a chart/diagram
   (pair with a label, pattern, or icon).
5. Live-updating regions (e.g. a streaming agent-progress log) use
   `aria-live="polite"` so assistive tech announces updates without
   interrupting the user.

## 5. SOLID / ACID / SCOPE — pointer

Already condensed in `AGENTS.md` §2–3 of this repo. Do not re-derive here;
cross-link `AGENTS.md` instead.

## 6. SemVer — pointer

Already condensed in `AGENTS.md` §9 (plain SemVer, explicit deviation from
the parent corpus's Year-Prefixed SemVer). Do not re-derive here.

## 7. Project scaffolding standards

1. One canonical scaffold per language/stack; do not hand-roll a bespoke
   layout when a standard one exists (`src/<package>/`, `tests/`,
   `pyproject.toml` for this Python repo — already in place, see
   `SCAFFOLDING.md`).
2. New specialist modules live under `src/engineering_studio/<domain>/`,
   never at the repo root.
3. Every new package/module ships with: an `__init__.py` (if Python), a
   matching `tests/` module, and an entry in the relevant README/AGENTS.md
   if it introduces a new specialist role.
4. Scaffolding changes (new folders, new top-level modules) are themselves
   Tier-1 reversible actions (create/edit) unless they delete existing
   structure, which requires confirmation per this repo's operational
   safety rules.

## 8. Virtual environment standards

1. Every Python environment for this repo MUST be an isolated virtual
   environment created via `python -m venv .venv` (already present at
   `engineering-studio-ai/.venv/`).
2. `.venv/` MUST remain in `.gitignore` and MUST NOT be committed.
3. CI MUST recreate the environment from scratch (no reliance on a locally
   cached `.venv`) — see `.github/workflows/ci.yml`.
4. Pin dependency versions in `requirements.txt`/`requirements-dev.txt`;
   re-resolve deliberately, not by ad hoc `pip install` inside an
   already-provisioned environment without updating the lock/requirements
   file.

## 9. UI / UX standards (demo-facing surfaces)

1. Information architecture: one product surface, one navigation model —
   do not let five specialist agents render five inconsistent panels.
2. Interaction design: every long-running agent action (Fireworks AI call,
   file generation) shows a determinate or indeterminate progress
   indicator; never a silently frozen UI.
3. Usability: the primary demo flow (one prompt in -> one package out) must
   be completable by a first-time user without reading documentation.
4. Design system: reuse one small token set (colors/typography/spacing) —
   ties directly into `AGENTS.md` §6 aesthetics rule.

## 10. Documentation standards (markdown structure)

Every `.md` document in this repo (specs, this file, README updates) uses:

1. YAML front matter: `title`, `author`, `date`, `version`, `keywords`,
   `status`.
2. A Table of Contents for any document with 3+ major sections.
3. Strict heading hierarchy: H1 once (title only), H2 major sections, H3
   subsections — never skip a level.
4. `WHAT` / `WHY` / `HOW` for every module- or function-level docstring
   (already required by `AGENTS.md` §4).
5. Math in LaTeX (`$...$` inline, `$$...$$` display) wherever a formula
   appears (cost models, confidence scores, etc.) — see `latex.agent.md`.
6. A changelog table at the end of any document that is expected to evolve
   across the hackathon (this file, each `.agent.md`, vision-style specs).

## References

- `AGENTS.md` (repo root) — SOLID/ACID/SCOPE/grounding/injection/
  token-efficiency/aesthetics/logging/security/SemVer.
- Public well-known definitions: WCAG 2.1, ARIA 1.2, SemVer 2.0.0, NASA/JPL
  "Power of Ten" (Gerard Holzmann, 2006).
- Internal precedent (not reproduced verbatim): `CodingStandardsRef/coding_stds/`
  (private corpus this repo is a public spin-off from).

## Changelog

| Version    | Date       | Author     | Description                                                                                                            |
| :--------- | :--------- | :--------- | :--------------------------------------------------------------------------------------------------------------------- |
| 2026.0.1.0 | 2026-07-06 | Hadrian Hu | Initial condensed standards summary companion to`AGENTS.md`, authored for the `.github/agents/` roster deployment. |
