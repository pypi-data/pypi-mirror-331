"""
Falla search engine scraper package.

This package provides search engine scraping functionality for the twat-search project.
Falla is embedded within this project to avoid external dependencies and provide
a stable implementation of search engine scraping.
"""

# this_file: src/twat_search/web/engines/lib_falla/__init__.py

from pathlib import Path

__version__ = "0.1.0"

# Set up package path
PACKAGE_PATH = Path(__file__).parent

# Available engine names for external use
AVAILABLE_ENGINES = [
    "aol",
    "ask",
    "bing",
    "dogpile",
    "duckduckgo",
    "gibiru",
    "google",
    "mojeek",
    "qwant",
    "searchencrypt",
    "startpage",
    "yahoo",
    "yandex",
]

# Export constants and utility functions - alphabetically sorted
__all__ = ["AVAILABLE_ENGINES", "PACKAGE_PATH", "__version__"]
