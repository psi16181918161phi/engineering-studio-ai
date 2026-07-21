"""WHAT: Mode-A/Mode-B screen-recording demo script — drives the real
webapp with Playwright, capturing per-stage screenshots and a full video
per (theme, demo prompt) combination, saved under `demo/recordings/`.
WHY: Implements `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` §11 (theme-aware
screen-recording execution plan) so the hackathon submission has real,
reviewable evidence of the multi-agent pipeline running end-to-end in
both Light Mode and Dark Mode, for each of the 3 confirmed demo prompts
(§7). Captures only the dashboard viewport — never the OS desktop, VS
Code, or any other unrelated window (§8).
HOW: Defaults to **Mode B** (`ENGINEERING_STUDIO_FAKE_PIPELINE=1`,
deterministic, no Fireworks API key needed) per explicit user
confirmation — pass `--live` to instead run Mode A against the real
pipeline (requires a valid `FIREWORKS_API_KEY` in `.env`; NOT the
default, since a missing/invalid key would otherwise silently produce a
misleading recording). Not part of the pytest suite — run directly:

    python demo/playwright_demo_script.py [--theme light|dark] [--live]
"""

from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDINGS_ROOT = REPO_ROOT / "demo" / "recordings"

DEMO_PROMPTS = [
    "Create a Python script that automates the backup of important files to a cloud storage service.",
    "Develop a simple web application that allows users to track their daily habits and visualize their progress over time.",
    "Write a command-line tool that analyzes text files and generates a summary report of word frequency and sentiment.",
]

STAGE_ORDER = (
    "research",
    "mechanical",
    "electrical",
    "firmware",
    "simulation",
    "business",
    "challenge",
    "quality_gate",
)


def _slugify(text: str) -> str:
    """WHAT: Short, stable kebab-case id for a demo prompt.

    HOW: First 5 significant words, lowercased, non-alphanumerics
    stripped — matches §11.3's naming convention example.
    """
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(words[:5])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _start_server(live: bool) -> tuple[subprocess.Popen[bytes], str]:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
    if not live:
        env["ENGINEERING_STUDIO_FAKE_PIPELINE"] = "1"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "engineering_studio.webapp:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        cwd=REPO_ROOT,
    )
    deadline = time.time() + 15.0
    while time.time() < deadline:
        try:
            if requests.get(f"{base_url}/api/health", timeout=0.5).status_code == 200:
                return process, base_url
        except requests.RequestException:
            pass
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError("demo server did not become healthy in time")


def _record_one(page, theme: str, prompt: str, screenshots_dir: Path) -> None:
    slug = _slugify(prompt)
    theme_dir = screenshots_dir / theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    if theme == "light":
        page.click("#theme-toggle")
        page.wait_for_function(
            "document.documentElement.dataset.theme === 'light'"
        )

    page.screenshot(path=str(theme_dir / f"{slug}_empty.png"))

    page.fill("#brief-input", prompt)
    page.click("#launch-button")
    page.wait_for_selector("#stage-grid", state="visible", timeout=5_000)

    for stage_id in STAGE_ORDER:
        selector = f'.stage-card[data-stage="{stage_id}"] .stage-card__status'
        page.wait_for_selector(f'{selector}[data-state="done"]', timeout=15_000)
        page.screenshot(path=str(theme_dir / f"{slug}_{stage_id}.png"))

    page.wait_for_selector("#gate-banner", state="visible", timeout=5_000)
    page.screenshot(path=str(theme_dir / f"{slug}_final.png"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real Fireworks pipeline (Mode A) instead of the default mocked Mode B.",
    )
    args = parser.parse_args()
    themes = ["light", "dark"] if args.theme == "both" else [args.theme]

    process, base_url = _start_server(live=args.live)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for theme in themes:
                video_dir = RECORDINGS_ROOT / "video" / theme
                video_dir.mkdir(parents=True, exist_ok=True)
                for prompt in DEMO_PROMPTS:
                    context = browser.new_context(
                        record_video_dir=str(video_dir),
                        record_video_size={"width": 1366, "height": 768},
                        viewport={"width": 1366, "height": 768},
                    )
                    page = context.new_page()
                    page.goto(base_url)
                    _record_one(
                        page, theme, prompt, RECORDINGS_ROOT / "screenshots"
                    )
                    page.close()
                    context.close()  # flushes the .webm video file
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    print(f"Recordings saved under {RECORDINGS_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
