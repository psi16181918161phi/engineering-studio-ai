# backend/ — Role 3 (AI Pipeline & Backend Engineering)

WHAT: Reserved for **optional additional backend services** only — e.g.
a thin REST/WebSocket API wrapper around the pipeline if the demo needs a
live web-facing endpoint instead of (or in addition to) the CLI.
WHY: The canonical, already-scaffolded backend package is
`../src/engineering_studio/` (`agents/`, `artifacts/`, `cli.py`,
`fireworks_client.py`, `task_specs.py`). Duplicating that structure here
would create two sources of truth and guarantee merge conflicts — see
`../SCAFFOLDING.md` §2.
HOW: If you need a web-facing service, add it here as e.g.
`backend/api/` and have it *import* `engineering_studio` as a dependency
rather than reimplementing pipeline logic. If no such service is needed
for the demo, this folder legitimately stays empty (`.gitkeep` only) —
that is a valid end state, not an incomplete one.

## Where the real backend code lives

See the root [`README.md`](../README.md) §Repository layout and
[`AGENTS.md`](../AGENTS.md) §3 (SCOPE control) — every specialist agent
module is under `../src/engineering_studio/agents/`, and writes only to
its own `../src/engineering_studio/artifacts/<discipline>/` folder.
