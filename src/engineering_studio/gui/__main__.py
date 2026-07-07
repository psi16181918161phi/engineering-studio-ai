"""WHAT: `python -m engineering_studio.gui` package-execution entry point.
WHY: Running `python -m <package>` executes `<package>/__main__.py`, not
`<package>/__init__.py` — mirrors `cli/__main__.py`'s pattern.
HOW: Delegates immediately to `main()`.
"""

from __future__ import annotations

from engineering_studio.gui import main

if __name__ == "__main__":
    main()
