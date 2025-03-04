#!/usr/bin/env python3
# /// script
# dependencies = ["playwright", "lxml", "requests"]
# ///
# this_file: src/twat_search/web/engines/falla.py
"""
Search engine wrappers based on the Falla scraping library.

This module provides search engine implementations that use the embedded
Falla library for scraping search engine results.
"""

import logging
from typing import Any, ClassVar, cast

from pydantic import HttpUrl
from twat_cache import ucache

from twat_search.web.engines.base import SearchEngine, register_engine
from twat_search.web.engines.lib_falla.core import (
    Aol,
    Ask,
    Bing,
    DogPile,
    DuckDuckGo,
    Falla,
    Gibiru,
    Google,
    Mojeek,
    Qwant,
    Yahoo,
    Yandex,
)
from twat_search.web.exceptions import EngineError
from twat_search.web.models import SearchResult

logger = logging.getLogger(__name__)

# List of available Falla engine names
FALLA_AVAILABLE_ENGINES = [
    "google",
    "bing",
    "duckduckgo",
    "yahoo",
    "ask",
    "aol",
    "dogpile",
    "gibiru",
    "mojeek",
    "qwant",
    "yandex",
]

# Track if Falla engines are available
_falla_available = False
# Flag set to True once the first Falla-based engine is initialized
_falla_initialized = False


def is_falla_available() -> bool:
    """
    Check if Falla search engines are available.

    Returns:
        bool: True if Falla engines are available, False otherwise
    """
    global _falla_available
    if not _falla_initialized:
        # Check if Falla can be initialized without errors
        try:
            # Basic check - create and validate a Google instance
            # Google constructor doesn't take a name parameter
            _check_engine = Google()
            _falla_available = True
        except Exception as e:
            logger.warning(f"Falla engines are not available: {e}")
            _falla_available = False

    return _falla_available


@register_engine
class FallaSearchEngine(SearchEngine):
    """Base class for all Falla-based search engines."""

    # To be overridden by subclasses
    engine_code = "falla"
    friendly_engine_name = "Falla Search"
    env_api_key_names: ClassVar[list[str]] = []

    # Note: This is marked as a ClassVar for type-checking, but will be overridden
    # by subclasses with their specific engine classes (Google, Bing, etc.)
    # The actual implementation doesn't use Falla directly
    _falla_engine_class: Any = Google  # Use Google as a default callable

    def __init__(self, config: Any, **kwargs: Any) -> None:
        """Initialize the Falla search engine."""
        super().__init__(config, **kwargs)

        # Create the Falla engine instance
        self._falla_engine = self._create_engine_instance()

        # Set global flag
        global _falla_initialized
        _falla_initialized = True

    def _create_engine_instance(self) -> Falla:
        """
        Create an instance of the Falla engine.

        Returns:
            Falla: Instance of the Falla engine class
        """
        # Create a new instance - each subclass of Falla has its own __init__
        # that handles initialization without explicit parameters
        return self._falla_engine_class()

    @ucache(maxsize=500, ttl=3600)  # Cache 500 searches for 1 hour
    async def search(self, query: str, **_kwargs: Any) -> list[SearchResult]:
        """
        Perform a search using the Falla engine.

        Args:
            query: Search query
            **_kwargs: Additional search parameters (ignored for Falla engines)

        Returns:
            list[SearchResult]: List of search results

        Raises:
            EngineError: If the search fails
        """
        try:
            # Perform the search using the async method
            # Falla engines return a list[dict[str, str]] as documented in their search_async method
            # Cast return value to ensure type safety
            raw_results = cast(list[dict[str, str]], await self._falla_engine.search_async(query=query))

            # Convert to SearchResult objects
            results = []
            for i, item in enumerate(raw_results):
                # Validate URL
                url = item.get("link", "")
                if not url:
                    continue

                try:
                    # Create search result object - Pydantic will validate the URL
                    result = SearchResult(
                        title=item.get("title", ""),
                        url=HttpUrl(url),  # Convert to HttpUrl type
                        snippet=item.get("snippet", ""),
                        source=self.engine_code,
                        rank=i + 1,
                        raw=item,
                    )
                    results.append(result)
                except ValueError as url_err:
                    # Log invalid URL but continue processing other results
                    logger.warning(f"Invalid URL '{url}' in {self.engine_code} result: {url_err}")
                    continue

            return self.limit_results(results)
        except Exception as e:
            logger.error(f"Search failed: {e!s}")
            msg = f"Search failed: {e!s}"
            raise EngineError(self.engine_code, msg) from e


