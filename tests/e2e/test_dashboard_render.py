"""WHAT: Static-render assertions per theme — topbar, launch panel,
empty-state message. No run submitted.
WHY: Confirms the dashboard's baseline chrome renders correctly under
both Light Mode and Dark Mode before any pipeline activity starts
(docs/PLAYWRIGHT_INTEGRATION_PLAN.md §11.2 step 3).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect


def _set_theme(page: Page, theme: str) -> None:
    if theme == "light" and page.get_attribute("html", "data-theme") != "light":
        page.click("#theme-toggle")
        expect(page.locator("html")).to_have_attribute("data-theme", "light")


def test_dashboard_renders_topbar_and_launch_panel(live_server: str, page: Page, theme: str) -> None:
    page.goto(live_server)
    _set_theme(page, theme)

    expect(page.locator("h1")).to_have_text("Engineering Studio AI")
    expect(page.locator("#brief-input")).to_be_visible()
    expect(page.locator("#launch-button")).to_have_text("Launch Run")


def test_dashboard_empty_state_before_any_run(live_server: str, page: Page, theme: str) -> None:
    page.goto(live_server)
    _set_theme(page, theme)

    expect(page.locator("#pipeline-empty")).to_be_visible()
    expect(page.locator("#stage-grid")).to_be_hidden()
    expect(page.locator("#run-history .run-history__empty")).to_have_text("No runs yet.")


def test_backend_health_indicator_reports_online(live_server: str, page: Page, theme: str) -> None:
    page.goto(live_server)
    _set_theme(page, theme)

    expect(page.locator("#server-status")).to_have_attribute("data-state", "ok")
    expect(page.locator("#server-status-text")).to_have_text("Backend online")
