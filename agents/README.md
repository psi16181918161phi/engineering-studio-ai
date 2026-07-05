# agents/ — Non-Code Agent Design Notes (root level)

WHAT: Per-specialist **design notes** (behavior, prompt intent, expected
inputs/outputs in prose) — NOT implementation code.
WHY: The canonical, already-scaffolded agent code lives in
`../src/engineering_studio/agents/` (`orchestrator.py`, `specialist.py`).
This root-level folder existed as a placeholder from the original
repository-structure plan (`../docs/RESPONSIBILITIES.md`); it is kept,
scoped narrowly to design notes, so Role 1/Role 2 have a place to draft a
specialist's intended behavior before Role 3 implements it — without
either folder duplicating the other's content.
HOW: One optional `<discipline>-agent-design.md` file per specialist,
written before (or alongside) the matching Task Specification in
`../docs/task-specs.md`. If a specialist's design is simple enough to
capture directly in its Task Specification block, this folder can stay
empty — that's a valid end state.

## Relationship to other agent-related locations

| Location | Contains |
|---|---|
| `agents/` (this folder) | Optional prose design notes, pre-implementation. |
| `../src/engineering_studio/agents/` | The actual `SpecialistAgent`/`Orchestrator` Python code (Role 3-owned). |
| `../docs/task-specs.md` | The exact Task Specification prompt each specialist call sends (Role 2/Role 3-owned). |
