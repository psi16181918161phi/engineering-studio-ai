"""WHAT: `util` subpackage for `_professional_video_demo`.
WHY: Groups batch orchestration (`pipeline.py`) and output formatting
(`reporter.py`), separate from `core`'s per-video mechanics.
HOW: No re-exports here; import submodules directly or via the
package's top-level `__init__.py`.
"""

from __future__ import annotations
