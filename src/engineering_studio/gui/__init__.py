"""WHAT: `textual` TUI application consuming the SDK directly (W6b).
WHY: A distinct Python-native interface from the browser webapp
(PREPLAN Q3) — runs in any terminal, matching the CLI's existing
runtime assumptions, and exercises `sdk.EngineeringStudioClient`
directly (not the HTTP API), since a local terminal app has no need for
a transport hop. Styled exclusively from `utils.palette.PALETTE_B` (the
mandated Variant B interface-surface palette) via `textual` CSS
variables — no widget hard-codes a color literal.
HOW: One `textual.app.App` subclass, `EngineeringStudioApp`, with an
`Input` for the product brief, a "Run pipeline" `Button`, a read-only
model-routing `Static` panel, and a `RichLog` for output. Business logic
(turning an `EngineeringStudioClient` outcome into display lines) lives in
the free function `format_pipeline_outcome()` so it can be unit-tested
without booting the TUI event loop; `EngineeringStudioApp` itself is
covered via `textual`'s headless `Pilot` API (`app.run_test()`). The
model-routing panel (OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md Phase 4.4) reuses
`sdk.get_model_info` — the exact same provider-agnostic (Fireworks/OpenAI)
factory the `/api/models` route and the CLI `models` subcommand consume —
so all three surfaces report identical model-routing state; it never
displays an API key value.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from engineering_studio.exceptions import (
    ModelUnavailableError,
    PipelineExecutionError,
    ValidationError,
)
from engineering_studio.models import PipelineResult
from engineering_studio.sdk import PROVIDERS, ROLES, EngineeringStudioClient, get_model_info
from engineering_studio.utils.palette import get_palette_for_surface

_DEFAULT_ARTIFACTS_ROOT = Path("runs") / "latest" / "artifacts"
_PALETTE = get_palette_for_surface("gui")


def format_pipeline_outcome(result: PipelineResult) -> str:
    """WHAT: Renders a `PipelineResult` as multi-line display text.

    ARGS:
        result (PipelineResult): A successful pipeline outcome.

    RETURNS:
        str: One header line plus one line per artifact.

    WHY: Pure function, no widget/event-loop dependency, so this
    formatting is unit-testable in isolation from the TUI itself.
    """
    lines = [f"Brief: {result.product_brief.text!r}"]
    lines.extend(
        f"  {artifact.discipline:12s} -> {artifact.output_path}" for artifact in result.artifacts
    )
    return "\n".join(lines)


def format_model_routing_panel() -> str:
    """WHAT: Renders the current model-routing state as multi-line text.

    RETURNS:
        str: One header line plus one line per (provider, role) pair from
        `sdk.PROVIDERS` x `sdk.ROLES`, e.g.
        "  fireworks specialist -> accounts/fireworks/models/gpt-oss-120b".
        A role whose environment variable is unset renders as
        "(not configured)" — never a fabricated model id.

    WHY: Pure function, no widget/event-loop dependency, so this panel's
    content is unit-testable in isolation from the TUI itself — mirrors
    `format_pipeline_outcome()`'s existing pattern.
    """
    lines = ["Model routing (provider -> role -> model):"]
    for provider in PROVIDERS:
        for role in ROLES:
            info = get_model_info(provider, role)
            model_display = info.model if info.configured else "(not configured)"
            lines.append(f"  {provider:10s} {role:12s} -> {model_display}")
    return "\n".join(lines)


class EngineeringStudioApp(App[None]):
    """WHAT: The Engineering Studio AI terminal (TUI) application.

    ATTRIBUTES:
        client (EngineeringStudioClient): The SDK client this app drives.

    WHY: SRP — this class only wires widgets to the SDK and displays
    outcomes/errors; it contains no pipeline logic of its own.
    """

    CSS = f"""
    Screen {{
        background: {_PALETTE.background};
        color: {_PALETTE.foreground_primary};
    }}
    Button {{
        background: {_PALETTE.accent};
        color: {_PALETTE.background};
    }}
    #brief_input {{
        border: solid {_PALETTE.accent};
    }}
    #model_routing_panel {{
        color: {_PALETTE.muted};
        border: solid {_PALETTE.accent};
        padding: 0 1;
    }}
    """

    def __init__(self, artifacts_root: Path | str | None = None) -> None:
        """WHAT: Constructs the app bound to one SDK client.

        ARGS:
            artifacts_root (Path | str | None): Forwarded to
                `EngineeringStudioClient`; defaults to
                `runs/latest/artifacts`.
        """
        super().__init__()
        self.client = EngineeringStudioClient(
            artifacts_root=Path(artifacts_root)
            if artifacts_root is not None
            else _DEFAULT_ARTIFACTS_ROOT
        )

    def compose(self) -> ComposeResult:
        """WHAT: Declares the app's widget tree."""
        yield Header()
        with Vertical():
            yield Input(placeholder="Product brief…", id="brief_input")
            yield Button("Run pipeline", id="run_button", variant="primary")
            yield Static(format_model_routing_panel(), id="model_routing_panel")
            yield RichLog(id="output_log", wrap=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """WHAT: Handles the "Run pipeline" button by validating and
        running the pipeline via `self.client`, then writing the outcome
        (or a domain error message) to the output log.

        WHY: Every domain exception is caught and displayed, never
        silently swallowed (Power-of-Ten rule 6 / live-data-honesty) —
        no fabricated success message is ever written on failure.
        """
        if event.button.id != "run_button":
            return
        brief_input = self.query_one("#brief_input", Input)
        output_log = self.query_one("#output_log", RichLog)
        try:
            result = self.client.run(brief_input.value)
        except ValidationError as exc:
            output_log.write(f"[error] Invalid product brief: {exc}")
            return
        except ModelUnavailableError as exc:
            output_log.write(f"[error] Model call failed — no fabricated result: {exc}")
            return
        except PipelineExecutionError as exc:
            output_log.write(f"[error] Pipeline execution failed: {exc}")
            return
        output_log.write(format_pipeline_outcome(result))


def main() -> None:
    """WHAT: `python -m engineering_studio.gui` entry point.

    WHY: `App.run()` takes over the real terminal (alternate screen
    buffer, raw input mode) and blocks until the user quits — it is
    intentionally excluded from coverage (`pragma: no cover`) rather than
    invoked under test, the same way `cli/__main__.py`'s
    `if __name__ == "__main__":` guard is excluded; `EngineeringStudioApp`
    itself is fully covered via the headless `Pilot` API in
    `tests/test_gui.py`.
    """
    EngineeringStudioApp().run()  # pragma: no cover


__all__ = ["EngineeringStudioApp", "format_model_routing_panel", "format_pipeline_outcome", "main"]
