# `engineering_studio/utils/` — shared helper functions

WHAT: Reserved package for small, reusable helper functions shared
across agents and modules (e.g. path/artifact-folder helpers, safe
write-to-temp-then-rename, structured-log setup).
WHY: Several specialist agents and `../cli/` need the same small
utilities (artifact path resolution, log formatting); centralizing them
here avoids copy-pasted helpers drifting out of sync, per `AGENTS.md`
§2 (pure functions where practical) and §7 (structured logging).
HOW: Currently an empty placeholder (`__init__.py` only). When
populated, one focused module per concern (e.g. `paths.py`,
`logging.py`), each function pure and independently unit-testable —
no module-level mutable state.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../../../AGENTS.md`](../../../AGENTS.md) §2, §7 — the functional and
  logging conventions these helpers should follow.
