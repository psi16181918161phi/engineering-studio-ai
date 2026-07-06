"""WHAT: Unit tests for the cross-cutting decorators (log_call, validate_args,
requires_env).
WHY: Each decorator sits at every future SDK/CLI/API/webapp/GUI call
boundary — must reach 100% coverage before those layers can rely on it.
HOW: No network/model calls; uses plain functions and `monkeypatch` for
environment variable manipulation.
"""

from __future__ import annotations

import logging

import pytest

from engineering_studio.decorators import log_call, requires_env, validate_args
from engineering_studio.exceptions import ConfigurationError, ValidationError


def test_log_call_returns_wrapped_result_and_preserves_name() -> None:
    @log_call
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add"


def test_log_call_logs_and_reraises_on_exception(caplog: pytest.LogCaptureFixture) -> None:
    @log_call
    def boom() -> None:
        raise RuntimeError("kaboom")

    with caplog.at_level(logging.DEBUG, logger="engineering_studio"):
        with pytest.raises(RuntimeError, match="kaboom"):
            boom()

    assert any("error in" in record.message for record in caplog.records)


def test_validate_args_allows_call_when_predicate_true() -> None:
    @validate_args(lambda x: x > 0, "x must be positive")
    def double(x: int) -> int:
        return x * 2

    assert double(3) == 6


def test_validate_args_raises_validation_error_when_predicate_false() -> None:
    @validate_args(lambda x: x > 0, "x must be positive")
    def double(x: int) -> int:
        return x * 2

    with pytest.raises(ValidationError, match="x must be positive"):
        double(-1)


def test_requires_env_passes_when_all_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXAMPLE_VAR", "value")

    @requires_env("EXAMPLE_VAR")
    def needs_var() -> str:
        return "ok"

    assert needs_var() == "ok"


def test_requires_env_raises_configuration_error_listing_all_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MISSING_VAR_1", raising=False)
    monkeypatch.delenv("MISSING_VAR_2", raising=False)

    @requires_env("MISSING_VAR_1", "MISSING_VAR_2")
    def needs_vars() -> str:
        return "unreachable"

    with pytest.raises(ConfigurationError) as exc_info:
        needs_vars()

    assert "MISSING_VAR_1" in str(exc_info.value)
    assert "MISSING_VAR_2" in str(exc_info.value)
