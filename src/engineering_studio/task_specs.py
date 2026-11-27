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

_DOCUMENT_TOKEN = re.compile(
    r"^[ \t]*(?P<marker>(?P<delimiter>[`~])(?P=delimiter){2,})"
    r"(?P<info>[^`~\n]*)(?:\n|\Z)"
    r"(?P<body>(?s:.*?))(?:^[ \t]*(?P=marker)(?P=delimiter)*[ \t]*$|(?P<unclosed>\Z))"
    r"|^ {0,3}##[ \t]+\d+\.[ \t]*(?P<title>[^\n]*)$"
    r"|(?P<section>^ {0,3}#{1,2}(?:[ \t]+[^\n]*)?$)",
    re.MULTILINE,
)
_SLUG_SEPARATOR = re.compile(r"[^a-z0-9]+")
_NESTED_SPEC_FENCE = re.compile(r"^[ \t]*```[ \t]*markdown[ \t]*$", re.MULTILINE)


class TaskSpecNotFoundError(Exception):
    """Raised when a requested stage id has no matching Task Specification."""


class TaskSpecFormatError(ValueError):
    """WHAT: Report an invalid stage or code fence in a task spec document.

    WHY: Dispatch must not use a prompt assigned to the wrong stage.
    HOW: The message identifies the source path and line, excluding prompt text.
    """


def _require_stage_body(path: Path, slug: str | None, line: int, specs: dict[str, str]) -> None:
    """WHAT: Require the preceding numbered section to own a prompt.

    WHY: A later section's prompt cannot complete an earlier section.
    HOW: Check the current slug's membership at each boundary and at EOF.
    """
    if slug is not None and slug not in specs:
        raise TaskSpecFormatError(f"{path}:{line}: stage is missing a markdown block")


def load_task_specs(docs_path: Path | None = None) -> dict[str, str]:
    """WHAT: Parses docs/task-specs.md into {stage_title_slug: spec_text}.

    WHY: Each stage must get only the prompt authored in its own section.
    HOW: Treat backtick and tilde fences as opaque tokens and bind one
    nonempty triple-backtick Markdown block to each numbered ATX H2.
    This document grammar uses ATX headings and standalone code fences.

    ARGS:
        docs_path (Path | None): Override path, primarily for tests.

    RETURNS:
        dict[str, str]: Mapping of a slugified stage title to the fenced
        Task Specification body text for that stage.

    RAISES:
        FileNotFoundError: If docs/task-specs.md is missing.
        TaskSpecFormatError: If the document is malformed or ambiguous.
    """
    path = docs_path or _DOCS_PATH
    text = path.read_text(encoding="utf-8")

    specs: dict[str, str] = {}
    slug: str | None = None
    stage_line = 1
    line = 1
    previous_offset = 0
    for token in _DOCUMENT_TOKEN.finditer(text):
        line += text.count("\n", previous_offset, token.start())
        previous_offset = token.start()
        title = token.group("title")
        if token.group("section") is not None:
            _require_stage_body(path, slug, stage_line, specs)
            slug = None
            continue
        if title is not None:
            _require_stage_body(path, slug, stage_line, specs)
            slug = _SLUG_SEPARATOR.sub("-", title.lower()).strip("-")
            if not slug:
                raise TaskSpecFormatError(f"{path}:{line}: stage title has no slug")
            if slug in specs:
                raise TaskSpecFormatError(f"{path}:{line}: duplicate stage slug")
            stage_line = line
            continue

        if token.group("unclosed") is not None:
            raise TaskSpecFormatError(f"{path}:{line}: unclosed code fence")
        if token.group("marker") != "```" or token.group("info").strip() != "markdown":
            continue
        if slug is None:
            raise TaskSpecFormatError(f"{path}:{line}: markdown block outside a stage")
        if slug in specs:
            raise TaskSpecFormatError(f"{path}:{line}: stage has multiple markdown blocks")
        raw_body = token.group("body")
        if _NESTED_SPEC_FENCE.search(raw_body):
            raise TaskSpecFormatError(f"{path}:{line}: nested markdown fence")
        body = raw_body.strip()
        if not body:
            raise TaskSpecFormatError(f"{path}:{line}: empty markdown block")
        specs[slug] = body

    _require_stage_body(path, slug, stage_line, specs)
    if not specs:
        raise TaskSpecFormatError(f"{path}:1: no numbered task stages")
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
        TaskSpecFormatError: If the task specification document is malformed.
    """
    specs = load_task_specs(docs_path)
    if slug not in specs:
        raise TaskSpecNotFoundError(f"no task spec found for slug={slug!r}; have {list(specs)}")
    return specs[slug]
