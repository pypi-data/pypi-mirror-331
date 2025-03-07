# this_file: src/twat_search/web/engines/lib_falla/utils.py
"""
Utility functions for the Falla search engine scraper.

This module provides helper functions for working with Falla search engines.
"""

import logging
from pathlib import Path

# Import all the search engine implementations
from twat_search.web.engines.lib_falla.core.aol import Aol
from twat_search.web.engines.lib_falla.core.ask import Ask
from twat_search.web.engines.lib_falla.core.bing import Bing
from twat_search.web.engines.lib_falla.core.dogpile import DogPile
from twat_search.web.engines.lib_falla.core.duckduckgo import DuckDuckGo
from twat_search.web.engines.lib_falla.core.falla import Falla
from twat_search.web.engines.lib_falla.core.gibiru import Gibiru
from twat_search.web.engines.lib_falla.core.google import Google
from twat_search.web.engines.lib_falla.core.mojeek import Mojeek
from twat_search.web.engines.lib_falla.core.qwant import Qwant
from twat_search.web.engines.lib_falla.core.searchencrypt import SearchEncrypt
from twat_search.web.engines.lib_falla.core.startpage import StartPage
from twat_search.web.engines.lib_falla.core.yahoo import Yahoo
from twat_search.web.engines.lib_falla.core.yandex import Yandex

# Set up logger
logger = logging.getLogger(__name__)


class Bcolors:
    """Terminal colors for pretty printing."""

    AUTRE = "\033[96m"  # rose
    HEADER = "\033[95m"  # rose
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"  # jaune
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def list_engines() -> list[str]:
    """
    List all available search engines.

    Returns:
        List[str]: List of available search engine names.
    """
    engines = []
    core_dir = Path(__file__).parent / "core"

    for file in core_dir.glob("*.py"):
        if file.name not in ["__init__.py", "falla.py"] and not file.name.startswith("__"):
            engine_name = file.stem
            engines.append(engine_name)

    return sorted(engines)


# Dictionary mapping engine names to their classes
ENGINES_MAP = {
    "aol": Aol,
    "ask": Ask,
    "bing": Bing,
    "dogpile": DogPile,
    "duckduckgo": DuckDuckGo,
    "gibiru": Gibiru,
    "google": Google,
    "mojeek": Mojeek,
    "qwant": Qwant,
    "searchencrypt": SearchEncrypt,
    "startpage": StartPage,
    "yahoo": Yahoo,
    "yandex": Yandex,
}


def get_engine_class(engine: str) -> type[Falla]:
    """
    Get the Falla engine class for a given engine name.

    Args:
        engine: Name of the search engine (case-insensitive)

    Returns:
        Type[Falla]: The engine class

    Raises:
        ValueError: If the engine is not found
    """
    engine_lower = engine.lower()
    if engine_lower not in ENGINES_MAP:
        available = ", ".join(ENGINES_MAP.keys())
        msg = f"Engine '{engine}' not found. Available engines: {available}"
        raise ValueError(msg)

    return ENGINES_MAP[engine_lower]


def get_results(engine: str, query: str, num_results: int = 10) -> list[dict[str, str]]:
    """
    Get search results from the specified engine using the synchronous API.

    Args:
        engine: Name of the search engine to use
        query: Search query
        num_results: Number of results to return (default: 10)

    Returns:
        List[Dict[str, str]]: List of search results, each containing title, link, and snippet

    Raises:
        ValueError: If the engine is not found
    """
    engine_class = get_engine_class(engine)
    engine_instance = engine_class()

    try:
        results = engine_instance.search(query)

        # Limit the number of results
        if num_results and len(results) > num_results:
            results = results[:num_results]

        return results
    except Exception as e:
        logger.error(f"Error getting results from {engine}: {e}")
        return []


async def get_results_async(engine: str, query: str, num_results: int = 10) -> list[dict[str, str]]:
    """
    Get search results from the specified engine using the asynchronous API.

    Args:
        engine: Name of the search engine to use
        query: Search query
        num_results: Number of results to return (default: 10)

    Returns:
        List[Dict[str, str]]: List of search results, each containing title, link, and snippet

    Raises:
        ValueError: If the engine is not found
    """
    engine_class = get_engine_class(engine)
    engine_instance = engine_class()

    try:
        results = await engine_instance.search_async(query)

        # Limit the number of results
        if num_results and len(results) > num_results:
            results = results[:num_results]

        return results
    except Exception as e:
        logger.error(f"Error getting results from {engine}: {e}")
        return []
    finally:
        # Make sure to clean up resources
        await engine_instance.close()
