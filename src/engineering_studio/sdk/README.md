# `engineering_studio/sdk/` — programmatic SDK

WHAT: A small, importable Python SDK that lets other tools or scripts
drive the pipeline programmatically:
`from engineering_studio.sdk import EngineeringStudioClient`, without
going through the CLI's argv parsing or an HTTP API.
WHY: `../cli/` and `../api/` both wrap `agents.orchestrator.run_pipeline`
for a specific transport (terminal, HTTP); this SDK gives a third,
typed, in-process integration point (e.g. for `../frontend/`, `../webapp/`,
`../gui/`, or test fixtures) without importing orchestrator internals or
handling raw `dict[str, Path]` outputs directly.
HOW: `EngineeringStudioClient(artifacts_root=...).run(product_brief)`
validates the brief via `models.ProductBrief`, delegates to
`agents.orchestrator.run_pipeline`, and returns a typed
`models.PipelineResult`. All failures surface as this package's
`exceptions` hierarchy (`ValidationError`, `ModelUnavailableError`,
`PipelineExecutionError`) — see `__init__.py`'s docstring for the exact
normalization rules. 100% test coverage in `tests/test_sdk.py`.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../agents/orchestrator.py`](../agents/orchestrator.py) — the
  pipeline entry point this SDK wraps.
- [`../models/__init__.py`](../models/__init__.py) — `ProductBrief` /
  `PipelineResult` typed contracts this SDK returns.
- [`../exceptions/__init__.py`](../exceptions/__init__.py) — the error
  hierarchy this SDK normalizes failures into.
