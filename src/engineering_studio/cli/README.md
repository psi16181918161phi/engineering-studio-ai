# `engineering_studio/cli/` — CLI entry point package

WHAT: The `python -m engineering_studio.cli` entry point (`main()` in
[`__init__.py`](__init__.py), invoked via [`__main__.py`](__main__.py)),
dispatching to three subcommands implemented in
[`commands.py`](commands.py): `run "<brief>" [--artifacts-root PATH]`
(the default when no recognized subcommand is given, for backward
compatibility with the pre-W4 `python -m engineering_studio.cli "<brief>"`
invocation), `status [--artifacts-root PATH]` (lists discipline folders
present under the artifacts root), and `artifacts [--artifacts-root PATH]`
(lists every artifact file under the artifacts root). Previously split
across a sibling `cli.py` file and this package; merged into one package
during the W7 coverage-closure workstream after the split was found to
silently break `python -m engineering_studio.cli` (the package shadowed
the sibling file at the `engineering_studio.cli` import path).
WHY: One canonical location for the CLI surface — see AGENTS.md §1
(single-responsibility modules) and §2 (OCP: add, don't rewrite).
HOW: `main()` loads `.env`, parses the optional subcommand name and an
optional `--artifacts-root PATH` pair, then delegates to
[`commands.py`](commands.py)'s `cmd_run`/`cmd_status`/`cmd_artifacts` —
each a thin, single-purpose function returning `(exit_code, message)`.
`cmd_run` is built on `sdk.EngineeringStudioClient` (W3/W4), not on
`agents.orchestrator.run_pipeline` directly. `status`/`artifacts` are
read-only filesystem introspection only — there is no persisted job
registry, so they never fabricate a "run in progress" state. Add a new
subcommand by adding a function to `commands.py` and one dispatch branch
in `main()`, rather than duplicating argument parsing.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`__init__.py`](__init__.py) — `main()` implementation (argument parsing + dispatch).
- [`commands.py`](commands.py) — `cmd_run`/`cmd_status`/`cmd_artifacts` implementations.
- [`__main__.py`](__main__.py) — `python -m engineering_studio.cli` entry point.
