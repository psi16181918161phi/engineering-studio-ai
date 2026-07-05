"""WHAT: Unit tests for SpecialistAgent's write-scope enforcement.
WHY: AGENTS.md §3 requires a specialist can never write outside its own
artifact folder — this is a structural/code guarantee, test it as such.
HOW: A fake ModelClient (no network) returns canned text; asserts the
written file always lands under artifacts/<discipline>/.
"""

from __future__ import annotations

from pathlib import Path

from engineering_studio.agents.specialist import SpecialistAgent


class _FakeClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return f"reply to: {user_prompt[:20]}"


def test_specialist_writes_only_to_own_folder(tmp_path: Path) -> None:
    agent = SpecialistAgent("mechanical", _FakeClient(), tmp_path)  # type: ignore[arg-type]
    output_path = agent.run("system prompt", "user prompt")

    assert output_path == tmp_path / "mechanical" / "output.md"
    assert output_path.read_text(encoding="utf-8").startswith("reply to:")
    assert not (tmp_path / "electrical").exists()
