"""WHAT: Loads the filled Task Specification blocks from docs/task-specs.md
and exposes them as named system prompts per pipeline stage.
WHY: Task Specifications are the SCOPE-control contract (AGENTS.md §3) —
they must be authored once in docs/task-specs.md and reused verbatim by
every agent module, never re-typed inline (avoids drift, single source
of truth per DRY/SSOT).
HOW: Parses fenced ```markdown code blocks under H2 headings; returns a
dict keyed by a short stage id (orchestrator, research, mechanical, ...).
"""

from __future__ import annotations

import re
from pathlib import Path

_DOCS_PATH = Path(__file__).resolve().parents[2] / "docs" / "task-specs.md"

_STAGE_HEADING_PATTERN = re.compile(
    r"^## \d+\.\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)
_CODE_BLOCK_PATTERN = re.compile(r"```markdown\n(?P<body>.*?)```", re.DOTALL)


class TaskSpecNotFoundError(Exception):
    """Raised when a requested stage id has no matching Task Specification."""


def load_task_specs(docs_path: Path | None = None) -> dict[str, str]:
    """WHAT: Parses docs/task-specs.md into {stage_title_slug: spec_text}.

    ARGS:
        docs_path (Path | None): Override path, primarily for tests.

    RETURNS:
        dict[str, str]: Mapping of a slugified stage title to the fenced
        Task Specification body text for that stage.

    RAISES:
        FileNotFoundError: If docs/task-specs.md is missing.
    """
    path = docs_path or _DOCS_PATH
    text = path.read_text(encoding="utf-8")

    headings = list(_STAGE_HEADING_PATTERN.finditer(text))
    blocks = list(_CODE_BLOCK_PATTERN.finditer(text))

    specs: dict[str, str] = {}
    for heading, block in zip(headings, blocks):
        slug = re.sub(r"[^a-z0-9]+", "-", heading.group("title").lower()).strip("-")
        specs[slug] = block.group("body").strip()
    return specs


def get_task_spec(slug: str, docs_path: Path | None = None) -> str:
    """WHAT: Returns one stage's Task Specification text by slug.

    ARGS:
        slug (str): e.g. "orchestrator-decomposition-pass".
        docs_path (Path | None): Override path, primarily for tests.

    RETURNS:
        str: The Task Specification body.

    RAISES:
        TaskSpecNotFoundError: If no stage matches `slug`.
    """
    specs = load_task_specs(docs_path)
    if slug not in specs:
        raise TaskSpecNotFoundError(f"no task spec found for slug={slug!r}; have {list(specs)}")
    return specs[slug]
