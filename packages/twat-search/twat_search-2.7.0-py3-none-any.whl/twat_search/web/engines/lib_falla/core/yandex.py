# Falla-Yandex
# Sanix-darker

import urllib.parse
from typing import cast

from bs4.element import Tag

from twat_search.web.engines.lib_falla.core.falla import Falla


class Yandex(Falla):
    """Yandex search engine implementation for Falla."""

    def __init__(self) -> None:
        """Initialize the Yandex search engine."""
        super().__init__(name="Yandex")
        self.use_method = "playwright"
        self.container_element = ("li", {"class": "serp-item"})
        self.wait_for_selector = "div.content__left"

    def get_url(self, query: str) -> str:
        """
        Get the search URL for a query.

        Args:
            query: Search query

        Returns:
            URL string
        """
        base_url = "https://yandex.com/search/"
        params = {
            "text": query,
            "lr": "87",  # English language results
            "lang": "en",
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
        title_elem = elm.select_one("div.organic__url-text")
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
        link_elem = elm.select_one("a.link")
        if link_elem and "href" in link_elem.attrs:
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
        snippet_elem = elm.select_one("div.text-container")
        if snippet_elem:
            return snippet_elem.get_text().strip()
        return ""


# y = Yandex()
# print(y.search("un avion"))
