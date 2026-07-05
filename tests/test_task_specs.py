"""WHAT: Unit tests for task_specs.py parsing.
WHY: docs/task-specs.md is the source of truth for every agent's system
prompt — a parsing regression would silently break SCOPE control.
HOW: Uses the real docs/task-specs.md (no live network calls needed).
"""

from __future__ import annotations

from engineering_studio.task_specs import get_task_spec, load_task_specs


def test_load_task_specs_finds_all_nine_stages() -> None:
    specs = load_task_specs()
    assert len(specs) == 9


def test_get_task_spec_returns_scope_declaration() -> None:
    spec = get_task_spec("mechanical-specialist-pass")
    assert "SCOPE:" in spec
    assert "artifacts/mechanical/" in spec
