"""WHAT: Real (unmocked) Playwright + real `uvicorn` subprocess smoke
test for both `demo._playwright_demo_script` and
`demo._professional_video_demo`'s shared server/browser plumbing.
WHY: The mocked unit/integration tier (`tests/demo/unit`,
`tests/demo/integration`) proves the *logic* is correct but never
actually launches a browser or a real ASGI process — this smoke test
closes that gap by running the real `core.server.start_server()` +
a real headless Chromium page load, WITHOUT the multi-minute paced
walkthrough (that full path is exercised by `demo/_professional_video_demo`'s
own CLI, not by an automated, always-run test). It is intentionally
**not** part of the 100%-coverage gate — see the separate
`pytest tests/demo/e2e` invocation in Task 7/CI.
HOW: Skips gracefully (rather than failing the whole suite) if Chromium
is not installed locally (`playwright install chromium` was never run),
matching this repo's "live-data honesty" convention: an environment gap
is reported as a skip, never silently treated as a pass.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from demo._playwright_demo_script.core.naming import slugify
from demo._playwright_demo_script.core.server import start_server


@pytest.fixture(scope="module")
def real_chromium():  # type: ignore[no-untyped-def]
    """WHAT: Launches one real headless Chromium instance for this
    module's tests, skipping the module if it is not installed.
    """
    try:
        playwright_ctx = sync_playwright()
        playwright = playwright_ctx.__enter__()
        browser = playwright.chromium.launch(headless=True)
    except Exception as exc:  # noqa: BLE001 - environment probe, not a code bug
        pytest.skip(f"Chromium is not installed locally ({exc}); run `playwright install chromium`.")
    try:
        yield browser
    finally:
        browser.close()
        playwright_ctx.__exit__(None, None, None)


def test_real_server_and_browser_can_load_the_demo_webapp(real_chromium) -> None:  # type: ignore[no-untyped-def]
    """WHAT: End-to-end smoke check: real server boots, a real browser
    page navigates to it, and the app's own health indicator flips to
    "ok" — proving the two new packages' shared `core.server` plumbing
    still works against the real webapp, not just against fakes.
    """
    process, base_url = start_server(live=False)
    try:
        context = real_chromium.new_context()
        page = context.new_page()
        page.goto(base_url)
        page.wait_for_selector('#server-status[data-state="ok"]', timeout=10_000)
        assert "Engineering Studio" in page.title()
        page.close()
        context.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:  # noqa: BLE001 - best-effort teardown
            process.kill()


def test_slugify_is_stable_against_a_real_confirmed_prompt() -> None:
    """WHAT: Sanity-checks `slugify()` (shared by both packages) against
    one of the real confirmed demo prompts, end-to-end with no mocking.
    """
    slug = slugify(
        "Create a Python script that automates the backup of important "
        "files to a cloud storage service."
    )
    assert slug == "create-a-python-script-that"
