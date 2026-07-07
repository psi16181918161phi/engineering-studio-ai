"""WHAT: `run` / `status` / `artifacts` subcommand implementations for the CLI.
WHY: W4 of the studio implementation plan migrates the CLI onto the SDK
(`EngineeringStudioClient`) rather than calling `agents.orchestrator`
directly, and adds two read-only introspection subcommands (`status`,
`artifacts`) so a user can inspect a prior run's filesystem output without
re-invoking the pipeline. Each function is a thin, single-purpose unit
(SOLID SRP) returning `(exit_code, message)` so `cli/__init__.py` only
has to print and exit — it never contains subcommand logic itself.
HOW: `cmd_run` delegates to `EngineeringStudioClient.run()` and maps its
typed exceptions to CLI exit codes/messages. `cmd_status` and
`cmd_artifacts` only read the filesystem under `artifacts_root` — they
never fabricate a "run in progress" state, since this CLI has no
persisted job registry (live-data-honesty: report what is actually on
disk, nothing more).
"""

from __future__ import annotations

from pathlib import Path

from engineering_studio.exceptions import (
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)
from engineering_studio.sdk import EngineeringStudioClient


def cmd_run(product_brief: str, artifacts_root: Path) -> tuple[int, str]:
    """WHAT: Validates and runs the full pipeline via the SDK.

    ARGS:
        product_brief (str): One-sentence hackathon demo prompt.
        artifacts_root (Path): Root directory all artifacts are written under.

    RETURNS:
        tuple[int, str]: `(exit_code, message)` — 0 on success, 1 on a
        validation failure, 2 on a model/pipeline execution failure.
    """
    client = EngineeringStudioClient(artifacts_root=artifacts_root)
    try:
        result = client.run(product_brief)
    except ValidationError as exc:
        return 1, f"Invalid product brief: {exc}"
    except ModelUnavailableError as exc:
        return 2, f"Model call failed — no fabricated result produced: {exc}"
    except PipelineExecutionError as exc:
        return 2, f"Pipeline execution failed: {exc}"

    lines = [f"Engineering Studio AI — brief: {result.product_brief.text!r}"]
    lines.extend(
        f"  {artifact.discipline:12s} -> {artifact.output_path}" for artifact in result.artifacts
    )
    return 0, "\n".join(lines)


def cmd_status(artifacts_root: Path) -> tuple[int, str]:
    """WHAT: Reports which discipline folders exist under `artifacts_root`.

    ARGS:
        artifacts_root (Path): Root directory to inspect.

    RETURNS:
        tuple[int, str]: `(0, message)` if at least one discipline folder
        is present, else `(1, message)` explaining nothing was found yet.

    WHY: Read-only filesystem introspection only — there is no persisted
    job registry to query, so this never claims a run is "in progress".
    """
    if not artifacts_root.exists():
        return 1, f"No artifacts found at {artifacts_root} (has `run` been executed yet?)"

    disciplines = sorted(p.name for p in artifacts_root.iterdir() if p.is_dir())
    if not disciplines:
        return 1, f"Artifacts root {artifacts_root} exists but contains no discipline output yet."

    lines = [f"Artifacts root: {artifacts_root}", f"Disciplines present ({len(disciplines)}):"]
    lines.extend(f"  - {discipline}" for discipline in disciplines)
    return 0, "\n".join(lines)


def cmd_artifacts(artifacts_root: Path) -> tuple[int, str]:
    """WHAT: Lists every artifact file under `artifacts_root`.

    ARGS:
        artifacts_root (Path): Root directory to inspect.

    RETURNS:
        tuple[int, str]: `(0, message)` listing files found, else
        `(1, message)` if the root is missing or empty.
    """
    if not artifacts_root.exists():
        return 1, f"No artifacts found at {artifacts_root} (has `run` been executed yet?)"

    files = sorted(path for path in artifacts_root.rglob("*") if path.is_file())
    if not files:
        return 1, f"Artifacts root {artifacts_root} exists but contains no files."

    lines = [f"Artifacts under {artifacts_root}:"]
    lines.extend(f"  - {path.relative_to(artifacts_root)}" for path in files)
    return 0, "\n".join(lines)


__all__ = ["cmd_run", "cmd_status", "cmd_artifacts"]
