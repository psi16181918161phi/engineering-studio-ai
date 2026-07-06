"""
run_scripts — Project-agnostic build pipeline suite.

WHAT: Package init for the project-agnostic run_scripts build pipeline suite.
      Exports the package version and the canonical main() entry point.

WHY:  A consistent package init enables `python -m run_scripts` invocation and
      provides a single authoritative version constant for all tooling.

HOW:  Defines __version__ and imports main from __main__ for programmatic use.
      All constants are module-level and frozen (REQ-FP-04).

Cross-references:
    REQ-FP-01   (I/O isolated, labelled # IMPURE)
    REQ-FP-04   (frozen module-level constants)
    G-07        (callable standalone: python -m run_scripts)
"""
from __future__ import annotations

__version__: str = "1.0.0"
__author__: str = "Hadrian Hu"
__all__: list[str] = ["__version__", "__author__"]
