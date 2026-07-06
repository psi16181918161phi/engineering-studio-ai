"""WHAT: Unit tests for the shared pydantic models (ProductBrief,
SpecialistArtifact, PipelineResult).
WHY: These are the typed contracts every SDK/CLI/API layer will depend on
going forward — must reach 100% coverage before those layers build on top.
HOW: Pure construction/validation assertions; no I/O, no model calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from engineering_studio.models import PipelineResult, ProductBrief, SpecialistArtifact


def test_product_brief_trims_whitespace() -> None:
    brief = ProductBrief(text="  build a drone  ")
    assert brief.text == "build a drone"


def test_product_brief_rejects_blank_text() -> None:
    with pytest.raises(PydanticValidationError):
        ProductBrief(text="   ")


def test_product_brief_rejects_empty_string() -> None:
    with pytest.raises(PydanticValidationError):
        ProductBrief(text="")


def test_specialist_artifact_rejects_blank_discipline(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        SpecialistArtifact(discipline="  ", output_path=tmp_path / "out.md")


def test_specialist_artifact_holds_path(tmp_path: Path) -> None:
    path = tmp_path / "mechanical" / "output.md"
    artifact = SpecialistArtifact(discipline="mechanical", output_path=path)
    assert artifact.output_path == path


def test_pipeline_result_from_pipeline_outputs_round_trips(tmp_path: Path) -> None:
    outputs = {
        "research": tmp_path / "research" / "output.md",
        "mechanical": tmp_path / "mechanical" / "output.md",
    }
    result = PipelineResult.from_pipeline_outputs("build a drone", outputs)

    assert result.product_brief.text == "build a drone"
    assert result.artifact_for("mechanical") == outputs["mechanical"]
    assert result.artifact_for("research") == outputs["research"]


def test_pipeline_result_artifact_for_raises_on_unknown_discipline(tmp_path: Path) -> None:
    result = PipelineResult.from_pipeline_outputs(
        "build a drone", {"research": tmp_path / "research" / "output.md"}
    )

    with pytest.raises(KeyError, match="electrical"):
        result.artifact_for("electrical")
