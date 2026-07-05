# research/ — Role 2 (AI Research & Prompt Engineering)

WHAT: Owned exclusively by Role 2. Research findings, technology
comparisons, design recommendations, and prompt-template drafts.
WHY: Keeps investigative/prompt-authoring work in one folder so it never
collides with `src/engineering_studio/` (Role 3) or `frontend/` (Role 5)
edits — see `../SCAFFOLDING.md` §2.
HOW: Fill in the templates below; promote a stabilized prompt draft into
`../docs/task-specs.md` only once it's ready (see `../SCAFFOLDING.md` §4
for the shared-file coordination rule on that file).

## Files in this folder

| File | Purpose |
|---|---|
| `research-findings.md` | Problem framing, constraints, prior art, open questions — every claim tagged `verified`/`unverified` with a `confidence` score. |
| `technology-comparisons.md` | AMD hardware/software options, model choices, agent frameworks, benchmarking notes. |
| `prompt-drafts/` | Work-in-progress Task Specification prompts before they're promoted into `../docs/task-specs.md`. |

## Rules

1. Never state a fact as fact without a source — mark `unverified` if you
   can't cite one (per `../AGENTS.md` §5 grounding rule).
2. Once a prompt draft is stable, copy its EXACT heading structure
   (`Mission` / `Allowed Files` / `Forbidden Files` / `Expected Outputs` /
   `SCOPE Declaration`) into `../docs/task-specs.md` — `task_specs.py`
   parses that structure programmatically; a malformed heading breaks the
   pipeline for every other role.
3. Do not edit files outside this folder except your own scoped addition
   to `../docs/task-specs.md` or `../docs/TEAM_QA.md` (see
   `../SCAFFOLDING.md` §4).
