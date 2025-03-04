# this_file: src/twat_search/web/engines/lib_falla/core/falla.py
"""
Base Falla class for search engine scraping.

This module provides the base class for all Falla search engine scrapers.
"""

import asyncio
import logging
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, ClassVar, Optional, Union, cast

import bs4
import requests
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from twat_search.web.engines.lib_falla.settings import SPLASH_SCRAP_URL

# Set up logger
logger = logging.getLogger(__name__)


class Falla:
    """
    Base class for all Falla search engine implementations.

    This class provides common functionality for web scraping search engines,
    including methods for making requests, parsing HTML, and extracting results.
    It supports both synchronous and asynchronous operation.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a new Falla search engine instance.

        Args:
            name: The name of the search engine
        """
        self.name = name
        self.results: list[dict[str, str]] = []
        self.use_method = "requests"  # Default to requests, can be "requests", "playwright", or "splash"
        self.container_element: tuple[str, dict[str, Any]] = ("div", {})

        # Playwright-specific attributes
        self.browser: Browser | None = None
        self.browser_context: BrowserContext | None = None
        self.max_retries = 3
        self.current_retry = 0
        self.wait_for_selector: str | None = None

    async def _initialize_browser(self) -> None:
        """
        Initialize the Playwright browser if not already initialized.
        """
        if self.browser is None:
            p = await async_playwright().start()
            self.browser = await p.chromium.launch(headless=True)

        if self.browser_context is None and self.browser is not None:
            self.browser_context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )

    async def _close_browser(self) -> None:
        """
        Close the Playwright browser and context if they exist.
        """
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

    async def _fetch_page(self, url: str) -> str:
        """
        Fetch a page using Playwright.

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

            # Wait a moment for JavaScript to render content
            try:
                # If we know what to wait for (a selector), use that
                if self.wait_for_selector:
                    logger.info(f"Waiting for selector: {self.wait_for_selector}")
                    await page.wait_for_selector(self.wait_for_selector, timeout=5000)
                else:
                    # Otherwise wait a short time
                    await asyncio.sleep(2)
            except PlaywrightTimeoutError:
                # If timeout occurs when waiting for selector, continue anyway
                logger.warning(f"Timeout waiting for selector in {self.name}")

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

    def get_element_from_type(
        self,
        bs_obj: bs4.element.Tag,
        type_elem: str,
        attr_elem: dict[str, Any],
    ) -> bs4.element.Tag | None:
        """
        Get a BeautifulSoup element by type and attributes.

        Args:
            bs_obj: BeautifulSoup object
            type_elem: HTML element type (e.g., 'div', 'a')
            attr_elem: Dictionary of attributes to match

        Returns:
            BeautifulSoup element or None if not found
        """
        try:
            result = bs_obj.find(type_elem, attr_elem)
            return result if isinstance(result, bs4.element.Tag) else None
        except Exception as e:
            logger.debug(f"Error getting element: {e}")
            return None

    def get_tag(
        self,
        element: bs4.element.Tag,
        _type: str = "div",
        _attr: dict[str, Any] | None = None,
    ) -> bs4.element.Tag | None:
        """
        Get a tag from within an element.

        Args:
            element: Parent BeautifulSoup element
            _type: Type of tag to find
            _attr: Attributes to match

        Returns:
            BeautifulSoup element or None if not found
        """
        if _attr is None:
            _attr = {}
        try:
            result = element.find(_type, _attr)
            return result if isinstance(result, bs4.element.Tag) else None
        except Exception as e:
            logger.debug(f"Error getting tag: {e}")
            return None

    async def parse_entry_point_async(self, entry_point: str) -> BeautifulSoup | None:
        """
        Parse the entry point URL and return a BeautifulSoup object asynchronously.

        Args:
            entry_point: URL to parse

        Returns:
            BeautifulSoup object or None if parsing fails
        """
        try:
            if self.use_method == "playwright":
                content = await self._fetch_page(entry_point)
                return BeautifulSoup(content, "html.parser")
            if self.use_method == "splash":
                return BeautifulSoup(self.scrapy_splash_request(entry_point), "html.parser")
            # requests
            return BeautifulSoup(self.get_html_content(entry_point), "html.parser")
        except Exception as e:
            logger.error(f"Error parsing entry point: {e}")
            return None

    def parse_entry_point(self, entry_point: str) -> BeautifulSoup | None:
        """
        Parse the entry point URL and return a BeautifulSoup object.

        Args:
            entry_point: URL to parse

        Returns:
            BeautifulSoup object or None if parsing fails
        """
        try:
            if self.use_method == "playwright":
                # Check if we're already in an event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an event loop, use a coroutine directly
                    if loop.is_running():
                        # Create a new future and run the coroutine
                        content_future = asyncio.create_task(self._fetch_page_sync(entry_point))
                        # Wait for the future to complete
                        content = loop.run_until_complete(content_future)
                    else:
                        # Loop exists but not running
                        content = loop.run_until_complete(self._fetch_page_sync(entry_point))
                except RuntimeError:
                    # No event loop exists, create one
                    content = asyncio.run(self._fetch_page_sync(entry_point))

                if not content:
                    logger.warning(f"No content returned from {entry_point}")
                    return None

                return BeautifulSoup(content, "html.parser")

            if self.use_method == "splash":
                return BeautifulSoup(self.scrapy_splash_request(entry_point), "html.parser")

            # requests method
            return BeautifulSoup(self.get_html_content(entry_point), "html.parser")
        except Exception as e:
            logger.error(f"Error parsing entry point: {e}", exc_info=True)
            return None

    async def _fetch_page_sync(self, url: str) -> str:
        """
        Fetch a page using Playwright for synchronous operations.
        This is a separate method to avoid issues with nested event loops.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    )

                    page = await context.new_page()
                    # Increase timeout to 60 seconds for slow connections
                    await page.goto(url, timeout=60000, wait_until="domcontentloaded")

                    # Wait for selector if specified
                    if self.wait_for_selector:
                        try:
                            logger.info(f"Waiting for selector: {self.wait_for_selector}")
                            # Increase timeout to 10 seconds for selector
                            await page.wait_for_selector(self.wait_for_selector, timeout=10000)
                        except PlaywrightTimeoutError:
                            # If timeout occurs when waiting for selector, continue anyway
                            logger.warning(f"Timeout waiting for selector in {self.name}")
                    else:
                        # Otherwise wait a short time
                        await asyncio.sleep(2)

                    # Get the page content
                    content = await page.content()
                    logger.info(f"Got content length: {len(content)}")

                    # Log a preview of the content for debugging
                    if len(content) > 0:
                        logger.debug(f"Content preview: {content[:200]}...")
                    else:
                        logger.warning("Received empty content")

                    return content
                finally:
                    await browser.close()
        except Exception as e:
            logger.error(f"Error fetching page with Playwright: {e}")
            self.current_retry += 1
            if self.current_retry < self.max_retries:
                # Wait before retrying with exponential backoff
                wait_time = 2**self.current_retry  # 2, 4, 8, 16...
                logger.info(f"Retrying in {wait_time} seconds (attempt {self.current_retry + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._fetch_page_sync(url)
            return ""

    def get_each_elements(self, elements: bs4.element.ResultSet) -> list[dict[str, str]]:
        """
        Extract search results from a list of elements.

        Args:
            elements: List of BeautifulSoup elements

        Returns:
            List of dictionaries containing search results
        """
        elements_list: list[dict[str, str]] = []

        for elm in elements[:10]:
            try:
                title = self.get_title(elm) or ""
                link = self.get_link(elm) or ""
                snippet = self.get_snippet(elm) or ""

                if link:  # Only add results with a valid link
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

    def scrapy_splash_request(self, entry_point: str) -> str:
        """
        Use Splash to render JavaScript before scraping.

        Args:
            entry_point: URL to scrape

        Returns:
            HTML content as string
        """
        try:
            splash_url = f"{SPLASH_SCRAP_URL}/render.html?url={entry_point}&timeout=10&wait=0.5"
            return requests.get(splash_url, timeout=30).text
        except Exception as e:
            logger.error(f"Error using Splash: {e}")
            return ""

    def get_html_content(self, url: str) -> str:
        """
        Get HTML content from a URL using requests.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        try:
            # Standard HTTP request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.text
        except Exception as e:
            logger.error(f"Error getting HTML content: {e}")
            return ""

    async def fetch_async(self, entry_point: str) -> list[dict[str, str]]:
        """
        Fetch and parse search results from an entry point URL asynchronously.

        Args:
            entry_point: URL to fetch

        Returns:
            List of dictionaries containing search results
        """
        try:
            html_parser = await self.parse_entry_point_async(entry_point)
            if html_parser:
                # Use ** unpacking to handle various BeautifulSoup attribute types
                elements = html_parser.find_all(self.container_element[0], attrs=self.container_element[1])
                return self.get_each_elements(elements)
            return []
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []

    def fetch(self, entry_point: str) -> list[dict[str, str]]:
        """
        Fetch and parse search results from an entry point URL.

        Args:
            entry_point: URL to fetch

        Returns:
            List of dictionaries containing search results
        """
        try:
            html_parser = self.parse_entry_point(entry_point)
            if html_parser:
                # Use ** unpacking to handle various BeautifulSoup attribute types
                elements = html_parser.find_all(self.container_element[0], attrs=self.container_element[1])
                return self.get_each_elements(elements)
            return []
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        msg = "Subclasses must implement get_url"
        raise NotImplementedError(msg)
        return ""  # This line is never reached, added to satisfy linter

    def get_title(self, elm: bs4.element.Tag) -> str:
        """
        Extract the title from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Title string
        """
        msg = "Subclasses must implement get_title"
        raise NotImplementedError(msg)

    def get_link(self, elm: bs4.element.Tag) -> str:
        """
        Extract the link from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Link URL string
        """
        msg = "Subclasses must implement get_link"
        raise NotImplementedError(msg)

    def get_snippet(self, elm: bs4.element.Tag) -> str:
        """
        Extract the snippet from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Snippet text string
        """
        msg = "Subclasses must implement get_snippet"
        raise NotImplementedError(msg)

    def search(self, query: str, pages: str = "") -> list[dict[str, str]]:
        """
        Search for a query and return results synchronously.

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

    async def search_async(self, query: str, pages: str = "") -> list[dict[str, str]]:
        """
        Search for a query and return results asynchronously.

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

            return await self.fetch_async(url)
        finally:
            # Clean up resources
            await self._close_browser()

    async def close(self) -> None:
        """Close browser resources."""
        await self._close_browser()
