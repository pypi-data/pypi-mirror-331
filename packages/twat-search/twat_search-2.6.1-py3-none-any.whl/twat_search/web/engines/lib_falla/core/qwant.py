# Falla-Qwant
# Sanix-darker

import asyncio
import logging
import urllib.parse

from bs4.element import Tag

from twat_search.web.engines.lib_falla.core.falla import Falla

logger = logging.getLogger(__name__)


class Qwant(Falla):
    """Qwant search engine implementation for Falla."""

    def __init__(self) -> None:
        """Initialize the Qwant search engine."""
        super().__init__(name="Qwant")
        self.use_method = "playwright"
        # Updated selectors for Qwant search results
        self.container_element = ("div", {"class": "result--web"})
        self.wait_for_selector = ".results-column"
        # Increase timeout for Qwant which can be slow to load
        self.max_retries = 5

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        params = {
            "q": query,
            "t": "web",
            "l": "en",
        }
        query_string = urllib.parse.urlencode(params)
        return f"https://www.qwant.com/?{query_string}"

    async def _fetch_page(self, url: str) -> str:
        """
        Override _fetch_page to handle Qwant consent page.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        page = None
        try:
            await self._initialize_browser()
            if not self.browser_context:
                logger.error("Browser context not initialized")
                return ""

            page = await self.browser_context.new_page()

            # Set timeout for navigation to prevent hanging
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")

            # Check for and handle consent page
            try:
                # Look for the consent button on Qwant
                consent_button = page.locator('button:has-text("Accept all")')
                if await consent_button.count() > 0:
                    logger.info("Consent page detected, clicking 'Accept all'")
                    await consent_button.click()
                    # Wait for navigation after consent
                    await page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.debug(f"No consent page or error handling consent: {e}")

            # Wait for results to load
            try:
                if self.wait_for_selector:
                    logger.info(f"Waiting for selector: {self.wait_for_selector}")
                    await page.wait_for_selector(self.wait_for_selector, timeout=5000)
                else:
                    await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"Timeout waiting for selector in {self.name}: {e}")

            # Get the page content
            return await page.content()
        except Exception as e:
            logger.error(f"Error fetching page with Playwright: {e}")
            self.current_retry += 1
            if self.current_retry < self.max_retries:
                # Wait before retrying
                await asyncio.sleep(2)
                return await self._fetch_page(url)
            return ""
        finally:
            if page:
                await page.close()

    def get_title(self, elm: Tag) -> str:
        """
        Extract the title from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Title string
        """
        # Updated selector for title
        title_elem = elm.select_one(".result__title")
        if title_elem:
            return title_elem.get_text().strip()

        # Fallback to other possible selectors
        title_elem = elm.select_one("a.url")
        if title_elem:
            return title_elem.get_text().strip()

        # Try generic h3 selector
        title_elem = elm.select_one("h3")
        if title_elem:
            return title_elem.get_text().strip()

        return ""

    def get_link(self, elm: Tag) -> str:
        """
        Extract the link from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Link URL string
        """
        # Updated selector for link
        link_elem = elm.select_one(".result__url")
        if link_elem and "href" in link_elem.attrs:
            return str(link_elem.attrs["href"])

        # Fallback to other possible selectors
        link_elem = elm.select_one("a.url")
        if link_elem and "href" in link_elem.attrs:
            return str(link_elem.attrs["href"])

        # Try any anchor with href
        link_elem = elm.select_one("a[href]")
        if link_elem and "href" in link_elem.attrs:
            return str(link_elem.attrs["href"])

        return ""

    def get_snippet(self, elm: Tag) -> str:
        """
        Extract the snippet from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Snippet text string
        """
        # Updated selector for snippet
        snippet_elem = elm.select_one(".result__desc")
        if snippet_elem:
            return snippet_elem.get_text().strip()

        # Fallback to other possible selectors
        snippet_elem = elm.select_one(".result__snippet")
        if snippet_elem:
            return snippet_elem.get_text().strip()

        # Try generic paragraph
        snippet_elem = elm.select_one("p")
        if snippet_elem:
            return snippet_elem.get_text().strip()

        return ""

    def search(self, query: str, pages: str = "") -> list[dict[str, str]]:
        """
        Search for a query and return results.

        Args:
            query: Search query
            pages: Optional pagination parameter

        Returns:
            List of dictionaries containing search results
        """
        url = self.get_url(query)
        if pages:
            url += f"&{pages}"
        return self.fetch(url)


# qw = Qwant()
# print(qw.search("un avion"))
