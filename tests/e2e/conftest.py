"""WHAT: Shared Playwright end-to-end fixtures — a live, real `uvicorn`
subprocess (Mode B, mocked pipeline) plus a `theme` fixture parametrized
across Light/Dark Mode.
WHY: Per `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` §3.2/§12.1 — a real ASGI
process is what actually exercises the SSE wire contract and browser
rendering, but it must never depend on a Fireworks API key or network
access in CI. `ENGINEERING_STUDIO_FAKE_PIPELINE=1` (see `runs.py`) swaps
in the deterministic `engineering_studio.testing.fake_pipeline` for the
subprocess's whole lifetime.
HOW: `live_server` starts `uvicorn engineering_studio.webapp:app` bound to
an OS-assigned free port as a subprocess, polls `/api/health` until ready,
yields the base URL, then terminates it. `browser`/`page` are the
standard sync-API Playwright fixtures (no `pytest-playwright` plugin
dependency — built directly on `playwright.sync_api` to keep the `e2e`
optional-dependency group to a single package). `theme` is parametrized
`["light", "dark"]` so every test using it runs once per theme
automatically, per the plan's modularized test-file table.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


def _free_port() -> int:
    """WHAT: Asks the OS for an unused TCP port.

    WHY: Lets multiple e2e runs (or a run alongside a manually-started
    dev server) coexist without a fixed-port collision.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server() -> Iterator[str]:
    """WHAT: Starts the real webapp as a subprocess, Mode B (mocked
    pipeline, no live model calls, no API key required).

    YIELDS:
        str: The server's base URL, e.g. "http://127.0.0.1:54231".
    """
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
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
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 15.0
        ready = False
        while time.time() < deadline:
            try:
                if requests.get(f"{base_url}/api/health", timeout=0.5).status_code == 200:
                    ready = True
                    break
            except requests.RequestException:
                pass
            time.sleep(0.2)
        if not ready:
            raise RuntimeError("live_server did not become healthy in time")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """WHAT: One headless Chromium instance shared across the whole e2e
    session (starting a new browser per test would be needlessly slow)."""
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True)
        yield instance
        instance.close()


@pytest.fixture
def context(browser: Browser) -> Iterator[BrowserContext]:
    """WHAT: A fresh, isolated browser context (cookies/localStorage) per
    test, so one test's Light/Dark toggle choice never leaks into
    another's."""
    ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Iterator[Page]:
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture(params=["light", "dark"])
def theme(request: pytest.FixtureRequest) -> str:
    """WHAT: Parametrizes a test across both supported dashboard themes."""
    return request.param
