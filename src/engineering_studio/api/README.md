# `engineering_studio/api/` — HTTP/SSE route definitions

WHAT: FastAPI route definitions that expose the multi-agent pipeline over
HTTP as a command-and-control surface, in addition to the CLI (`../cli.py`).
WHY: Keeps transport-layer code (routes, request/response wiring)
separate from orchestration logic (`../agents/orchestrator.py`) per
`AGENTS.md` §1 (single-responsibility modules) — every route handler here
calls into `engineering_studio.runs.runs` (itself a thin wrapper around
`agents.orchestrator.run_pipeline`), never reimplements pipeline logic.
HOW: One module per resource/route group:

| Module | Routes | Purpose |
|---|---|---|
| `runs.py` | `POST /api/runs`, `GET /api/runs`, `GET /api/runs/{id}`, `GET /api/runs/{id}/stream`, `GET /api/runs/{id}/artifacts/{stage}` | Launch a run, list/inspect runs, stream live stage status (SSE), fetch a stage's artifact text. |
| `health.py` | `GET /api/health` | Liveness probe. |
| `downloads.py` | `GET /api/runs/{id}/artifacts/{stage}/download`, `GET /api/runs/{id}/download` | Download one stage's artifact file, or every artifact from a run zipped together. |
| `models.py` | `GET /api/models` | Read-only model-routing snapshot (provider + model id, never the API key) for every `sdk.PROVIDERS` x `sdk.ROLES` pair — see `OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md` Phase 4.2. |

All four routers are mounted by [`../webapp/app.py`](../webapp/README.md).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../webapp/README.md`](../webapp/README.md) — the app instance that
  would mount these routes.
- [`../../../backend/README.md`](../../../backend/README.md) — why
  transport code stays in `src/` rather than root `backend/`.
