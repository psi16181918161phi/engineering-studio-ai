"""WHAT: Shared Playwright test doubles for the `tests/demo` suite.
WHY: Neither `_playwright_demo_script` nor `_professional_video_demo`
should ever launch a real browser or spawn a real uvicorn subprocess in
the mocked unit/integration test tier (100%-coverage gate) — a shared,
minimal fake of the small slice of the Playwright sync API these
packages actually use lets every test run instantly and deterministically.
HOW: `FakePage`/`FakeLocator`/`FakeContext`/`FakeBrowser`/`FakeChromium`/
`FakePlaywright` mirror just the methods `core/*.py` calls (`click`,
`fill`, `locator`, `wait_for_selector`, `wait_for_function`,
`wait_for_timeout`, `screenshot`, `evaluate`, `inner_text`, `goto`,
`close`, `new_page`, `new_context`, `launch`). `FakeVideo` fakes the
`page.video.path()` Playwright uses for recorded `.webm` files.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class FakeVideo:
    """WHAT: Fakes `Page.video` — a raw recorded video file's path."""

    def __init__(self, path_str: str | None = None) -> None:
        self._path = path_str

    def path(self) -> str | None:
        return self._path


class FakeLocator:
    """WHAT: Fakes `Page.locator(selector)`'s returned element handle."""

    def __init__(self, page: "FakePage", selector: str) -> None:
        self._page = page
        self.selector = selector

    def click(self) -> None:
        self._page.clicks.append(self.selector)

    def fill(self, value: str) -> None:
        self._page.fills.append((self.selector, value))

    def press_sequentially(self, text: str, delay: float | None = None) -> None:
        self._page.fills.append((self.selector, text))
        self._page.typed_delays.append(delay)


class FakePage:
    """WHAT: Fakes the small slice of Playwright's `Page` API used by
    `core.scenario`/`core.recorder`/`core.overlay` in both packages.
    """

    def __init__(self, gate_text: str = "PASS: All quality checks succeeded.") -> None:
        self.theme = "dark"
        self.video: FakeVideo = FakeVideo()
        self.clicks: list[str] = []
        self.fills: list[tuple[str, str]] = []
        self.typed_delays: list[float | None] = []
        self.timeouts_ms: list[int] = []
        self.evaluated: list[tuple[str, Any]] = []
        self.screenshots: list[str] = []
        self.closed = False
        self._gate_text = gate_text
        self.url: str | None = None

    def goto(self, url: str) -> None:
        self.url = url

    def click(self, selector: str) -> None:
        self.clicks.append(selector)
        if selector == "#theme-toggle":
            self.theme = "light"

    def fill(self, selector: str, value: str) -> None:
        self.fills.append((selector, value))

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(self, selector)

    def wait_for_selector(
        self, selector: str, state: str | None = None, timeout: float | None = None
    ) -> None:
        return None

    def wait_for_function(self, expression: str, timeout: float | None = None) -> None:
        return None

    def wait_for_timeout(self, timeout_ms: float) -> None:
        self.timeouts_ms.append(int(timeout_ms))

    def screenshot(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"")
        self.screenshots.append(path)

    def evaluate(self, script: str, arg: Any = None) -> Any:
        self.evaluated.append((script, arg))
        return None

    def inner_text(self, selector: str) -> str:
        return self._gate_text

    def close(self) -> None:
        self.closed = True


class FakeContext:
    """WHAT: Fakes `Browser.new_context(...)`'s returned browser context,
    including the `record_video_dir` -> raw `.webm` file simulation.
    """

    def __init__(self, record_video_dir: str | None = None, **_: Any) -> None:
        self.record_video_dir = record_video_dir
        self.pages: list[FakePage] = []
        self.closed = False

    def new_page(self) -> FakePage:
        page = FakePage()
        if self.record_video_dir:
            video_dir = Path(self.record_video_dir)
            video_dir.mkdir(parents=True, exist_ok=True)
            raw_path = video_dir / f"raw_{len(self.pages)}.webm"
            raw_path.write_bytes(b"fake-video-bytes")
            page.video = FakeVideo(str(raw_path))
        self.pages.append(page)
        return page

    def close(self) -> None:
        self.closed = True


class FakeBrowser:
    """WHAT: Fakes `chromium.launch(...)`'s returned `Browser`."""

    def __init__(self) -> None:
        self.contexts: list[FakeContext] = []
        self.closed = False

    def new_context(self, **kwargs: Any) -> FakeContext:
        context = FakeContext(**kwargs)
        self.contexts.append(context)
        return context

    def close(self) -> None:
        self.closed = True


class FakeChromium:
    """WHAT: Fakes `playwright.chromium`."""

    def __init__(self, browser: FakeBrowser) -> None:
        self._browser = browser

    def launch(self, headless: bool = True) -> FakeBrowser:
        return self._browser


class FakePlaywright:
    """WHAT: Fakes the object yielded by `with sync_playwright() as p:`."""

    def __init__(self) -> None:
        self.browser = FakeBrowser()
        self.chromium = FakeChromium(self.browser)

    def __enter__(self) -> "FakePlaywright":
        return self

    def __exit__(self, *exc_info: Any) -> bool:
        return False


def fake_sync_playwright() -> FakePlaywright:
    """WHAT: Drop-in replacement for `playwright.sync_api.sync_playwright`."""
    return FakePlaywright()


class FakeProcess:
    """WHAT: Fakes `subprocess.Popen` for a spawned demo server process."""

    def __init__(self) -> None:
        self.terminated = False
        self.killed = False

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, timeout: float | None = None) -> int:
        return 0

    def kill(self) -> None:
        self.killed = True


class FakeTimeoutProcess(FakeProcess):
    """WHAT: Fakes a process whose `.wait()` always times out, forcing the
    `util.pipeline` teardown code down its `process.kill()` fallback path.
    """

    def wait(self, timeout: float | None = None) -> int:
        raise subprocess.TimeoutExpired(cmd="uvicorn", timeout=timeout or 5)


def fake_start_server(
    process: FakeProcess | None = None,
) -> tuple[FakeProcess, str]:
    """WHAT: Drop-in replacement for `core.server.start_server`.

    RETURNS:
        tuple[FakeProcess, str]: A fake process and a fake base URL.
    """
    return process or FakeProcess(), "http://127.0.0.1:1"
