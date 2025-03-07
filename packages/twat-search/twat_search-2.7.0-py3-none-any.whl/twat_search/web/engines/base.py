# this_file: src/twat_search/web/engines/base.py
"""
Base class and factory functions for search engines.

This module defines the abstract base class that all search engines must
implement, as well as functions to register and instantiate engines.
"""

from __future__ import annotations

import abc
import asyncio
import logging
import os
import random
from typing import TYPE_CHECKING, Any, ClassVar

import httpx

from twat_search.web.exceptions import EngineError, SearchError

if TYPE_CHECKING:
    from twat_search.web.config import EngineConfig
    from twat_search.web.models import SearchResult

# Initialize logger
logger = logging.getLogger(__name__)

# List of user agents to rotate for scrapers to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
]


class SearchEngine(abc.ABC):
    """
    Abstract base class for all search engines.

    All search engine implementations must subclass this and implement
    the search method.
    """

    # Class variables that must be defined by subclasses
    engine_code: ClassVar[str] = ""
    # User-friendly name for display purposes
    friendly_engine_name: ClassVar[str] = ""
    # List of environment variable names that can hold the API key
    env_api_key_names: ClassVar[list[str]] = []
    # Override with engine-specific names
    env_enabled_names: ClassVar[list[str]] = []
    # Override with engine-specific names
    env_params_names: ClassVar[list[str]] = []

    # Instance variables
    api_key: str | None

    def __init__(self, config: EngineConfig, **kwargs: Any) -> None:
        """
        Initialize the search engine with configuration and common parameters.

        Args:
            config: Engine configuration
            **kwargs: Additional engine-specific parameters
        """
        self.config = config
        self.kwargs = kwargs

        # Common parameters with default values
        self.num_results = kwargs.get("num_results", 5)
        self.country = kwargs.get("country")
        self.language = kwargs.get("language")
        self.safe_search = kwargs.get("safe_search", True)
        self.time_frame = kwargs.get("time_frame")

        # Settings for robust HTTP requests - can be overridden in kwargs
        self.timeout = kwargs.get("timeout", 10)
        self.retries = kwargs.get("retries", 2)
        self.retry_delay = kwargs.get("retry_delay", 1.0)
        self.use_random_user_agent = kwargs.get("use_random_user_agent", True)

        if not config.enabled:
            msg = f"Engine '{self.engine_code}' is disabled."
            raise EngineError(self.engine_code, msg)

        # Check for API key if required
        if self.env_api_key_names:
            # Add detailed debugging
            logger.debug(f"Engine '{self.engine_code}' requires an API key")
            logger.debug(f"Config API key: {self.config.api_key is not None}")
            if self.config.api_key:
                # Safely log a portion of the API key
                key_value = self.config.api_key
                key_prefix = key_value[:4] if len(key_value) > 4 else "****"
                key_suffix = key_value[-4:] if len(key_value) > 4 else "****"
                logger.debug(f"Config API key value: {key_prefix}...{key_suffix}")

            # Check environment variables directly
            for env_var in self.env_api_key_names:
                env_value = os.environ.get(env_var)
                logger.debug(f"Environment variable {env_var}: {env_value is not None}")
                if env_value:
                    # Safely log a portion of the environment variable value
                    env_prefix = env_value[:4] if len(env_value) > 4 else "****"
                    env_suffix = env_value[-4:] if len(env_value) > 4 else "****"
                    logger.debug(f"Env var {env_var} value: {env_prefix}...{env_suffix}")

            # Check if the API key is being set from the environment in the config
            logger.debug(f"Final API key check before validation: {self.config.api_key is not None}")

            if not self.config.api_key:
                msg = (
                    f"API key is required for {self.engine_code}. "
                    f"Please set it via one of these env vars: {', '.join(self.env_api_key_names)}"
                )
                logger.error(f"API key validation failed: {msg}")
                raise EngineError(self.engine_code, msg)

            logger.debug(f"API key validation passed for {self.engine_code}")
            self.api_key = self.config.api_key
        else:
            self.api_key = None

    def _get_num_results(self, param_name: str = "num_results", min_value: int = 1) -> int:
        """
        Get the standardized number of results to return, respecting user preference.

        This method should be used by all engine implementations to ensure
        the num_results parameter is consistently respected.

        Args:
            param_name: The engine-specific parameter name for number of results
                        (e.g., "num_results", etc.)
            min_value: The minimum value that the engine accepts

        Returns:
            The number of results to request
        """
        # Get value from kwargs
        value = self.kwargs.get(param_name)
        if value is not None:
            try:
                return max(min_value, int(value))
            except (TypeError, ValueError):
                logger.warning(f"Invalid value for '{param_name}' ({value!r}) in {self.engine_code}, using default.")
                # Fall through to next option if value is invalid

        # If not in kwargs get from config
        default = self.config.default_params.get(param_name) or self.config.default_params.get("num_results")
        if default is not None:
            try:
                return max(min_value, int(default))
            except (TypeError, ValueError):
                logger.warning(
                    f"Invalid default value for '{param_name}' ({default!r}) in {self.engine_code}, using fallback.",
                )
                # Fall through to default if value is invalid

        # Return a reasonable default
        return 5

    @property
    def max_results(self) -> int:
        """
        Get the maximum number of results to return based on user input or defaults.

        Returns:
            The maximum number of results to return.
        """
        return self._get_num_results(param_name="num_results", min_value=1)

    def limit_results(self, results: list[SearchResult]) -> list[SearchResult]:
        """
        Limit the number of results to respect the user's num_results parameter.

        This method should be called at the end of search implementations to ensure
        that regardless of how many results are gathered, we respect the user's
        requested limit.

        Args:
            results: The full list of results

        Returns:
            A list limited to max_results items
        """
        # Add debug logging
        logger.debug(f"limit_results: Got {len(results)} results, self.num_results={self.num_results}")

        # If we have no results, just return the empty list
        if not results:
            return results

        max_results = self.max_results
        logger.debug(f"limit_results: Using max_results={max_results}")

        if max_results > 0 and len(results) > max_results:
            limited = results[:max_results]
            logger.debug(f"limit_results: Limiting to {len(limited)} results")
            return limited

        logger.debug(f"limit_results: Returning all {len(results)} results (no limiting needed)")
        return results

    async def make_http_request(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_data: Any = None,
        timeout: float | None = None,
        retries: int | None = None,
        retry_delay: float | None = None,
    ) -> httpx.Response:
        """
        Make a robust HTTP request with built-in retries and configurable settings.

        This method is designed to make HTTP requests more robust, especially for scrapers
        that might be blocked or rate-limited.

        Args:
            url: The URL to request
            method: HTTP method (GET, POST, etc.)
            headers: HTTP headers to include
            params: URL parameters
            json_data: JSON data for request body
            timeout: Request timeout in seconds
            retries: Number of retries on failure
            retry_delay: Delay between retries in seconds

        Returns:
            httpx.Response: The HTTP response

        Raises:
            EngineError: If all request attempts fail
        """
        # Set defaults if not provided
        actual_timeout = self.timeout if timeout is None else timeout
        actual_retries = self.retries if retries is None else retries
        actual_retry_delay = self.retry_delay if retry_delay is None else retry_delay

        # Build headers with random user agent if enabled
        if headers is None:
            headers = {}

        if self.use_random_user_agent and "user-agent" not in {k.lower() for k in headers}:
            headers["User-Agent"] = random.choice(USER_AGENTS)

        delay = actual_retry_delay  # Initial delay
        # Initialize with None, but will be a RequestError or HTTPStatusError after a failed attempt
        last_error: httpx.RequestError | httpx.HTTPStatusError | None = None

        # Try the request multiple times
        for attempt in range(1, actual_retries + 2):  # +2 because we want actual_retries+1 attempts
            try:
                async with httpx.AsyncClient(timeout=actual_timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_data,
                    )
                    response.raise_for_status()
                    return response
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt > actual_retries:
                    # Final retry failed
                    # This will be reached on the last iteration if all attempts fail
                    break

                # Add jitter to retry delay to avoid thundering herd effect
                jitter = random.uniform(0.5, 1.5)
                actual_delay = delay * jitter

                # Log the error and retry
                logger.warning(
                    f"Request failed (attempt {attempt}/{actual_retries + 1}), retrying in {actual_delay:.2f}s: {exc}",
                )

                await asyncio.sleep(actual_delay)
                delay *= 2  # Exponential backoff

        # If we get here, all attempts failed
        # At this point, last_error should always be set to a RequestError or HTTPStatusError
        # because we only exit the loop after at least one attempt has failed
        # But we'll add a fallback just in case (should never happen)
        if last_error is None:
            last_error = httpx.RequestError("Unknown error occurred during HTTP request")

        msg = f"HTTP request failed after {actual_retries + 1} attempts: {last_error}"
        raise EngineError(self.engine_code, msg) from last_error

    @abc.abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        """
        Search using this engine.

        Args:
            query: The search query

        Returns:
            List of search results
        """

    def _get_api_key(self) -> str:
        """
        Get the API key for the search engine.

        Returns:
            The API key.

        Raises:
            EngineError: If the API key is missing.
        """
        if not self.config.api_key:
            raise EngineError(
                self.engine_code,
                f"API key is required. Set it via one of these env vars: {', '.join(self.env_api_key_names)}",
            )
        return self.config.api_key


