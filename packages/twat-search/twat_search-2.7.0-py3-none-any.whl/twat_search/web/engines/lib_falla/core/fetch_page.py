#!/usr/bin/env python3
# this_file: src/twat_search/web/engines/lib_falla/core/fetch_page.py
"""
Standalone script to fetch a web page using Playwright.

This script is designed to be called as a subprocess from the Falla implementation
to avoid issues with asyncio.run() in the main process.
"""

import argparse
import asyncio
import logging
import sys

from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


async def fetch_page(url: str, wait_for_selector: str | None = None) -> str:
    """
    Fetch a web page using Playwright.

    Args:
        url: The URL to fetch
        wait_for_selector: Optional CSS selector to wait for

    Returns:
        The page content as a string
    """
    logger.info(f"Fetching {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )

            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")

            # Wait for selector if specified
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=5000)
                except Exception as e:
                    logger.warning(f"Timeout waiting for selector: {e}")

            # Get the page content
            content = await page.content()
            logger.info(f"Got content length: {len(content)}")

            return content
        finally:
            await browser.close()


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(description="Fetch a web page using Playwright")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--wait-for", help="CSS selector to wait for")
    args = parser.parse_args()

    await fetch_page(args.url, args.wait_for)

    # Print the content to stdout for the parent process to capture


def main():
    """Main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
