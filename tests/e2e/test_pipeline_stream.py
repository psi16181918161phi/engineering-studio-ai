"""WHAT: Full run-submission + SSE stage-transition + artifact-download
assertions, parametrized by theme and by each confirmed demo prompt
(docs/PLAYWRIGHT_INTEGRATION_PLAN.md §7, §11.2).
WHY: The single highest-value e2e test — proves the entire live-server
wire contract (POST /api/runs -> SSE stream -> stage cards -> "View
output" -> download links) works end-to-end in a real browser, against
the CI-safe deterministic Mode-B pipeline (never real model calls).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

# WHAT: The 3 confirmed demo prompts (docs/PLAYWRIGHT_INTEGRATION_PLAN.md
# §7 "Software-first set (preferred for the live demo)").
DEMO_PROMPTS = [
    "Create a Python script that automates the backup of important files to a cloud storage service.",
    "Develop a simple web application that allows users to track their daily habits and visualize their progress over time.",
    "Write a command-line tool that analyzes text files and generates a summary report of word frequency and sentiment.",
]

_STAGE_ORDER = (
    "research",
    "mechanical",
    "electrical",
    "firmware",
    "simulation",
    "business",
    "challenge",
    "quality_gate",
)


@pytest.mark.parametrize("prompt", DEMO_PROMPTS)
def test_full_pipeline_run_reaches_quality_gate(
    live_server: str, page: Page, theme: str, prompt: str
) -> None:
    page.goto(live_server)
    if theme == "light":
        page.click("#theme-toggle")

    page.fill("#brief-input", prompt)
    page.click("#launch-button")

    expect(page.locator("#stage-grid")).to_be_visible(timeout=5_000)

    for stage_id in _STAGE_ORDER:
        card = page.locator(f'.stage-card[data-stage="{stage_id}"] .stage-card__status')
        expect(card).to_have_attribute("data-state", "done", timeout=10_000)

    expect(page.locator("#gate-banner")).to_be_visible()
    expect(page.locator("#run-meta-status")).to_have_attribute("data-state", "done")


def test_stage_output_and_download_links_become_available(
    live_server: str, page: Page
) -> None:
    page.goto(live_server)
    page.fill("#brief-input", DEMO_PROMPTS[0])
    page.click("#launch-button")

    research_card = page.locator('.stage-card[data-stage="research"]')
    expect(research_card.locator(".stage-card__status")).to_have_attribute(
        "data-state", "done", timeout=10_000
    )

    research_card.locator(".stage-card__toggle").click()
    expect(research_card.locator(".stage-card__output")).to_contain_text("Research")

    download_link = research_card.locator(".stage-card__download")
    expect(download_link).to_be_visible()
    href = download_link.get_attribute("href")
    assert href is not None
    assert "/artifacts/research/download" in href


def test_download_all_link_appears_once_run_completes(live_server: str, page: Page) -> None:
    page.goto(live_server)
    page.fill("#brief-input", DEMO_PROMPTS[1])
    page.click("#launch-button")

    expect(page.locator("#run-meta-status")).to_have_attribute(
        "data-state", "done", timeout=15_000
    )
    download_all = page.locator("#download-all-link")
    expect(download_all).to_be_visible()
    href = download_all.get_attribute("href")
    assert href is not None
    assert "/download" in href
