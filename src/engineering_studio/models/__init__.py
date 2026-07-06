"""WHAT: Shared pydantic data models/schemas for Engineering Studio AI.
WHY: Centralizes typed contracts (product brief input, per-discipline
artifact records, whole-pipeline results) for use across agents, the SDK,
CLI, and API layers, rather than passing untyped dicts/strings between
modules.
HOW: Three models: `ProductBrief` (validated input text), `SpecialistArtifact`
(one discipline's output path record), and `PipelineResult` (the full
`run_pipeline()` outcome, replacing the current bare `dict[str, Path]`
return type with a typed, constructible wrapper).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBrief(BaseModel):
    """WHAT: A validated, one-sentence hackathon demo prompt.

    ATTRIBUTES:
        text (str): The brief itself, 1-2000 characters, whitespace-trimmed.

    WHY: Fails fast on blank/oversized input before any model call is made,
    rather than letting an empty string silently propagate into a prompt.
    """

    text: str = Field(..., min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("product brief text must not be blank/whitespace-only")
        return stripped


class SpecialistArtifact(BaseModel):
    """WHAT: One specialist discipline's written output record.

    ATTRIBUTES:
        discipline (str): Folder name under artifacts/, e.g. "mechanical".
        output_path (Path): Path to the written artifact file.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    discipline: str = Field(..., min_length=1)
    output_path: Path

    @field_validator("discipline")
    @classmethod
    def _discipline_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("discipline must not be blank/whitespace-only")
        return stripped


class PipelineResult(BaseModel):
    """WHAT: The full outcome of one `run_pipeline()` invocation.

    ATTRIBUTES:
        product_brief (ProductBrief): The validated input that drove this run.
        artifacts (list[SpecialistArtifact]): One entry per discipline stage
            that produced an output (research, business, plus each parallel
            specialist).

    WHY: Replaces the orchestrator's current bare `dict[str, Path]` return
    value with a typed, self-describing result the SDK/CLI/API layers can
    depend on directly.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    product_brief: ProductBrief
    artifacts: list[SpecialistArtifact]

    @classmethod
    def from_pipeline_outputs(
        cls, product_brief: str, outputs: dict[str, Path]
    ) -> PipelineResult:
        """WHAT: Builds a `PipelineResult` from the orchestrator's raw output.

        ARGS:
            product_brief (str): The raw brief text passed to `run_pipeline`.
            outputs (dict[str, Path]): The `{discipline: output_path}` mapping
                `run_pipeline()` currently returns.

        RETURNS:
            PipelineResult: The typed equivalent of `outputs`.
        """
        return cls(
            product_brief=ProductBrief(text=product_brief),
            artifacts=[
                SpecialistArtifact(discipline=discipline, output_path=path)
                for discipline, path in outputs.items()
            ],
        )

    def artifact_for(self, discipline: str) -> Path:
        """WHAT: Looks up one discipline's output path by name.

        ARGS:
            discipline (str): e.g. "mechanical".

        RETURNS:
            Path: That discipline's output file path.

        RAISES:
            KeyError: If no artifact was recorded for `discipline`.
        """
        for artifact in self.artifacts:
            if artifact.discipline == discipline:
                return artifact.output_path
        raise KeyError(f"no artifact recorded for discipline={discipline!r}")


__all__ = ["ProductBrief", "SpecialistArtifact", "PipelineResult"]
