"""WHAT: Base class for a single-responsibility specialist agent that
writes only to its own artifact folder.
WHY: Enforces AGENTS.md §3 (SCOPE control) and §2 (SRP) in code, not just
in the prompt text — a specialist literally cannot construct a path
outside its own folder.
HOW: `SpecialistAgent.run()` calls the model client, then writes the
reply to `<artifacts_root>/<discipline>/output.md` via a temp-then-rename
write (ACID-lite durability, AGENTS.md §2).
"""

from __future__ import annotations

import os
from pathlib import Path

from engineering_studio.fireworks_client import ModelClient


class SpecialistAgent:
    """WHAT: One specialist's model-call-and-write-artifact unit of work.

    ATTRIBUTES:
        discipline (str): Folder name under artifacts/, e.g. "mechanical".
        client (ModelClient): The model backend this specialist calls.
        artifacts_root (Path): Root of the artifacts/ tree.

    WHY: SRP — a SpecialistAgent only produces its own artifact; it never
    reads or writes another discipline's folder (enforced by construction,
    see `_output_path`).

    HOW: Stateless aside from construction args; safe to instantiate one
    per specialist and dispatch concurrently.
    """

    def __init__(self, discipline: str, client: ModelClient, artifacts_root: Path) -> None:
        self.discipline = discipline
        self.client = client
        self.artifacts_root = artifacts_root

    def _output_path(self) -> Path:
        """WHAT: Resolves this specialist's own artifact file path.

        RETURNS:
            Path: `<artifacts_root>/<discipline>/output.md`.

        HOW: Always derived from `self.discipline` — no caller-supplied
        path is ever accepted, which is what makes cross-folder writes
        structurally impossible for this class.
        """
        folder = self.artifacts_root / self.discipline
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "output.md"

    def run(self, system_prompt: str, user_prompt: str) -> Path:
        """WHAT: Calls the model and durably writes the result artifact.

        ARGS:
            system_prompt (str): The stage's Task Specification text.
            user_prompt (str): Upstream artifacts / product brief content.

        RETURNS:
            Path: The written artifact file path.

        RAISES:
            ModelUnavailableError: Propagated from the model client on
                failure — never swallowed into a fabricated artifact.
        """
        reply = self.client.complete(system_prompt, user_prompt)
        final_path = self._output_path()
        tmp_path = final_path.with_suffix(".md.tmp")
        tmp_path.write_text(reply, encoding="utf-8")
        os.replace(tmp_path, final_path)
        return final_path
