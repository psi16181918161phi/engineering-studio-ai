"""WHAT: Unit tests for the domain exception hierarchy.
WHY: Every subclass must chain to `EngineeringStudioError` -> `Exception` so
callers can catch broadly or narrowly; also verifies `fireworks_client`'s
`ModelUnavailableError` joined the hierarchy without breaking its identity.
HOW: Pure `isinstance`/`issubclass` assertions — no I/O, no network.
"""

from __future__ import annotations

import pytest

from engineering_studio.exceptions import (
    ArtifactWriteError,
    ConfigurationError,
    EngineeringStudioError,
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exc_type",
    [
        ConfigurationError,
        ModelUnavailableError,
        ValidationError,
        PipelineExecutionError,
        ArtifactWriteError,
    ],
)
def test_all_subclasses_chain_to_base(exc_type: type[Exception]) -> None:
    assert issubclass(exc_type, EngineeringStudioError)
    assert issubclass(exc_type, Exception)


def test_base_is_a_plain_exception_subclass() -> None:
    assert issubclass(EngineeringStudioError, Exception)


def test_instances_carry_message() -> None:
    err = ConfigurationError("FIREWORKS_API_KEY is not set")
    assert str(err) == "FIREWORKS_API_KEY is not set"


def test_fireworks_client_model_unavailable_error_joins_hierarchy() -> None:
    from engineering_studio.fireworks_client import (
        ModelUnavailableError as ClientModelUnavailableError,
    )

    assert issubclass(ClientModelUnavailableError, EngineeringStudioError)


def test_pipeline_execution_error_preserves_cause() -> None:
    original = ValueError("upstream failure")
    try:
        try:
            raise original
        except ValueError as exc:
            raise PipelineExecutionError("pipeline aborted") from exc
    except PipelineExecutionError as pipeline_exc:
        assert pipeline_exc.__cause__ is original
