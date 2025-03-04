#!/usr/bin/env python3
import asyncio
import logging

from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_page(url):
    """Fetch a page using Playwright."""
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

            # Wait for body to be available
            await page.wait_for_selector("body", timeout=5000)

            # Get the page content
            content = await page.content()
            logger.info(f"Got content length: {len(content)}")

            return content
        finally:
            await browser.close()


def fetch_page_sync(url):
    """Synchronous wrapper for fetch_page."""
    try:
        return asyncio.run(fetch_page(url))
    except Exception as e:
        logger.error(f"Error in fetch_page_sync: {e}")
        return None


if __name__ == "__main__":
    # Test with Google
    content = fetch_page_sync("https://www.google.com/search?q=FontLab")
    if content:
        pass
    else:
        pass

    # Test with DuckDuckGo
    content = fetch_page_sync("https://html.duckduckgo.com/html/?q=FontLab")
    if content:
        pass
    else:
        pass
