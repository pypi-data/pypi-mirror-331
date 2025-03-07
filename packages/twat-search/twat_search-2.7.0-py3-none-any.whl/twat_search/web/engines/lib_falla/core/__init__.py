"""
Core module for the Falla search engine scraper.

This module contains the base Falla class and the specific search engine implementations.
"""

# this_file: src/twat_search/web/engines/lib_falla/core/__init__.py

from __future__ import annotations

# Import all engine classes
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

# Define __all__ to explicitly export the classes
__all__ = [
    "Aol",
    "Ask",
    "Bing",
    "DogPile",
    "DuckDuckGo",
    "Falla",
    "Gibiru",
    "Google",
    "Mojeek",
    "Qwant",
    "SearchEncrypt",
    "StartPage",
    "Yahoo",
    "Yandex",
]
