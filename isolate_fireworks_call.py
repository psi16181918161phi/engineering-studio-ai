"""WHAT: Isolates ONE Fireworks chat-completion call from the full
Engineering Studio AI pipeline, so you can tell "is it the model or my
pipeline code?" in a single run.
WHY: Answers debugging questions 7 and 8 from the fireworks-integration
issue: exact request time / prompt size, and a way to test one simple
completion outside `run_pipeline()`.
HOW: Reads the same FIREWORKS_* env vars the real client reads, posts
one request directly with `requests`, and prints timing + the `usage`
block (prompt_tokens / completion_tokens / reasoning_tokens if present)
so you can see whether time is going into hidden reasoning tokens.

USAGE (from repo root, with .venv active and .env loaded):
    python isolate_fireworks_call.py accounts/fireworks/models/gpt-oss-120b
    python isolate_fireworks_call.py accounts/fireworks/models/gpt-oss-120b low
"""

from __future__ import annotations

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["FIREWORKS_BASE_URL"].rstrip("/")
API_KEY = os.environ["FIREWORKS_API_KEY"]

SYSTEM_PROMPT = "You are a concise engineering assistant."
USER_PROMPT = "In one paragraph, list the top 3 components of a warehouse robot."


def main() -> None:
    model = sys.argv[1] if len(sys.argv) > 1 else "accounts/fireworks/models/gpt-oss-120b"
    reasoning_effort = sys.argv[2] if len(sys.argv) > 2 else "low"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
        "max_tokens": 512,
        "reasoning_effort": reasoning_effort,
    }

    prompt_chars = len(SYSTEM_PROMPT) + len(USER_PROMPT)
    print(f"model={model!r} reasoning_effort={reasoning_effort!r} prompt_chars={prompt_chars}")

    start = time.perf_counter()
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload,
            timeout=90.0,
        )
    except requests.RequestException as exc:
        elapsed = time.perf_counter() - start
        print(f"FAILED after {elapsed:.2f}s: {exc}")
        return
    elapsed = time.perf_counter() - start

    print(f"HTTP {response.status_code} in {elapsed:.2f}s")
    if response.status_code != 200:
        print(response.text[:500])
        return

    data = response.json()
    usage = data.get("usage", {})
    print(f"usage: {usage}")  # look for reasoning_tokens / completion_tokens_details here
    print("--- content ---")
    print(data["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()