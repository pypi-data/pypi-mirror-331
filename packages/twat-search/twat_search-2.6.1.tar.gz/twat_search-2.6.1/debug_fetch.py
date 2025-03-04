#!/usr/bin/env python3
"""
Debug script to fetch and save HTML content from various search engines.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class DebugFetcher:
    """Fetches and saves HTML content from search engines for analysis."""

    def __init__(self):
        """Initialize the fetcher."""
        self.engines = {
            "yahoo": "https://search.yahoo.com/search?p={}",
            "qwant": "https://www.qwant.com/?q={}",
            "google": "https://www.google.com/search?q={}",
            "duckduckgo": "https://html.duckduckgo.com/html/?q={}",
            "bing": "https://www.bing.com/search?q={}",
        }
        self.output_dir = Path("debug_output")

    async def fetch_page(self, url: str, engine: str) -> str:
        """Fetch a page using Playwright.

        Args:
            url: The URL to fetch
            engine: The search engine being used

        Returns:
            The page content
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
                await page.goto(url, timeout=60000, wait_until="networkidle")

                # Take a screenshot for visual inspection
                await page.screenshot(path=self.output_dir / f"{engine}_screenshot.png")

                # Get the page content
                content = await page.content()
                logger.info(f"Got content length: {len(content)}")

                return content
            finally:
                await browser.close()

    def save_html(self, content: str, engine: str) -> None:
        """Save HTML content to a file.

        Args:
            content: The HTML content
            engine: The search engine name
        """
        path = self.output_dir / f"{engine}_content.html"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved HTML content to {path}")

    def analyze_selectors(self, content: str, engine: str) -> None:
        """Analyze HTML content to suggest selectors.

        Args:
            content: The HTML content
            engine: The search engine name
        """
        soup = BeautifulSoup(content, "html.parser")

        # Output potential container elements for search results
        with open(self.output_dir / f"{engine}_analysis.txt", "w", encoding="utf-8") as f:
            f.write(f"Analysis for {engine}\n")
            f.write("=" * 80 + "\n\n")

            # Common container class patterns
            potential_containers = [
                # Yahoo
                "div.dd.algo",
                "div.algo-sr",
                "div.dd.algo.algo-sr",
                # Qwant
                "article.webResult",
                "div.result",
                "div.web-result",
                # Generic
                "div.result",
                "div.search-result",
                "li.result",
            ]

            f.write("Potential containers found:\n")
            for selector in potential_containers:
                elements = soup.select(selector)
                f.write(f"{selector}: {len(elements)} elements found\n")

                # If elements are found, look for title, link, and snippet patterns
                if elements and len(elements) > 0:
                    sample = elements[0]
                    f.write(f"\nSample structure of {selector}:\n")
                    f.write(str(sample)[:500] + "...\n\n")

            # Look for other common patterns
            f.write("\nOther potential elements:\n")
            for tag in ["h1", "h2", "h3", "h4", "a.title", "p.description", ".snippet"]:
                elements = soup.select(tag)
                if elements and len(elements) > 0:
                    f.write(f"{tag}: {len(elements)} elements found\n")
                    if len(elements) < 5:  # Only show samples for a small number
                        for i, elem in enumerate(elements):
                            f.write(f"  {i + 1}. {elem.get_text().strip()[:100]}\n")

    async def process_engine(self, engine: str, query: str) -> None:
        """Process a search engine.

        Args:
            engine: The search engine to use
            query: The search query
        """
        if engine not in self.engines:
            logger.error(f"Unsupported engine: {engine}")
            return

        url = self.engines[engine].format(query.replace(" ", "+"))
        content = await self.fetch_page(url, engine)
        self.save_html(content, engine)
        self.analyze_selectors(content, engine)

    async def run(self, engines: list[str], query: str) -> None:
        """Run the fetcher for multiple engines.

        Args:
            engines: The search engines to use
            query: The search query
        """
        self.output_dir.mkdir(exist_ok=True)

        logger.info(f"Processing engines: {', '.join(engines)}")
        for engine in engines:
            await self.process_engine(engine, query)


async def main_async() -> None:
    """Main async function."""
    parser = argparse.ArgumentParser(description="Fetch search engine HTML for debugging")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--engines",
        "-e",
        nargs="+",
        choices=["google", "duckduckgo", "bing", "yahoo", "qwant", "all"],
        default=["yahoo", "qwant"],
        help="Search engines to use",
    )
    args = parser.parse_args()

    engines = args.engines
    if "all" in engines:
        engines = ["google", "duckduckgo", "bing", "yahoo", "qwant"]

    fetcher = DebugFetcher()
    await fetcher.run(engines, args.query)


def main() -> None:
    """Main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