# Registry of available search engines
_engine_registry: dict[str, type[SearchEngine]] = {}


def register_engine(engine_class: type[SearchEngine]) -> type[SearchEngine]:
    """
    Register a search engine class.

    Args:
        engine_class: The search engine class to register

    Returns:
        The registered search engine class
    """
    try:
        # Check that the engine class has required attributes
        if not hasattr(engine_class, "engine_code") or not engine_class.engine_code:
            error_msg = "Engine must define a non-empty 'engine_code' attribute."
            raise AttributeError(error_msg)

        # Now check for env_api_key_names attribute
        if not hasattr(engine_class, "env_api_key_names"):
            error_msg = "Engine must define a 'env_api_key_names' attribute."
            raise AttributeError(error_msg)

        # Register the engine
        _engine_registry[engine_class.engine_code] = engine_class

        # Set friendly_name if not defined
        if not engine_class.friendly_engine_name:
            try:
                from twat_search.web.engine_constants import ENGINE_FRIENDLY_NAMES

                engine_class.friendly_engine_name = ENGINE_FRIENDLY_NAMES.get(
                    engine_class.engine_code,
                    engine_class.engine_code,
                )
            except ImportError:
                engine_class.friendly_engine_name = engine_class.engine_code

        return engine_class
    except Exception as e:
        logger.error(f"Failed to register engine {engine_class.__name__}: {e}")
        return engine_class  # Return the class even if registration failed


