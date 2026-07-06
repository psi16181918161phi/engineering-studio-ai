# `engineering_studio/api/` — HTTP/WebSocket route definitions

WHAT: Reserved package for the FastAPI (or equivalent ASGI) route
definitions that expose the multi-agent pipeline over HTTP, if the demo
needs a web-facing endpoint in addition to the CLI (`../cli/`).
WHY: Keeps transport-layer code (routes, request/response wiring)
separate from orchestration logic (`../agents/orchestrator.py`) per
`AGENTS.md` §1 (single-responsibility modules) — a route handler should
call into `agents.orchestrator.run_pipeline`, never reimplement it.
HOW: Currently an empty placeholder (`__init__.py` only) — this is a
valid end state if the hackathon demo ships CLI-only. When populated,
one module per resource/route group (e.g. `runs.py`, `health.py`), each
importable by root [`backend/`](../../../backend/README.md) (optional
external service wrapper) or [`webapp/`](../webapp/README.md) (this
package's own app instance).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../webapp/README.md`](../webapp/README.md) — the app instance that
  would mount these routes.
- [`../../../backend/README.md`](../../../backend/README.md) — why
  transport code stays in `src/` rather than root `backend/`.