# Define engine classes for specific Falla engines
@register_engine
class GoogleFallaEngine(FallaSearchEngine):
    """Google search implementation using Falla."""

    engine_code = "google_falla"
    friendly_engine_name = "Google (Falla)"
    _falla_engine_class = Google


@register_engine
class BingFallaEngine(FallaSearchEngine):
    """Bing search implementation using Falla."""

    engine_code = "bing_falla"
    friendly_engine_name = "Bing (Falla)"
    _falla_engine_class = Bing


@register_engine
class DuckDuckGoFallaEngine(FallaSearchEngine):
    """DuckDuckGo search implementation using Falla."""

    engine_code = "duckduckgo_falla"
    friendly_engine_name = "DuckDuckGo (Falla)"
    _falla_engine_class = DuckDuckGo


@register_engine
class YahooFallaEngine(FallaSearchEngine):
    """Yahoo search implementation using Falla."""

    engine_code = "yahoo_falla"
    friendly_engine_name = "Yahoo (Falla)"
    _falla_engine_class = Yahoo


@register_engine
class AskFallaEngine(FallaSearchEngine):
    """Ask.com search implementation using Falla."""

    engine_code = "ask_falla"
    friendly_engine_name = "Ask.com (Falla)"
    _falla_engine_class = Ask


@register_engine
class AolFallaEngine(FallaSearchEngine):
    """AOL search implementation using Falla."""

    engine_code = "aol_falla"
    friendly_engine_name = "AOL (Falla)"
    _falla_engine_class = Aol


@register_engine
class DogpileFallaEngine(FallaSearchEngine):
    """Dogpile search implementation using Falla."""

    engine_code = "dogpile_falla"
    friendly_engine_name = "Dogpile (Falla)"
    _falla_engine_class = DogPile


@register_engine
class GibiruFallaEngine(FallaSearchEngine):
    """Gibiru search implementation using Falla."""

    engine_code = "gibiru_falla"
    friendly_engine_name = "Gibiru (Falla)"
    _falla_engine_class = Gibiru


@register_engine
class MojeekFallaEngine(FallaSearchEngine):
    """Mojeek search implementation using Falla."""

    engine_code = "mojeek_falla"
    friendly_engine_name = "Mojeek (Falla)"
    _falla_engine_class = Mojeek


@register_engine
class QwantFallaEngine(FallaSearchEngine):
    """Qwant search implementation using Falla."""

    engine_code = "qwant_falla"
    friendly_engine_name = "Qwant (Falla)"
    _falla_engine_class = Qwant


@register_engine
class YandexFallaEngine(FallaSearchEngine):
    """Yandex search implementation using Falla."""

    engine_code = "yandex_falla"
    friendly_engine_name = "Yandex (Falla)"
    _falla_engine_class = Yandex


# Convenience functions for direct API access
# These match the function naming convention used in the module


async def google_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Google search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["google_falla"],
        **kwargs,
    )


async def bing_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Bing search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["bing_falla"],
        **kwargs,
    )


async def duckduckgo_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a DuckDuckGo search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["duckduckgo_falla"],
        **kwargs,
    )


async def yahoo_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Yahoo search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["yahoo_falla"],
        **kwargs,
    )


async def ask_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform an Ask.com search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["ask_falla"],
        **kwargs,
    )


async def aol_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform an AOL search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["aol_falla"],
        **kwargs,
    )


async def dogpile_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Dogpile search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["dogpile_falla"],
        **kwargs,
    )


async def gibiru_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Gibiru search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["gibiru_falla"],
        **kwargs,
    )


async def mojeek_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Mojeek search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["mojeek_falla"],
        **kwargs,
    )


async def qwant_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Qwant search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["qwant_falla"],
        **kwargs,
    )


async def yandex_falla(query: str, **kwargs: Any) -> list[SearchResult]:
    """
    Perform a Yandex search using Falla engine.

    Args:
        query: Search query
        **kwargs: Additional parameters passed to the search function

    Returns:
        list[SearchResult]: Search results
    """
    from twat_search.web.api import search

    return await search(
        query,
        engines=["yandex_falla"],
        **kwargs,
    )
