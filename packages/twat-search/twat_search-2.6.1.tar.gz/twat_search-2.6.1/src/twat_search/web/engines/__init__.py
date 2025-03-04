# this_file: src/twat_search/web/engines/__init__.py
"""
Package containing various search engine implementations for the twat_search.web API.

Each module in this package implements one or more search engines
that can be used with the API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from twat_search.web.engine_constants import (
    ALL_POSSIBLE_ENGINES,
    AOL_FALLA,
    ASK_FALLA,
    BING_FALLA,
    BING_SCRAPER,
    BRAVE,
    BRAVE_NEWS,
    CRITIQUE,
    DOGPILE_FALLA,
    DUCKDUCKGO,
    DUCKDUCKGO_FALLA,
    ENGINE_FRIENDLY_NAMES,
    GIBIRU_FALLA,
    GOOGLE_FALLA,
    GOOGLE_HASDATA,
    GOOGLE_HASDATA_FULL,
    GOOGLE_SCRAPER,
    GOOGLE_SERPAPI,
    MOJEEK_FALLA,
    PPLX,
    QWANT_FALLA,
    TAVILY,
    YAHOO_FALLA,
    YANDEX_FALLA,
    YOU,
    YOU_NEWS,
    standardize_engine_name,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from twat_search.web.models import SearchResult

# Import engine constants from the dedicated module

# Initialize __all__ list with engine name constants
__all__ = [
    # Helper functions
    "ALL_POSSIBLE_ENGINES",
    "AOL_FALLA",
    "ASK_FALLA",
    "BING_FALLA",
    # Engine name constants
    "BING_SCRAPER",
    "BRAVE",
    "BRAVE_NEWS",
    "CRITIQUE",
    "DOGPILE_FALLA",
    "DUCKDUCKGO",
    "DUCKDUCKGO_FALLA",
    "ENGINE_FRIENDLY_NAMES",
    "GIBIRU_FALLA",
    # Falla-based engines
    "GOOGLE_FALLA",
    "GOOGLE_HASDATA",
    "GOOGLE_HASDATA_FULL",
    "GOOGLE_SCRAPER",
    "GOOGLE_SERPAPI",
    "MOJEEK_FALLA",
    "PPLX",
    "QWANT_FALLA",
    "TAVILY",
    "YAHOO_FALLA",
    "YANDEX_FALLA",
    "YOU",
    "YOU_NEWS",
    "available_engine_functions",
    "get_available_engines",
    "get_engine_function",
    "is_engine_available",
    "standardize_engine_name",
]

# Dict to track available engine functions - using Any type to avoid signature incompatibilities
available_engine_functions: dict[str, Any] = {}

# Import base functionality first
try:
    from twat_search.web.engines.base import SearchEngine, get_engine, get_registered_engines, register_engine

    __all__.extend(
        ["SearchEngine", "get_engine", "get_registered_engines", "register_engine"],
    )
except ImportError:
    pass

# Import each engine module and add its components to __all__ if successful
try:
    from twat_search.web.engines.brave import BraveNewsSearchEngine, BraveSearchEngine, brave, brave_news

    available_engine_functions["brave"] = brave
    available_engine_functions["brave_news"] = brave_news
    __all__.extend(
        ["BraveNewsSearchEngine", "BraveSearchEngine", "brave", "brave_news"],
    )
except ImportError:
    pass


try:
    from twat_search.web.engines.tavily import TavilySearchEngine, tavily

    available_engine_functions["tavily"] = tavily
    __all__.extend(["TavilySearchEngine", "tavily"])
except ImportError:
    pass

try:
    from twat_search.web.engines.pplx import PerplexitySearchEngine, pplx

    available_engine_functions["pplx"] = pplx
    __all__.extend(["PerplexitySearchEngine", "pplx"])
except ImportError:
    pass

try:
    from twat_search.web.engines.you import YouNewsSearchEngine, YouSearchEngine, you, you_news

    available_engine_functions["you"] = you
    available_engine_functions["you_news"] = you_news
    __all__.extend(
        ["YouNewsSearchEngine", "YouSearchEngine", "you", "you_news"],
    )
except ImportError:
    pass

try:
    from twat_search.web.engines.critique import CritiqueSearchEngine, critique

    available_engine_functions["critique"] = critique
    __all__.extend(["CritiqueSearchEngine", "critique"])
except ImportError:
    pass

try:
    from twat_search.web.engines.duckduckgo import DuckDuckGoSearchEngine, duckduckgo

    available_engine_functions["duckduckgo"] = duckduckgo
    __all__.extend(["DuckDuckGoSearchEngine", "duckduckgo"])
except ImportError:
    pass

# Try to import bing_scraper engine
try:
    from twat_search.web.engines.bing_scraper import BingScraperSearchEngine, bing_scraper

    available_engine_functions["bing_scraper"] = bing_scraper
    __all__.extend(["BingScraperSearchEngine", "bing_scraper"])
except ImportError as e:
    logger.warning(f"Failed to import bing_scraper: {e}")

# Import HasData engines
try:
    from twat_search.web.engines.hasdata import (
        HasDataGoogleEngine,
        HasDataGoogleLightEngine,
        hasdata_google,
        hasdata_google_full,
    )

    available_engine_functions["hasdata_google"] = hasdata_google
    available_engine_functions["hasdata_google_full"] = hasdata_google_full
    __all__.extend(
        [
            "HasDataGoogleEngine",
            "HasDataGoogleLightEngine",
            "hasdata_google",
            "hasdata_google_full",
        ],
    )
except ImportError:
    pass

# Import Google Scraper engine
try:
    from twat_search.web.engines.google_scraper import GoogleScraperEngine, google_scraper

    available_engine_functions["google_scraper"] = google_scraper
    __all__.extend(["GoogleScraperEngine", "google_scraper"])
except (ImportError, SyntaxError) as e:
    logger.warning(f"Failed to import google_scraper module: {e}")

# Try to import SerpAPI engine
try:
    from twat_search.web.engines.serpapi import SerpApiSearchEngine, google_serpapi

    available_engine_functions["google_serpapi"] = google_serpapi
    __all__.extend(["SerpApiSearchEngine", "google_serpapi"])
except (ImportError, AttributeError):
    pass


# Import Falla-based engines
try:
    from twat_search.web.engines.falla import (
        AolFallaEngine,
        AskFallaEngine,
        BingFallaEngine,
        DogpileFallaEngine,
        DuckDuckGoFallaEngine,
        FallaSearchEngine,
        GibiruFallaEngine,
        GoogleFallaEngine,
        MojeekFallaEngine,
        QwantFallaEngine,
        YahooFallaEngine,
        YandexFallaEngine,
        aol_falla,
        ask_falla,
        bing_falla,
        dogpile_falla,
        duckduckgo_falla,
        gibiru_falla,
        google_falla,
        is_falla_available,
        mojeek_falla,
        qwant_falla,
        yahoo_falla,
        yandex_falla,
    )

    # Register engine functions
    if is_falla_available():
        available_engine_functions["google_falla"] = google_falla
        available_engine_functions["bing_falla"] = bing_falla
        available_engine_functions["duckduckgo_falla"] = duckduckgo_falla
        available_engine_functions["yahoo_falla"] = yahoo_falla
        available_engine_functions["ask_falla"] = ask_falla
        available_engine_functions["aol_falla"] = aol_falla
        available_engine_functions["dogpile_falla"] = dogpile_falla
        available_engine_functions["gibiru_falla"] = gibiru_falla
        available_engine_functions["mojeek_falla"] = mojeek_falla
        available_engine_functions["qwant_falla"] = qwant_falla
        available_engine_functions["yandex_falla"] = yandex_falla

    else:
        logger.warning("Falla search engines are not available")

    # Add to __all__
    __all__.extend(
        [
            "AolFallaEngine",
            "AskFallaEngine",
            "BingFallaEngine",
            "DogpileFallaEngine",
            "DuckDuckGoFallaEngine",
            "FallaSearchEngine",
            "GibiruFallaEngine",
            "GoogleFallaEngine",
            "MojeekFallaEngine",
            "QwantFallaEngine",
            "YahooFallaEngine",
            "YandexFallaEngine",
            "aol_falla",
            "ask_falla",
            "bing_falla",
            "dogpile_falla",
            "duckduckgo_falla",
            "gibiru_falla",
            "google_falla",
            "is_falla_available",
            "mojeek_falla",
            "qwant_falla",
            "yahoo_falla",
            "yandex_falla",
        ],
    )
except (ImportError, SyntaxError) as e:
    logger.warning(f"Failed to import falla module: {e}")


# Add helper functions
def is_engine_available(engine_name: str) -> bool:
    """Check if an engine is available (its dependencies are installed).

    Args:
        engine_name: Name of the engine to check

    Returns:
        True if the engine is available, False otherwise
    """
    standardized_name = standardize_engine_name(engine_name)
    return standardized_name in available_engine_functions


def get_engine_function(
    engine_name: str,
) -> Callable[..., Coroutine[Any, Any, list[SearchResult]]] | None:
    """Get the function for a specific engine.

    Args:
        engine_name: Name of the engine

    Returns:
        The engine function if available, None otherwise
    """
    standardized_name = standardize_engine_name(engine_name)
    return available_engine_functions.get(standardized_name)


def get_available_engines() -> list[str]:
    """Get a list of all available engines.

    Returns:
        List of available engine names
    """
    return list(available_engine_functions.keys())