def get_engine(engine_name: str, config: EngineConfig, **kwargs: Any) -> SearchEngine:
    """
    Get an instance of a search engine by name.

    This function looks up the engine class by name, then instantiates it
    with the provided configuration and parameters.

    Args:
        engine_name: Name of the engine to instantiate
        config: Engine configuration
        **kwargs: Additional engine-specific parameters

    Returns:
        An instance of the requested search engine

    Raises:
        SearchError: If the engine is not found
    """
    # Get the registry of engines
    engines = get_registered_engines()

    # Standardize the engine name for lookup
    from twat_search.web.engines import standardize_engine_name

    std_engine_name = standardize_engine_name(engine_name)

    # Try to find the engine class
    engine_class = engines.get(std_engine_name)

    # If not found with standardized name, try original name (for backward compatibility)
    if engine_class is None:
        engine_class = engines.get(engine_name)

    # If still not found, provide a helpful error message
    if engine_class is None:
        available_engines = ", ".join(sorted(engines.keys()))
        msg = f"Engine '{engine_name}' not found. Available engines: {available_engines}"
        logger.error(msg)
        msg = f"Unknown search engine '{engine_name}'"
        raise SearchError(msg)

    try:
        # Check if the engine is enabled in the configuration
        if not config.enabled:
            msg = (
                f"Engine '{engine_name}' is disabled in configuration. "
                f"Enable it by setting the appropriate environment variable "
                f"or updating the configuration."
            )
            logger.warning(msg)
            raise EngineError(engine_name, msg)

        # Try to instantiate the engine
        engine_instance = engine_class(config, **kwargs)
        logger.debug(f"Successfully initialized engine: {engine_name}")
        return engine_instance
    except EngineError as e:
        # Re-raise EngineError with more context if needed
        if "API key" in str(e):
            # Provide more helpful information for API key errors
            env_vars = getattr(engine_class, "env_api_key_names", [])
            env_vars_str = ", ".join(env_vars) if env_vars else "No environment variables defined"
            msg = f"{e!s} Environment variables for this engine: {env_vars_str}"
            logger.error(msg)
            raise EngineError(engine_name, msg) from e
        # For other EngineError types, just re-raise
        raise
    except Exception as e:
        # For any other exception, wrap it in an EngineError with context
        msg = f"Failed to initialize engine '{engine_name}': {e}"
        logger.error(msg)
        raise EngineError(engine_name, msg) from e


def get_registered_engines() -> dict[str, type[SearchEngine]]:
    """
    Get a dictionary of all registered search engines.

    Returns:
        A dictionary mapping engine codes to engine classes.
    """
    return _engine_registry.copy()
