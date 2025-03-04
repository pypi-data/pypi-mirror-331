#!/usr/bin/env python3
"""
Standalone script to test Falla search functionality.
"""

import argparse
import asyncio
import logging
import sys

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class SimpleFallaSearch:
    """A simplified version of the Falla search engine."""

    def __init__(self, engine: str = "google"):
        """Initialize the search engine.

        Args:
            engine: The search engine to use (google, duckduckgo, bing, yahoo, qwant)
        """
        self.engine = engine
        self.selectors = {
            "google": {
                "container": "div.tF2Cxc",
                "title": "h3",
                "link": "a",
                "snippet": "div.VwiC3b",
                "wait_for": "body",
            },
            "duckduckgo": {
                "container": "div.result__body",
                "title": "h2.result__title",
                "link": "a.result__a",
                "snippet": "div.result__snippet",
                "wait_for": "body",
            },
            "bing": {
                "container": "li.b_algo",
                "title": "h2",
                "link": "a",
                "snippet": "div.b_caption p",
                "wait_for": "body",
            },
            "yahoo": {
                "container": "div.dd.algo.algo-sr",
                "title": "h3.title",
                "link": "a.d-ib",
                "snippet": "div.compText.aAbs",
                "wait_for": "#results",
            },
            "qwant": {
                "container": "article.webResult",
                "title": "a.title",
                "link": "a.title",
                "snippet": "p.description",
                "wait_for": ".webResults",
            },
        }

    def get_url(self, query: str) -> str:
        """Get the search URL for the given query.

        Args:
            query: The search query

        Returns:
            The search URL
        """
        query = query.replace(" ", "+")
        if self.engine == "google":
            return f"https://www.google.com/search?q={query}"
        if self.engine == "duckduckgo":
            return f"https://html.duckduckgo.com/html/?q={query}"
        if self.engine == "bing":
            return f"https://www.bing.com/search?q={query}"
        if self.engine == "yahoo":
            return f"https://search.yahoo.com/search?p={query}"
        if self.engine == "qwant":
            return f"https://www.qwant.com/?q={query}"
        error_msg = f"Unsupported engine: {self.engine}"
        raise ValueError(error_msg)

    async def fetch_page(self, url: str) -> str | None:
        """Fetch a page using Playwright.

        Args:
            url: The URL to fetch

        Returns:
            The page content or None if an error occurred
        """
        logger.info(f"Fetching {url}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    )

                    page = await context.new_page()
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")

                    # Wait for the selector if specified
                    selector = self.selectors[self.engine]["wait_for"]
                    if selector:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                        except Exception as e:
                            logger.warning(f"Timeout waiting for selector: {e}")

                    # Get the page content
                    content = await page.content()
                    logger.info(f"Got content length: {len(content)}")

                    # Print the first 500 characters of the content for debugging
                    logger.info(f"Content preview: {content[:500]}")

                    return content
                finally:
                    await browser.close()
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return None

    def parse_results(self, html: str) -> list[dict[str, str]]:
        """Parse search results from HTML.

        Args:
            html: The HTML content

        Returns:
            A list of search results
        """
        results: list[dict[str, str]] = []
        soup = BeautifulSoup(html, "html.parser")

        # Get the container selector
        container_selector = self.selectors[self.engine]["container"]

        # Find all result containers
        containers = soup.select(container_selector)
        logger.info(f"Found {len(containers)} result containers")

        for container in containers:
            try:
                # Get the title
                title_elem = container.select_one(self.selectors[self.engine]["title"])
                title = title_elem.get_text().strip() if title_elem else ""

                # Get the link
                link_elem = container.select_one(self.selectors[self.engine]["link"])
                link = str(link_elem.get("href")) if link_elem and link_elem.get("href") else ""

                # Get the snippet
                snippet_elem = container.select_one(self.selectors[self.engine]["snippet"])
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                # Only add results with a link
                if link:
                    results.append({"title": title, "link": link, "snippet": snippet})
            except Exception as e:
                logger.error(f"Error parsing result: {e}")
                continue

        return results

    async def search(self, query: str) -> list[dict[str, str]]:
        """Search for the given query.

        Args:
            query: The search query

        Returns:
            A list of search results
        """
        url = self.get_url(query)
        html = await self.fetch_page(url)

        if not html:
            logger.warning("No HTML content returned")
            return []

        return self.parse_results(html)

    def search_sync(self, query: str) -> list[dict[str, str]]:
        """Synchronous version of search.

        Args:
            query: The search query

        Returns:
            A list of search results
        """
        return asyncio.run(self.search(query))


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(description="Search using Falla")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--engine",
        "-e",
        choices=["google", "duckduckgo", "bing", "yahoo", "qwant"],
        default="google",
        help="Search engine to use",
    )
    args = parser.parse_args()

    search = SimpleFallaSearch(engine=args.engine)
    results = await search.search(args.query)

    if results:
        for _i, _result in enumerate(results, 1):
            pass
    else:
        pass


def main():
    """Main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
