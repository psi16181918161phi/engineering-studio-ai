"""WHAT: Theme-toggle behavior tests — default state, click-to-switch,
`localStorage` persistence across a reload. No pipeline run involved.
WHY: Isolates the Light/Dark toggle contract (docs/TEAM_QA.md §4) from
pipeline-streaming concerns, per the plan's modularized test-file table
(docs/PLAYWRIGHT_INTEGRATION_PLAN.md §12.1).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect


def test_dark_mode_is_the_default(live_server: str, page: Page) -> None:
    page.goto(live_server)
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    expect(page.locator("#theme-toggle-text")).to_have_text("Dark mode")


def test_toggle_switches_to_light_and_back(live_server: str, page: Page) -> None:
    page.goto(live_server)
    page.click("#theme-toggle")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
    expect(page.locator("#theme-toggle-text")).to_have_text("Light mode")

    page.click("#theme-toggle")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_theme_choice_persists_across_reload(live_server: str, page: Page) -> None:
    page.goto(live_server)
    page.click("#theme-toggle")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")

    page.reload()
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
