# `engineering_studio/decorators/` — cross-cutting decorators

WHAT: Reserved package for cross-cutting function/method decorators
(e.g. retry-with-backoff for Fireworks AI calls, execution timing,
structured-log wrapping) applied to agent and pipeline functions.
WHY: `AGENTS.md` §1 names **decorators** as one of the four enforced
OOP elements every module should be decomposable into — collecting
them here (instead of inlining ad hoc decorators per agent module)
keeps them single-purpose, testable in isolation, and reusable across
every specialist agent.
HOW: Currently an empty placeholder (`__init__.py` only). When
populated, each decorator is one small function in its own module (e.g.
`retry.py`, `timing.py`), imported by `../agents/*.py` and
`../fireworks_client.py` — no decorator should have side effects beyond
its stated purpose (logging, retry, timing), per AGENTS.md §2 (pure
functions where practical).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../../../AGENTS.md`](../../../AGENTS.md) §1, §7 — code structure and
  logging/observability conventions these decorators should follow.
