# `engineering_studio/exceptions/` — package exception hierarchy

WHAT: Reserved package for the project's custom exception classes
(e.g. a common `EngineeringStudioError` base, plus specific errors for
artifact-write failures, invalid Task Specifications, scope violations).
WHY: `AGENTS.md` §1 names **exception handlers** as one of the four
enforced OOP elements every module should be decomposable into.
`ModelUnavailableError` currently lives in `../fireworks_client.py`;
as the exception surface grows, a shared hierarchy here avoids each
module defining its own ad hoc error types.
HOW: Currently an empty placeholder (`__init__.py` only). When
populated, define a small class hierarchy (e.g. `EngineeringStudioError`
→ `ModelUnavailableError`, `ArtifactWriteError`, `ScopeViolationError`)
and re-export from `../fireworks_client.py` for backward compatibility
rather than introducing a duplicate error type.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../fireworks_client.py`](../fireworks_client.py) — current home of
  `ModelUnavailableError`.
