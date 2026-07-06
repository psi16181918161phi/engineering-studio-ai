"""WHAT: In-process programmatic SDK: `EngineeringStudioClient`.
WHY: Gives other tools/scripts (and future `../frontend/`, `../webapp/`,
`../api/`, `../gui/` layers) a stable, typed import path to drive the
pipeline without going through the CLI's argv parsing or an HTTP
transport, and without importing `agents.orchestrator` internals or
handling raw `dict[str, Path]` outputs directly.
HOW: `EngineeringStudioClient.run()` validates the brief via
`models.ProductBrief`, delegates to `agents.orchestrator.run_pipeline`,
and returns a typed `models.PipelineResult`. Domain failures are
normalized to this package's `exceptions` hierarchy: a `ModelUnavailableError`
from the pipeline propagates as-is (it is already a domain-specific,
publicly meaningful error); a pydantic validation failure on the input
brief is re-raised as `exceptions.ValidationError`; any other unexpected
failure during the pipeline run is wrapped in `exceptions.PipelineExecutionError`
(via `raise ... from exc`, preserving the original cause) so callers only
ever need to catch this package's own exception types.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError as _PydanticValidationError

from engineering_studio.agents.orchestrator import run_pipeline
from engineering_studio.exceptions import (
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)
from engineering_studio.models import PipelineResult, ProductBrief

_DEFAULT_ARTIFACTS_ROOT = Path("runs") / "latest" / "artifacts"


class EngineeringStudioClient:
    """WHAT: Thin, typed, in-process client wrapping the studio pipeline.

    ATTRIBUTES:
        artifacts_root (Path): Root directory all artifacts are written
            under; created on `run()` if it does not already exist.

    WHY: SRP — this class only validates input, delegates to the
    orchestrator, and normalizes the result/errors into this package's
    typed contracts; it contains no pipeline logic of its own.
    """

    def __init__(self, artifacts_root: Path | str | None = None) -> None:
        """WHAT: Constructs a client bound to one artifacts root directory.

        ARGS:
            artifacts_root (Path | str | None): Where artifacts are
                written. Defaults to `runs/latest/artifacts` (relative to
                the current working directory) to match the CLI's default.
        """
        self.artifacts_root = (
            Path(artifacts_root) if artifacts_root is not None else _DEFAULT_ARTIFACTS_ROOT
        )

    def run(self, product_brief: str) -> PipelineResult:
        """WHAT: Validates `product_brief` and runs the full studio pipeline.

        ARGS:
            product_brief (str): One-sentence hackathon demo prompt.

        RETURNS:
            PipelineResult: The typed pipeline outcome (validated brief +
            one `SpecialistArtifact` per stage that produced output).

        RAISES:
            ValidationError: If `product_brief` is blank/whitespace-only
                or exceeds the length limit — raised before any model
                call is made.
            ModelUnavailableError: Propagated unchanged from the pipeline
                if an inference backend could not be reached.
            PipelineExecutionError: Wraps any other unexpected failure
                during the pipeline run, preserving the original error as
                `__cause__`.
        """
        try:
            brief = ProductBrief(text=product_brief)
        except _PydanticValidationError as exc:
            raise ValidationError(str(exc)) from exc

        self.artifacts_root.mkdir(parents=True, exist_ok=True)

        try:
            outputs = run_pipeline(brief.text, self.artifacts_root)
        except ModelUnavailableError:
            raise
        except Exception as exc:
            raise PipelineExecutionError(f"pipeline aborted: {exc}") from exc

        return PipelineResult.from_pipeline_outputs(brief.text, outputs)


__all__ = ["EngineeringStudioClient"]
