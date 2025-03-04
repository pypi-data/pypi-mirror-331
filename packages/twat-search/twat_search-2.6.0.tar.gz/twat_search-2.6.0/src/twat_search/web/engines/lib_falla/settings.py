"""
Settings for the Falla search engine scraper.

This module provides configuration settings for the Falla search engine scraper.
"""

from __future__ import annotations

import os
from pathlib import Path

# Default settings
SPLASH_SCRAP_URL = os.environ.get("FALLA_SPLASH_SCRAP_URL", "http://localhost:8050")

# Path to the Falla directory
FALLA_DIR = Path(__file__).parent
