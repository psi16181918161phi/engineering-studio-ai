# `engineering_studio/gui/` — `textual` TUI application (W6b)

WHAT: `EngineeringStudioApp` in [`__init__.py`](__init__.py) — a
`textual` terminal (TUI) app with a product-brief input, a "Run
pipeline" button, a read-only model-routing panel, and an output log,
run via `python -m engineering_studio.gui` ([`__main__.py`](__main__.py)).
Consumes `sdk.EngineeringStudioClient` directly (not the HTTP API in
[`../api/`](../api/README.md)) since a local terminal app has no need
for a transport hop. The model-routing panel
(OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md Phase 4.4) reuses `sdk.get_model_info`
— the same provider-agnostic (Fireworks/OpenAI) factory the `/api/models`
route and the CLI `models` subcommand consume — to show which model
answers which pipeline role, never an API key.
WHY: A distinct Python-native interface from the browser webapp
(PREPLAN Q3) — no separate build toolchain, cross-platform in any
terminal, matching the CLI's existing runtime assumptions.
HOW: Business logic (`format_pipeline_outcome()`,
`format_model_routing_panel()`) is a pair of pure functions,
unit-tested without booting the TUI event loop; `EngineeringStudioApp`
itself is covered via `textual`'s headless `Pilot` API
(`app.run_test()`), run under `anyio`'s built-in pytest plugin (no
extra `pytest-asyncio` dependency). Styled exclusively from
`utils.palette.PALETTE_B` (Variant B interface-surface palette) via
`textual` CSS — no widget hard-codes a color literal. `main()`'s
`App.run()` call is `# pragma: no cover` (it takes over the real
terminal and blocks) — everything reachable without that call is 100%
covered in
[`../../../tests/test_gui.py`](../../../tests/test_gui.py).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../sdk/`](../sdk/README.md) — the client this app drives directly.
- [`../webapp/README.md`](../webapp/README.md) — the browser-facing
  equivalent surface (separate per PREPLAN Q3, not this package).
- [`../utils/palette.py`](../utils/palette.py) — the palette tokens
  this app's CSS is built from.
