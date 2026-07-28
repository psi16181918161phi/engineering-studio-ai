"""WHAT: `util` subpackage for `_playwright_demo_script`.
WHY: Groups orchestration (`pipeline.py`) and output formatting
(`reporter.py`), separate from `core`'s per-scenario mechanics.
HOW: No re-exports here; import submodules directly or via the
package's top-level `__init__.py`.
"""

from __future__ import annotations
