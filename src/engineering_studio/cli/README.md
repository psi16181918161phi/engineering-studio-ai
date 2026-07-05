# `engineering_studio/cli/` — CLI subcommand modules (reserved)

WHAT: Reserved package for splitting CLI subcommands into their own
modules if the single entry point in [`../cli.py`](../cli.py) grows
beyond one command (e.g. `run`, `status`, `list-artifacts`).
WHY: `../cli.py` (`python -m engineering_studio.cli "<brief>"`) is the
canonical entry point for the hackathon demo and stays that way unless
the CLI surface grows enough to warrant subcommands — see AGENTS.md §1
(single-responsibility modules) and §2 (OCP: add, don't rewrite).
HOW: Currently an empty placeholder (`__init__.py` only) — a valid end
state if `../cli.py` remains a single-command CLI for the demo. When
populated, one module per subcommand, dispatched from `../cli.py`'s
`main()` rather than duplicating argument parsing there.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3.

## Related

- [`../cli.py`](../cli.py) — current single-command entry point.
