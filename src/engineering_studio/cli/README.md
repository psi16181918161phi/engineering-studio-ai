# `engineering_studio/cli/` — CLI entry point package

WHAT: The `python -m engineering_studio.cli "<brief>"` entry point
(`main()` in [`__init__.py`](__init__.py), invoked via
[`__main__.py`](__main__.py)). Previously split across a sibling
`cli.py` file and this package; merged into one package during the W7
coverage-closure workstream after the split was found to silently break
`python -m engineering_studio.cli` (the package shadowed the sibling
file at the `engineering_studio.cli` import path).
WHY: One canonical location for the CLI surface — see AGENTS.md §1
(single-responsibility modules) and §2 (OCP: add, don't rewrite).
HOW: `main()` loads `.env`, calls `agents.orchestrator.run_pipeline`,
and prints where each artifact landed. If the CLI surface grows beyond
one command (e.g. `run`, `status`, `list-artifacts`), add sibling
modules here (one per subcommand) dispatched from `main()`, rather than
duplicating argument parsing.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`__init__.py`](__init__.py) — `main()` implementation.
- [`__main__.py`](__main__.py) — `python -m engineering_studio.cli` entry point.
