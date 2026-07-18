"""WHAT: Command-line entry point: `python -m engineering_studio.cli ...`.
WHY: Fastest path to a working hackathon demo — no web server required to
show the multi-agent pipeline producing a real artifact tree. W4 migrates
this package onto `sdk.EngineeringStudioClient` (rather than calling
`agents.orchestrator.run_pipeline` directly) and adds two read-only
introspection subcommands, `status` and `artifacts`, on top of the
existing `run` behavior — see `commands.py` for each subcommand's
implementation. A fourth subcommand, `models [fireworks|openai]`
(OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md Phase 4.3), reports the currently
configured model id per pipeline role/provider, reusing the same
`sdk.get_model_info` factory as the `/api/models` route and the TUI's
model-info panel — never an API key.
HOW: Loads `.env`, parses an optional leading subcommand name (`run`,
`status`, `artifacts`, `models`) plus an optional `--artifacts-root PATH` pair,
dispatches to the matching function in `commands.py`, then prints its
returned message and returns its exit code. Bare positional text with no
recognized subcommand name (the pre-W4 invocation form,
`python -m engineering_studio.cli "<brief>"`) is treated as an implicit
`run` for backward compatibility.

NOTE: This module previously lived as a sibling file
`engineering_studio/cli.py` alongside this now-populated `cli/` package.
That was a latent bug: once both `cli.py` and `cli/__init__.py` existed,
Python's import system resolved `engineering_studio.cli` to this package
unconditionally, silently shadowing the sibling file and breaking the
documented `python -m engineering_studio.cli` invocation (it raised
"'engineering_studio.cli' is a package and cannot be directly executed").
The implementation has been merged into this package (see
`__main__.py` for the `python -m` entry point) so the module and its
reserved-for-subcommands package identity are no longer split across two
conflicting filesystem entries.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from engineering_studio.cli.commands import cmd_artifacts, cmd_models, cmd_run, cmd_status

_DEFAULT_ARTIFACTS_ROOT = Path("runs") / "latest" / "artifacts"
_SUBCOMMANDS = ("run", "status", "artifacts", "models")


def main(argv: list[str] | None = None) -> int:
    """WHAT: CLI entry point.

    ARGS:
        argv (list[str] | None): Defaults to `sys.argv[1:]`.

    RETURNS:
        int: Process exit code (0 success, 1 usage/validation error, 2
        model/pipeline failure).
    """
    load_dotenv()
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(_usage())
        return 1

    if args[0] in _SUBCOMMANDS:
        subcommand, rest = args[0], args[1:]
    else:
        # Backward-compatible legacy invocation: bare brief text implies `run`.
        subcommand, rest = "run", args

    artifacts_root, rest = _extract_artifacts_root(rest)

    if subcommand == "run":
        if not rest:
            print(_usage())
            return 1
        exit_code, message = cmd_run(" ".join(rest), artifacts_root)
    elif subcommand == "status":
        exit_code, message = cmd_status(artifacts_root)
    elif subcommand == "models":
        exit_code, message = cmd_models(rest[0] if rest else None)
    else:
        exit_code, message = cmd_artifacts(artifacts_root)

    print(message)
    return exit_code


def _extract_artifacts_root(args: list[str]) -> tuple[Path, list[str]]:
    """WHAT: Pulls an optional `--artifacts-root PATH` pair out of `args`.

    ARGS:
        args (list[str]): Remaining CLI arguments after the subcommand name.

    RETURNS:
        tuple[Path, list[str]]: The resolved artifacts root (defaulting to
        `runs/latest/artifacts`) and the remaining arguments with the
        `--artifacts-root PATH` pair removed, in original order.
    """
    remaining: list[str] = []
    artifacts_root = _DEFAULT_ARTIFACTS_ROOT
    index = 0
    while index < len(args):
        if args[index] == "--artifacts-root" and index + 1 < len(args):
            artifacts_root = Path(args[index + 1])
            index += 2
            continue
        remaining.append(args[index])
        index += 1
    return artifacts_root, remaining


def _usage() -> str:
    """WHAT: Builds the multi-line usage banner printed on argument errors."""
    return (
        'Usage: python -m engineering_studio.cli "<product brief>"\n'
        '   or: python -m engineering_studio.cli run "<product brief>" [--artifacts-root PATH]\n'
        "   or: python -m engineering_studio.cli status [--artifacts-root PATH]\n"
        "   or: python -m engineering_studio.cli artifacts [--artifacts-root PATH]\n"
        "   or: python -m engineering_studio.cli models [fireworks|openai]"
    )


__all__ = ["main"]
