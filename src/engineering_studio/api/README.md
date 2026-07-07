# `engineering_studio/api/` — FastAPI HTTP route definitions (W5)

WHAT: `create_app()` in [`__init__.py`](__init__.py) builds a FastAPI
app exposing `GET /health`, `POST /pipeline/run`, and
`GET /pipeline/{id}` over the multi-agent pipeline, for callers other
than the CLI (`../cli/`) — notably [`../webapp/`](../webapp/README.md)
(W6a), which consumes this app in-process.
WHY: Keeps transport-layer code (routes, request/response wiring)
separate from orchestration logic (`../agents/orchestrator.py`) per
`AGENTS.md` §1 (single-responsibility modules) — every route delegates
to `sdk.EngineeringStudioClient`, never reimplements pipeline logic.
HOW: `create_app()` is a factory (fresh app + in-memory job registry per
call) so tests get isolation; the module-level `app` is a ready instance
for `uvicorn engineering_studio.api:app`. The job registry is in-memory
only — deliberately not persisted, per the live-data-honesty rule (no
fabricated "durable job store"). 100% test coverage in
[`../../../tests/test_api.py`](../../../tests/test_api.py).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../webapp/README.md`](../webapp/README.md) — the app instance that
  would mount these routes.
- [`../../../backend/README.md`](../../../backend/README.md) — why
  transport code stays in `src/` rather than root `backend/`.
