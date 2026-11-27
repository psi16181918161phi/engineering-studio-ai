"""WHAT: Shared Playwright end-to-end fixtures — a live, real `uvicorn`
subprocess (Mode B, mocked pipeline) plus a `theme` fixture parametrized
across Light/Dark Mode.
WHY: Per `docs/PLAYWRIGHT_INTEGRATION_PLAN.md` §3.2/§12.1 — a real ASGI
process is what actually exercises the SSE wire contract and browser
rendering, but it must never depend on a Fireworks API key or network
access in CI. `ENGINEERING_STUDIO_FAKE_PIPELINE=1` (see `runs.py`) swaps
in the deterministic `engineering_studio.testing.fake_pipeline` for the
subprocess's whole lifetime.
HOW: `live_server` gives each test a loopback server and its own temporary
working directory, polls `/api/health` until ready, and reaps the server
after the test. `browser`/`page` are the
standard sync-API Playwright fixtures (no `pytest-playwright` plugin
dependency — built directly on `playwright.sync_api` to keep the `e2e`
optional-dependency group to a single package). `theme` is parametrized
`["light", "dark"]` so every test using it runs once per theme
automatically, per the plan's modularized test-file table.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

_SOURCE = Path(__file__).resolve().parents[2] / "src"
_SERVER = """
from pathlib import Path
import socket
import uvicorn

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind(("127.0.0.1", 0))
    pending = Path("port.tmp")
    pending.write_text(str(listener.getsockname()[1]), encoding="ascii")
    pending.replace("port")
    config = uvicorn.Config("engineering_studio.webapp:app", host="127.0.0.1")
    uvicorn.Server(config).run(sockets=[listener])
"""


@pytest.fixture
def live_server(tmp_path: Path) -> Iterator[str]:
    """WHAT: Serve the real dashboard with a deterministic fake pipeline.

    WHY: Persisted runs and previous tests must not contaminate browser state.
    HOW: Start Uvicorn in a fresh working directory with absolute imports,
    bounded readiness, and guaranteed process cleanup.

    YIELDS:
        str: The server's base URL, e.g. "http://127.0.0.1:54231".
    """
    port_file = tmp_path / "port"
    env = dict(os.environ)
    env["ENGINEERING_STUDIO_FAKE_PIPELINE"] = "1"
    env["PYTHON_DOTENV_DISABLED"] = "1"
    env["PYTHONPATH"] = str(_SOURCE)
    process = subprocess.Popen(
        [sys.executable, "-c", _SERVER],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 15.0
        base_url: str | None = None
        with requests.Session() as session:
            session.trust_env = False
            while process.poll() is None and time.monotonic() < deadline:
                if port_file.is_file():
                    origin = f"http://127.0.0.1:{port_file.read_text(encoding='ascii')}"
                    try:
                        if session.get(f"{origin}/api/health", timeout=0.5).status_code == 200:
                            base_url = origin
                            break
                    except requests.RequestException:
                        pass
                time.sleep(0.2)
        if base_url is None:
            raise RuntimeError("live_server did not become healthy in time")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """WHAT: One headless Chromium instance shared across the whole e2e
    session.

    WHY: New contexts isolate browser state without restarting the engine.
    HOW: Use bundled Chromium by default, or a locally installed channel
    when STUDIO_E2E_BROWSER_CHANNEL is provided.
    """
    with sync_playwright() as playwright:
        channel = os.environ.get("STUDIO_E2E_BROWSER_CHANNEL") or None
        instance = playwright.chromium.launch(headless=True, channel=channel)
        try:
            yield instance
        finally:
            instance.close()


@pytest.fixture
def context(browser: Browser, live_server: str) -> Iterator[BrowserContext]:
    """WHAT: A fresh, isolated browser context (cookies/localStorage) per
    test, so one test's Light/Dark toggle choice never leaks into
    another's."""

    def local_only(route: Route) -> None:
        """WHAT: Allow the test origin. WHY: Browser CI must stay offline.

        HOW: Restrict page requests to this test's loopback server.
        """
        if route.request.url.startswith(f"{live_server}/"):
            route.continue_()
        else:
            route.abort()

    ctx = browser.new_context(service_workers="block")
    try:
        ctx.route("**/*", local_only)
        yield ctx
    finally:
        ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Iterator[Page]:
    """WHAT: Provide a fresh page. WHY: Avoid navigation leaks.

    HOW: Close the page in the fixture's teardown even on test failure.
    """
    p = context.new_page()
    try:
        yield p
    finally:
        p.close()


@pytest.fixture(params=["light", "dark"])
def theme(request: pytest.FixtureRequest) -> str:
    """WHAT: Parametrizes a test across both supported dashboard themes."""
    return request.param
