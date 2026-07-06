"""WHAT: `python -m engineering_studio.cli` package-execution entry point.
WHY: Running `python -m <package>` executes `<package>/__main__.py`, not
`<package>/__init__.py` — this file is required for the documented
`python -m engineering_studio.cli "<brief>"` invocation to work now that
`cli` is a package (see `__init__.py`'s module docstring for the history).
HOW: Delegates immediately to `main()`.
"""

from __future__ import annotations

from engineering_studio.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
