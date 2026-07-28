"""WHAT: Short, stable kebab-case slug helper for a demo prompt.
WHY: Isolated as a pure function (FP §3) so it is trivially unit tested
and reusable by `demo._professional_video_demo` without duplication.
HOW: First 5 significant words, lowercased, non-alphanumerics stripped —
matches the original script's naming convention.
"""

from __future__ import annotations

import re


def slugify(text: str) -> str:
    """WHAT: Converts free text into a short, stable kebab-case id.

    ARGS:
        text (str): Arbitrary prompt/description text.

    RETURNS:
        str: First 5 significant (alphanumeric) words, lowercased and
        hyphen-joined.
    """
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(words[:5])
