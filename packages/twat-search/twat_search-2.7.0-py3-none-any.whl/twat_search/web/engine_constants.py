# this_file: src/twat_search/web/engine_constants.py
"""
Constants defining engine names and utility functions for standardization.

This module is separate to avoid circular dependencies between engines and config.
"""

# Engine name constants for use throughout the codebase
# These constants should be used instead of string literals
from __future__ import annotations

DEFAULT_NUM_RESULTS = 5

BING_SCRAPER = "bing_scraper"
BRAVE = "brave"
BRAVE_NEWS = "brave_news"
CRITIQUE = "critique"
DUCKDUCKGO = "duckduckgo"
GOOGLE_HASDATA = "google_hasdata"
GOOGLE_HASDATA_FULL = "google_hasdata_full"
GOOGLE_SCRAPER = "google_scraper"
GOOGLE_SERPAPI = "google_serpapi"
PPLX = "pplx"
TAVILY = "tavily"
YOU = "you"
YOU_NEWS = "you_news"

# Falla-based engines
GOOGLE_FALLA = "google_falla"
BING_FALLA = "bing_falla"
DUCKDUCKGO_FALLA = "duckduckgo_falla"
AOL_FALLA = "aol_falla"
ASK_FALLA = "ask_falla"
DOGPILE_FALLA = "dogpile_falla"
GIBIRU_FALLA = "gibiru_falla"
MOJEEK_FALLA = "mojeek_falla"
QWANT_FALLA = "qwant_falla"
YAHOO_FALLA = "yahoo_falla"
YANDEX_FALLA = "yandex_falla"


# Complete list of all possible engines
ALL_POSSIBLE_ENGINES = [
    BING_SCRAPER,
    BRAVE_NEWS,
    BRAVE,
    CRITIQUE,
    DUCKDUCKGO,
    GOOGLE_HASDATA_FULL,
    GOOGLE_HASDATA,
    GOOGLE_SCRAPER,
    GOOGLE_SERPAPI,
    PPLX,
    TAVILY,
    YOU_NEWS,
    YOU,
    # Falla-based engines
    GOOGLE_FALLA,
    BING_FALLA,
    DUCKDUCKGO_FALLA,
    AOL_FALLA,
    ASK_FALLA,
    DOGPILE_FALLA,
    GIBIRU_FALLA,
    MOJEEK_FALLA,
    QWANT_FALLA,
    YAHOO_FALLA,
    YANDEX_FALLA,
]

# Dictionary of friendly names for engines
ENGINE_FRIENDLY_NAMES = {
    BING_SCRAPER: "Bing scaper",
    BRAVE_NEWS: "Brave News with API key",
    BRAVE: "Brave with API key",
    CRITIQUE: "Critique Labs with API key",
    DUCKDUCKGO: "DuckDuckGo",
    GOOGLE_HASDATA_FULL: "Full Google scraper via HasData with API key",
    GOOGLE_HASDATA: "Light Google scraper via HasData with API key",
    GOOGLE_SCRAPER: "Google scraper",
    GOOGLE_SERPAPI: "Google via SerpAPI with API key",
    PPLX: "Perplexity with API key",
    TAVILY: "Tavily with API key",
    YOU_NEWS: "You.com News with API key",
    YOU: "You.com with API key",
    # Falla-based engines
    GOOGLE_FALLA: "Google (Falla)",
    BING_FALLA: "Bing (Falla)",
    DUCKDUCKGO_FALLA: "DuckDuckGo (Falla)",
    AOL_FALLA: "AOL (Falla)",
    ASK_FALLA: "Ask.com (Falla)",
    DOGPILE_FALLA: "DogPile (Falla)",
    GIBIRU_FALLA: "Gibiru (Falla)",
    MOJEEK_FALLA: "Mojeek (Falla)",
    QWANT_FALLA: "Qwant (Falla)",
    YAHOO_FALLA: "Yahoo (Falla)",
    YANDEX_FALLA: "Yandex (Falla)",
}


def standardize_engine_name(engine_name: str) -> str:
    """Standardize engine name by replacing hyphens with underscores.

    Args:
        engine_name: The engine name to standardize

    Returns:
        The standardized engine name
    """
    return engine_name.replace("-", "_")
