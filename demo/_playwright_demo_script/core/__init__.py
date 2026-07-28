"""WHAT: `core` subpackage for `_playwright_demo_script`.
WHY: Groups pure/isolated I/O helpers (naming, server bootstrap,
recording) per SOLID SRP.
HOW: No re-exports here; import submodules directly or via the
package's top-level `__init__.py`.
"""

from __future__ import annotations
