"""WHAT: Cross-cutting decorators shared by SDK/CLI/API/webapp/GUI code.
WHY: Keeps logging, argument validation, and environment-variable checks
out of every call site (SOLID SRP — one decorator, one concern) while
still enforcing NASA/JPL Power-of-Ten rule 6 (check every fallible call)
and rule 4 (validate preconditions at boundaries).
HOW: Three decorators: `log_call` (structured before/after/error logging,
never logs argument values), `validate_args` (runs a caller-supplied
predicate over call arguments before the wrapped function executes), and
`requires_env` (raises `ConfigurationError` up front if named environment
variables are unset, rather than letting a downstream error surface deep
in the call stack).
"""

from __future__ import annotations

import functools
import logging
import os
from collections.abc import Callable
from typing import Any, TypeVar

from engineering_studio.exceptions import ConfigurationError

_LOGGER = logging.getLogger("engineering_studio")

F = TypeVar("F", bound=Callable[..., Any])


def log_call(func: F) -> F:
    """WHAT: Logs function entry, successful exit, and any raised exception.

    ARGS:
        func (Callable): The function to wrap.

    RETURNS:
        Callable: The wrapped function, with identical signature/behavior.

    WHY: Gives every decorated call point consistent, greppable log lines
    without repeating boilerplate at each call site.

    HOW: Logs `func.__qualname__` only — never argument values, since
    those may contain product briefs or other user content not meant for
    log aggregation without redaction review.
    """

    @functools.wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        _LOGGER.debug("enter %s", func.__qualname__)
        try:
            result = func(*args, **kwargs)
        except Exception:
            _LOGGER.exception("error in %s", func.__qualname__)
            raise
        _LOGGER.debug("exit %s", func.__qualname__)
        return result

    return _wrapper  # type: ignore[return-value]


def validate_args(predicate: Callable[..., bool], message: str) -> Callable[[F], F]:
    """WHAT: Decorator factory that validates call arguments before the
    wrapped function runs.

    ARGS:
        predicate (Callable[..., bool]): Called with the same arguments as
            the wrapped function; must return `True` to proceed.
        message (str): Error text raised via `ValidationError` when the
            predicate returns `False`.

    RETURNS:
        Callable[[F], F]: A decorator applying this validation.

    WHY: Fails fast on invalid input before any model call or I/O happens
    (Power-of-Ten rule 4 — assertion density at function boundaries).
    """

    def _decorator(func: F) -> F:
        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            from engineering_studio.exceptions import ValidationError

            if not predicate(*args, **kwargs):
                raise ValidationError(message)
            return func(*args, **kwargs)

        return _wrapper  # type: ignore[return-value]

    return _decorator


def requires_env(*names: str) -> Callable[[F], F]:
    """WHAT: Decorator factory that ensures named environment variables are
    set before the wrapped function executes.

    ARGS:
        *names (str): Environment variable names that must be non-empty.

    RETURNS:
        Callable[[F], F]: A decorator enforcing this precondition.

    RAISES:
        ConfigurationError: If any named variable is unset or empty, listing
            every missing name (not just the first) so a caller can fix all
            of them in one pass.

    WHY: Turns a downstream error deep inside a call chain into one clear,
    actionable error raised at the boundary.
    """

    def _decorator(func: F) -> F:
        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            missing = [name for name in names if not os.environ.get(name)]
            if missing:
                raise ConfigurationError(
                    f"{func.__qualname__} requires environment variable(s) "
                    f"not set: {', '.join(missing)} (see .env.example)."
                )
            return func(*args, **kwargs)

        return _wrapper  # type: ignore[return-value]

    return _decorator


__all__ = ["log_call", "validate_args", "requires_env"]
