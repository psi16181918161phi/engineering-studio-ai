"""WHAT: Enables `python -m demo._professional_video_demo` invocation.
WHY: SCOPE §3 (def main() + __name__ guard) and SOLID SRP.
HOW: Delegates immediately to `main.main()`.
"""

from __future__ import annotations

import sys

from .main import main

if __name__ == "__main__":  # pragma: no cover - process entry point
    sys.exit(main())
