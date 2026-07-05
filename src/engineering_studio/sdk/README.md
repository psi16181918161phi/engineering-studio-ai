# `engineering_studio/sdk/` — programmatic SDK (reserved)

WHAT: Reserved package for a small, importable Python SDK that lets
other tools or scripts drive the pipeline programmatically (e.g.
`from engineering_studio.sdk import EngineeringStudioClient`) without
going through the CLI or an HTTP API.
WHY: `../cli.py` and `../api/` both wrap `agents.orchestrator.run_pipeline`
for a specific transport (terminal, HTTP); an SDK module gives a third,
in-process integration point (e.g. for `../frontend/` or `../tests/`
fixtures) without importing orchestrator internals directly.
HOW: Currently an empty placeholder (`__init__.py` only) — a valid end
state if no external programmatic consumer is needed for the demo. When
populated, expose a thin client class that wraps
`agents.orchestrator.run_pipeline` with a stable public signature.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../agents/orchestrator.py`](../agents/orchestrator.py) — the
  pipeline entry point this SDK would wrap.
