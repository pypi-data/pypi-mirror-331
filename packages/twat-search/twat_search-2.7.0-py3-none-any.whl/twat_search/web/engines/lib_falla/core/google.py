# this_file: src/twat_search/web/engines/lib_falla/core/google.py
"""
Google search engine implementation for the Falla search engine scraper.

This module provides the Google search engine implementation for the Falla search engine.
"""

import logging
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from twat_search.web.engines.lib_falla.core.falla import Falla

if TYPE_CHECKING:
    from collections.abc import Mapping

# Set up logger
logger = logging.getLogger(__name__)


class Google(Falla):
    """Google search engine implementation for Falla."""

    def __init__(self) -> None:
        """Initialize the Google search engine."""
        super().__init__(name="Google")
        self.use_method = "playwright"
        # Use the more reliable and general container selector from falla_search.py
        self.container_element = ("div", {"class": "g"})
        # Selector to wait for to indicate results have loaded
        self.wait_for_selector = "body"
        # Increase retries and timeout for Google
        self.max_retries = 5

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        base_url = "https://www.google.com/search"
        params = {
            "q": query,
            "num": "100",
            "hl": "en",
            "gl": "us",
        }
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"

    def get_title(self, elm: Tag) -> str:
        """
        Extract the title from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Title string
        """
        title_elem = elm.find("h3")
        if title_elem and isinstance(title_elem, Tag):
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
        link_elem = elm.find("a")
        if link_elem and isinstance(link_elem, Tag) and "href" in link_elem.attrs:
            href = cast(str, link_elem.attrs["href"])
            # Google prepends URLs with "/url?q=" and adds tracking parameters
            if href.startswith("/url?"):
                href = href.split("&")[0].replace("/url?q=", "")
                return urllib.parse.unquote(href)
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
        # Try various snippet element selectors that Google might use
        snippet_elem = elm.find("div", {"class": "VwiC3b"})
        if not snippet_elem or not isinstance(snippet_elem, Tag):
            snippet_elem = elm.find("span", {"class": "aCOpRe"})
        if not snippet_elem or not isinstance(snippet_elem, Tag):
            snippet_elem = elm.find("div", {"class": "BNeawe s3v9rd AP7Wnd"})
        if not snippet_elem or not isinstance(snippet_elem, Tag):
            # Try to find any text container that might hold a snippet
            text_containers = elm.find_all(["div", "span", "p"], class_=True)
            for container in text_containers:
                if (
                    isinstance(container, Tag)
                    and container.get_text().strip()
                    and hasattr(container, "name")
                    and container.name != "h3"
                ):
                    snippet_elem = container
                    break

        if snippet_elem and isinstance(snippet_elem, Tag):
            return snippet_elem.get_text().strip()
        return ""

    def get_each_elements(self, elements: ResultSet) -> list[dict[str, str]]:
        """
        Process a list of BeautifulSoup elements into search results.

        Args:
            elements: List of BeautifulSoup elements

        Returns:
            List of dictionaries containing search results
        """
        elements_list: list[dict[str, str]] = []

        for elm in elements:
            if not isinstance(elm, Tag):
                continue

            try:
                title = self.get_title(elm)
                link = self.get_link(elm)
                snippet = self.get_snippet(elm)

                # Only add if we have at least a title or link
                if title or link:
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

    async def search_async(self, query: str, pages: str = "") -> list[dict[str, str]]:
        """
        Search for a query and return results asynchronously.
        Override to add debugging.

        Args:
            query: Search query
            pages: Optional pagination parameter

        Returns:
            List of dictionaries containing search results
        """
        try:
            url = self.get_url(query)
            if pages:
                url += f"&{pages}"

            logger.info(f"Starting Google search for: {query}")
            logger.info(f"URL: {url}")

            # Get the raw HTML content
            await self._initialize_browser()
            if not self.browser_context:
                logger.error("Browser context not initialized")
                return []

            page = await self.browser_context.new_page()

            try:
                # Set timeout for navigation to prevent hanging
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")

                logger.info("Page loaded, waiting for selector...")
                # Wait for selector
                try:
                    if self.wait_for_selector:
                        await page.wait_for_selector(self.wait_for_selector, timeout=10000)
                        logger.info(f"Selector '{self.wait_for_selector}' found")
                except Exception as e:
                    logger.warning(f"Timeout waiting for selector: {e}")

                # Check for CAPTCHA
                try:
                    captcha_selector = 'form[action*="sorry/index"]'
                    captcha_exists = await page.evaluate(f"""() => {{
                        return !!document.querySelector('{captcha_selector}');
                    }}""")

                    if captcha_exists:
                        logger.warning("CAPTCHA detected on Google search page")
                        # Take a screenshot for debugging
                        await page.screenshot(path="google_captcha.png")
                        return []
                except Exception as e:
                    logger.error(f"Error checking for CAPTCHA: {e}")

                # Get the page content
                html_content = await page.content()
                logger.info(f"Retrieved HTML content, length: {len(html_content)}")

                # Save to file for debugging
                debug_file = f"google_debug_{query.replace(' ', '_')}.html"
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Wrote HTML content to {Path(debug_file).resolve()}")

                # Look for specific elements to debug selector issues
                result_count = await page.evaluate("""() => {
                    const results = document.querySelectorAll('div.g');
                    return results.length;
                }""")
                logger.info(f"JavaScript found {result_count} results with 'div.g' selector")

                # Try alternate selectors
                alt_selectors = [
                    "div.Gx5Zad",
                    "div.tF2Cxc",
                    "div[jscontroller='SC7lYd']",
                    "div.yuRUbf",
                    "div.eKjLze",
                    "h3",
                    "a[href]",
                ]

                for selector in alt_selectors:
                    try:
                        count = await page.evaluate(f"""() => {{
                            const elements = document.querySelectorAll('{selector}');
                            return elements.length;
                        }}""")
                        logger.info(f"Found {count} elements with selector: {selector}")
                    except Exception as e:
                        logger.error(f"Error evaluating selector {selector}: {e}")
            finally:
                await page.close()

            # Continue with the normal search process
            results = await self.fetch_async(url)
            logger.info(f"Got {len(results)} results from fetch_async")

            if not results:
                logger.warning("No results found with standard method, trying alternate parsing")

                # Parse the saved HTML file
                if Path(debug_file).exists():
                    with open(debug_file, encoding="utf-8") as f:
                        html_content = f.read()

                    soup = BeautifulSoup(html_content, "html.parser")

                    # Try various selectors
                    alt_container_selectors: list[tuple[str, Mapping[str, Any]]] = [
                        ("div", {"class": "g"}),
                        ("div", {"class": "Gx5Zad"}),
                        ("div", {"class": "tF2Cxc"}),
                        ("div", {"jscontroller": "SC7lYd"}),
                        ("div", {"class": "yuRUbf"}),
                        ("div", {"class": "eKjLze"}),
                    ]

                    for selector_type, selector_attrs in alt_container_selectors:
                        logger.info(f"Trying alternate selector: {selector_type}.{selector_attrs}")
                        elements = soup.find_all(selector_type, attrs=selector_attrs)
                        logger.info(f"Found {len(elements)} elements")

                        if elements:
                            self.container_element = (selector_type, selector_attrs)
                            logger.info(f"Using alternate container: {self.container_element}")
                            # Try to extract results with this selector
                            manual_results = []
                            for elem in elements[:10]:
                                if not isinstance(elem, Tag):
                                    continue

                                title = self.get_title(elem) or ""
                                link = self.get_link(elem) or ""
                                snippet = self.get_snippet(elem) or ""

                                if title or link:  # Only add if we have at least a title or link
                                    logger.info(f"Found result: {title} - {link}")
                                    manual_results.append(
                                        {
                                            "title": title,
                                            "link": link,
                                            "snippet": snippet,
                                        },
                                    )

                            if manual_results:
                                logger.info(f"Found {len(manual_results)} results with alternate parsing")
                                return manual_results

            return results
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []

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


# g = Google()
# print(g.search("un avion"))
