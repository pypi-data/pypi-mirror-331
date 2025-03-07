# this_file: src/twat_search/web/engines/lib_falla/core/bing.py
"""
Bing search engine implementation for the Falla search engine scraper.

This module provides the Bing search engine implementation for the Falla search engine.
"""

import urllib.parse
from typing import cast

from bs4.element import Tag

from twat_search.web.engines.lib_falla.core.falla import Falla


class Bing(Falla):
    """Bing search engine implementation for Falla."""

    def __init__(self) -> None:
        """Initialize the Bing search engine."""
        super().__init__(name="Bing")
        self.use_method = "playwright"
        self.container_element = ("li", {"class": "b_algo"})
        self.wait_for_selector = "body"
        self.max_retries = 5

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        base_url = "https://www.bing.com/search"
        params = {
            "q": query,
            "count": "50",
            "setlang": "en",
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
        title_elem = elm.find("h2")
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
        link_elem = elm.find("a")
        if link_elem and isinstance(link_elem, Tag) and "href" in link_elem.attrs:
            return cast(str, link_elem.attrs["href"])
        return ""

    def get_snippet(self, elm: Tag) -> str:
        """
        Extract the snippet from a search result element.

        Args:
            elm: BeautifulSoup element

        Returns:
            Snippet text string
        """
        snippet_elem = elm.find("div", {"class": "b_caption"})
        if snippet_elem and isinstance(snippet_elem, Tag):
            p_elem = snippet_elem.find("p")
            if p_elem and isinstance(p_elem, Tag):
                return p_elem.get_text().strip()
        return ""


# b = Bing()
# print(b.search("un avion"))
