#!/usr/bin/env python3
"""
Simple POE.ninja builds scraper using Playwright.
Start basic - just navigate to a league's builds page.
"""

from playwright.sync_api import sync_playwright
import sys


def load_builds_page(league: str, headless: bool = False):
    """
    Load the builds page for a given league.

    Args:
        league: League identifier (e.g., "mercenarieshcssf", "keepershcssf")
        headless: Run browser in headless mode (default: False for debugging)

    Returns:
        Page object (for now, just to verify it loaded)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        url = f"https://poe.ninja/builds/{league}"
        print(f"Loading: {url}")

        # Navigate and wait for page to load
        # Use domcontentloaded instead of networkidle (more reliable)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Give the page a moment for JS to render
        page.wait_for_timeout(2000)

        # Basic verification - check title
        title = page.title()
        print(f"Page title: {title}")

        # Check if we got the right page
        if "poe.ninja" in title.lower():
            print("✓ Successfully loaded POE.ninja")
        else:
            print("✗ Unexpected page")

        # Keep browser open for inspection (when not headless)
        if not headless:
            print("\nBrowser open - press Enter to close...")
            input()

        browser.close()
        return True


if __name__ == "__main__":
    # Parse arguments
    headless = "--headless" in sys.argv

    # Get league name (skip --headless if present)
    league_args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    league = league_args[0] if league_args else "mercenarieshcssf"

    print("POE.ninja Builds Scraper")
    print("="*60)
    print(f"League: {league}")
    print(f"Headless: {headless}")
    print("="*60 + "\n")

    load_builds_page(league, headless)
