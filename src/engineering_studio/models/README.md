# `engineering_studio/models/` — data models & schemas

WHAT: Reserved package for `pydantic` data models shared across the
pipeline — e.g. a `TaskSpecification` model, per-discipline artifact
schemas, and any API request/response models used by `../api/`.
WHY: `pydantic>=2.6` is already a project dependency (`pyproject.toml`).
Centralizing schemas here (instead of inline dicts) gives every
specialist agent and the API layer one validated, typed contract for
artifact data, per `AGENTS.md` §2 (deterministic, referentially
transparent glue code).
HOW: Currently an empty placeholder (`__init__.py` only). When
populated, one model (or closely related group of models) per module
(e.g. `task_spec.py`, `artifact.py`), imported by
`../task_specs.py`, `../agents/*.py`, and `../api/` as needed.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../task_specs.py`](../task_specs.py) — current Task Specification
  handling this package would formalize with typed models.
