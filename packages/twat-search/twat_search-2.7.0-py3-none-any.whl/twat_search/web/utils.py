# this_file: src/twat_search/web/utils.py
"""
Utility functions for the web search API.

This module provides various utility functions used by the web search API.
"""

from __future__ import annotations

import logging
import os
import time
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

# Add proper dotenv loading

# Set up logging
logger = logging.getLogger(__name__)


def load_environment(force_reload: bool = False) -> None:
    """
    Load environment variables from .env file.

    This function provides a consistent way to load environment variables across the codebase.

    Args:
        force_reload: Whether to reload the environment variables even if they're already loaded
    """
    loaded_flag = "_TWAT_SEARCH_ENV_LOADED"
    # Check if we've already loaded the environment variables
    if not force_reload and os.environ.get(loaded_flag) == "1":
        logger.debug("Environment variables already loaded")
        return

    # Load environment variables from .env file
    load_dotenv()

    # Set a flag to indicate that we've loaded the variables
    os.environ[loaded_flag] = "1"

    # Log which API keys are found
    if logger.isEnabledFor(logging.DEBUG):  # Only in debug mode
        for key, value in os.environ.items():
            if ("API_KEY" in key or "_KEY" in key) and key != loaded_flag:
                masked_value = value[:4] + "****" if value else None
                logger.debug(
                    f"Found environment variable: {key}={masked_value}",
                )
    else:
        logger.info("Environment variables loaded")


class RateLimiter:
    """
    Rate limiter to prevent sending too many requests to an API.

    Args:
        calls_per_second: Maximum number of calls per second
    """

    def __init__(self, calls_per_second: float) -> None:
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
        self.call_timestamps: list[float] = []

    async def wait(self) -> None:
        """
        Wait until we can make another API call.
        """
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        if elapsed < self.min_interval:
            delay = self.min_interval - elapsed
            logger.debug(f"Rate limiter sleeping for {delay:.4f} seconds")
            time.sleep(delay)
        self.last_call_time = time.time()

    def wait_if_needed(self) -> None:
        """
        Wait if needed to respect the rate limit.

        This method is used by the tests to check rate limiting functionality.
        """
        current_time = time.time()

        # Clean up old timestamps (older than 1 second)
        self.call_timestamps = [ts for ts in self.call_timestamps if current_time - ts <= 1.0]

        # Check if we need to wait
        if len(self.call_timestamps) >= self.calls_per_second:
            oldest_timestamp = min(self.call_timestamps)
            elapsed = current_time - oldest_timestamp
            if elapsed < 1.0:  # If less than 1 second has passed since oldest call
                delay = 1.0 - elapsed
                logger.debug(f"Rate limiter sleeping for {delay:.4f} seconds")
                time.sleep(delay)

        # Record this call
        self.call_timestamps.append(time.time())


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain name (e.g., "example.com")
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    if not domain:
        # If netloc is empty, the URL might not include the protocol
        # Try parsing the path as a domain
        parsed = urlparse(f"https://{url}")
        domain = parsed.netloc
    return domain


def extract_query_param(url: str, param: str) -> str | None:
    """
    Extract a query parameter from a URL.

    Args:
        url: URL to extract parameter from
        param: Parameter name to extract

    Returns:
        Parameter value or None if not found
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get(param, [None])[0]
