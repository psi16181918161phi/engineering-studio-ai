"""WHAT: Domain exception hierarchy for Engineering Studio AI.
WHY: A single, importable base (`EngineeringStudioError`) lets SDK/CLI/API/
webapp/GUI callers catch *any* domain failure with one `except` clause,
while still distinguishing failure classes (config vs. model vs. pipeline
vs. validation) when they need to. Ties into NASA/JPL Power-of-Ten rule 6
(check every fallible call; never silently swallow an error) and the
live-data-honesty rule in AGENTS.md SS5 (never fabricate a success).
HOW: A shallow, flat hierarchy — no deep inheritance chains (Power-of-Ten
rule 8: limit indirection). Each subclass adds no behavior, only identity,
so `isinstance` checks stay cheap and predictable.
"""

from __future__ import annotations


class EngineeringStudioError(Exception):
    """WHAT: Base class for every domain-specific error raised by this package.

    WHY: Callers across SDK/CLI/API/webapp/GUI can catch this one type to
    handle "something in the studio pipeline failed" without needing to
    know every specific subclass in advance.

    HOW: Plain `Exception` subclass; carries no additional state beyond
    the standard `args` message tuple.
    """


class ConfigurationError(EngineeringStudioError):
    """WHAT: Raised when required configuration (env vars, files) is missing
    or invalid.

    WHY: Distinguishes "you forgot to set something up" from a runtime
    model/pipeline failure, so CLI/API callers can print a fix-it message
    instead of a stack trace.
    """


class ModelUnavailableError(EngineeringStudioError):
    """WHAT: Raised when an inference backend cannot be reached or returns
    an error.

    WHY: Re-exported here (in addition to
    `engineering_studio.fireworks_client.ModelUnavailableError`, which now
    also inherits from `EngineeringStudioError`) so SDK/CLI/API code can
    depend on the exceptions package alone without importing the concrete
    Fireworks client module.
    """


class ValidationError(EngineeringStudioError):
    """WHAT: Raised when caller-supplied input (e.g. a product brief) fails
    domain validation before any model call is made.

    WHY: Fails fast, before spending an inference call on invalid input.
    """


class PipelineExecutionError(EngineeringStudioError):
    """WHAT: Raised when the orchestrated pipeline fails partway through,
    wrapping whichever stage-specific error caused the abort.

    WHY: Gives SDK/CLI/API callers one exception type to catch for "the
    pipeline did not complete", while `__cause__` (via `raise ... from exc`)
    preserves the original stage-level error for diagnostics.
    """


class ArtifactWriteError(EngineeringStudioError):
    """WHAT: Raised when a specialist agent's artifact cannot be written to
    its designated folder (e.g. permissions, disk full, invalid path).

    WHY: Distinguishes an I/O failure from a model failure — both look like
    "the pipeline didn't finish" to a caller, but need different remediation.
    """


__all__ = [
    "EngineeringStudioError",
    "ConfigurationError",
    "ModelUnavailableError",
    "ValidationError",
    "PipelineExecutionError",
    "ArtifactWriteError",
]
