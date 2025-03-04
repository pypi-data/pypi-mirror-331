"""
TwAT Search package - Tools for web search and information retrieval.

This package provides utilities for searching the web and retrieving information
from various sources.
"""

# Initialize empty __all__ list
from __future__ import annotations

__all__ = []

# Include version
try:
    from twat_search.__version__ import version as __version__

    __all__.append("__version__")
except ImportError:
    __version__ = "0.1.0"  # Fallback version
    __all__.append("__version__")

# Configure twat_cache if available
try:
    import twat_cache

    from twat_search.paths import get_cache_dir

    # Configure twat_cache to use the paths from twat_os
    twat_cache.utils.get_cache_path = lambda *args, **kwargs: get_cache_dir()
except ImportError:
    pass  # twat_cache is not installed, no configuration needed

# Import submodules if available
try:
    from twat_search import web

    __all__.append("web")
except ImportError:
    pass
