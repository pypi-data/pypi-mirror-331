# Falla-DuckDuckGo
# Sanix-darker

import asyncio
import logging
import urllib.parse

from bs4.element import Tag

from twat_search.web.engines.lib_falla.core.falla import Falla

logger = logging.getLogger(__name__)


class DuckDuckGo(Falla):
    """DuckDuckGo search engine implementation for Falla."""

    def __init__(self) -> None:
        """Initialize the DuckDuckGo search engine."""
        super().__init__(name="DuckDuckGo")
        self.use_method = "playwright"
        # Use the HTML version of DuckDuckGo which is more reliable for scraping
        self.container_element = ("div", {"class": "result"})
        self.wait_for_selector = ".results"
        # Increase timeout for DuckDuckGo which can be slow to load
        self.max_retries = 5

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        # Use the HTML version of DuckDuckGo which is more reliable for scraping
        base_url = "https://html.duckduckgo.com/html/"
        params = {
            "q": query,
            "kl": "us-en",  # Region and language
        }
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"

    async def _fetch_page(self, url: str) -> str:
        """
        Override _fetch_page to handle DuckDuckGo challenges.

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

            # Check for and handle CAPTCHA or challenge page
            try:
                # Look for common challenge indicators
                challenge_selectors = [
                    'form[action*="challenge"]',
                    'input[name="g-recaptcha-response"]',
                    ".challenge-form",
                    'div[class*="captcha"]',
                ]

                for selector in challenge_selectors:
                    challenge_exists = await page.evaluate(f"""() => {{
                        return !!document.querySelector('{selector}');
                    }}""")

                    if challenge_exists:
                        logger.warning(f"Challenge detected on DuckDuckGo using selector: {selector}")
                        # Take a screenshot for debugging
                        await page.screenshot(path="duckduckgo_challenge.png")
                        # Try to save the HTML content for analysis
                        html_content = await page.content()
                        with open("duckduckgo_challenge.html", "w", encoding="utf-8") as f:
                            f.write(html_content)
                        logger.info("Saved challenge page content for debugging")
                        break
            except Exception as e:
                logger.debug(f"Error checking for challenges: {e}")

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
        # HTML version of DuckDuckGo uses this class for titles
        title_elem = elm.select_one(".result__title")
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
        # HTML version of DuckDuckGo uses this class for links
        link_elem = elm.select_one(".result__a")
        if link_elem and "href" in link_elem.attrs:
            href = str(link_elem.attrs["href"])
            # The HTML version of DuckDuckGo uses relative URLs
            if href.startswith("/"):
                return f"https://duckduckgo.com{href}"
            return href
        return ""

    def get_snippet(self, elm: Tag) -> str:
        """
        Extract the snippet from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Snippet text string
        """
        # HTML version of DuckDuckGo uses this class for snippets
        snippet_elem = elm.select_one(".result__snippet")
        if snippet_elem:
            return snippet_elem.get_text().strip()
        return ""

    def get_each_elements(self, elements: list) -> list[dict[str, str]]:
        """
        Custom implementation to filter out elements that don't have valid links.

        Args:
            elements: List of BeautifulSoup elements

        Returns:
            List of dictionaries containing search results
        """
        elements_list: list[dict[str, str]] = []

        for elm in elements:
            try:
                # Only process if it has a valid link
                link = self.get_link(elm)
                if link:
                    title = self.get_title(elm) or ""
                    snippet = self.get_snippet(elm) or ""

                    elements_list.append(
                        {
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                        },
                    )
            except Exception as e:
                logger.debug(f"Error processing element: {e}")
                continue

        return elements_list


# d = DuckDuckGo()
# print(d.search("un avion"))
