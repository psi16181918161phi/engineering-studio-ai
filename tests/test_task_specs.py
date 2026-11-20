"""WHAT: Unit tests for task_specs.py parsing.
WHY: docs/task-specs.md is the source of truth for every agent's system
prompt — a parsing regression would silently break SCOPE control.
HOW: Uses the real docs/task-specs.md (no live network calls needed).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio.task_specs import (
    TaskSpecFormatError,
    TaskSpecNotFoundError,
    get_task_spec,
    load_task_specs,
)


def test_load_task_specs_finds_all_twelve_stages() -> None:
    specs = load_task_specs()
    assert len(specs) == 12
    assert "reviewer-critique-pass" in specs
    assert "exploratory-qa-scenario-pass" in specs
    assert "validator-cross-consistency-pass" in specs


def test_get_task_spec_returns_scope_declaration() -> None:
    spec = get_task_spec("mechanical-specialist-pass")
    assert "SCOPE:" in spec
    assert "artifacts/mechanical/" in spec


def test_get_task_spec_raises_for_unknown_slug() -> None:
    with pytest.raises(TaskSpecNotFoundError, match="no-such-slug"):
        get_task_spec("no-such-slug")


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_stage_owns_only_its_markdown_block(tmp_path: Path, newline: str) -> None:
    """WHAT: Verify correct prompt boundaries and literal prompt content.

    WHY: Stage-like headings in examples or prompts must not change routing.
    HOW: Parse equivalent LF and CRLF files, including a fence at EOF.
    """
    lines = [
        "# Task document",
        "```text",
        "## 1. Example heading",
        "```",
        "~~~~text",
        "## 1. Tilde example heading",
        "```markdown",
        "tilde example body",
        "```",
        "~~~~",
        "````text",
        "## 1. Longer backtick example heading",
        "```markdown",
        "longer example body",
        "```",
        "`````",
        "## 3. Mechanical / Design",
        "### Section note",
        "```markdown",
        "  First line  ",
        "## 4. Prompt heading",
        "inline ``` token",
        "```",
        "   ## 9. Electrical",
        "```markdown",
        "second body",
        "```",
    ]
    path = tmp_path / "task-specs.md"
    path.write_bytes(newline.join(lines).encode())

    result = load_task_specs(path)

    assert list(result) == ["mechanical-design", "electrical"]
    assert result == {
        "mechanical-design": "First line  \n## 4. Prompt heading\ninline ``` token",
        "electrical": "second body",
    }


_FIRST_STAGE = "## 1. First Stage\n```markdown\nfirst body\n```\n"


@pytest.mark.parametrize(
    ("text", "line", "message"),
    [
        ("# Intro\n", 1, "no numbered task stages"),
        ("## 1. !!!\n", 1, "stage title has no slug"),
        ("```markdown\norphan\n```\n", 1, "markdown block outside a stage"),
        ("## 1. Empty\n```markdown\n \t\n```\n", 2, "empty markdown block"),
        ("## 1. Never closed\n```markdown\nbody\n", 2, "unclosed code fence"),
        (
            "## 1. Unclosed\n```markdown\nfirst\n## 2. Second\n```markdown\nsecond\n```\n",
            2,
            "nested markdown fence",
        ),
        (
            "## 1. Missing\n## 2. Next\n```markdown\nnext\n```\n",
            1,
            "stage is missing a markdown block",
        ),
        (
            "## 1. Missing\n## Appendix\n```markdown\nappendix\n```\n",
            1,
            "stage is missing a markdown block",
        ),
        (
            "## 1. Missing\n  ## Appendix\n```markdown\nappendix\n```\n",
            1,
            "stage is missing a markdown block",
        ),
        (
            "## 1. Missing\n# Appendix\n```markdown\nappendix\n```\n",
            1,
            "stage is missing a markdown block",
        ),
        (
            _FIRST_STAGE + "## Appendix\n```markdown\nappendix\n```\n",
            6,
            "markdown block outside a stage",
        ),
        (
            _FIRST_STAGE + "## 2. Missing\n```text\nexample\n```\n",
            5,
            "stage is missing a markdown block",
        ),
        (_FIRST_STAGE + "```markdown\nextra\n```\n", 5, "stage has multiple markdown blocks"),
        (_FIRST_STAGE + "## 2. FIRST-stage\n", 5, "duplicate stage slug"),
    ],
)
def test_malformed_document_fails_before_serving_any_stage(
    tmp_path: Path, text: str, line: int, message: str
) -> None:
    """WHAT: Require an explicit format error for malformed specifications.

    WHY: A plausible early prompt must not hide an invalid later section.
    HOW: Dispatch against each fixture and verify the error and source line.
    """
    path = tmp_path / "task-specs.md"
    path.write_text(text, encoding="utf-8")

    with pytest.raises(TaskSpecFormatError) as error:
        get_task_spec("first-stage", path)

    assert str(error.value) == f"{path}:{line}: {message}"
