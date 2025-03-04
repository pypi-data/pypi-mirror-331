# this_file: src/twat_search/web/config.py
"""
Configuration management for the web search module.

This module handles loading and managing configuration for the web search API.
It supports loading from environment variables, a configuration file, or explicit parameters.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, ClassVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from twat_search.web.engine_constants import (
    AOL_FALLA,
    ASK_FALLA,
    BING_FALLA,
    BING_SCRAPER,
    BRAVE,
    BRAVE_NEWS,
    CRITIQUE,
    DEFAULT_NUM_RESULTS,
    DOGPILE_FALLA,
    DUCKDUCKGO,
    DUCKDUCKGO_FALLA,
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
)

# Load environment variables from .env file if present
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Default configuration data
DEFAULT_CONFIG: dict[str, dict[str, Any]] = {
    "engines": {
        # DuckDuckGo
        DUCKDUCKGO: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "region": "us-en",
                "safesearch": "moderate",
                "timelimit": "y",  # past year
                "num_results": 20,
            },
        },
        # Brave API-based
        BRAVE: {
            "enabled": True,
            "api_key": None,  # BRAVE_API_KEY
            "default_params": {
                "country": "US",
                "language": "en-US",
                "safe_search": True,
            },
        },
        # Tavily
        TAVILY: {
            "enabled": True,
            "api_key": None,  # TAVILY_API_KEY
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "search_depth": "basic",  # or "advanced"
                "include_domains": [],
                "exclude_domains": [],
                "include_answer": False,
                "include_raw_content": False,
                "include_images": False,
            },
        },
        # You.com
        YOU: {
            "enabled": True,
            "api_key": None,  # YOU_API_KEY
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "country_code": "us",
                "safe_search": True,
            },
        },
        # You.com News
        YOU_NEWS: {
            "enabled": True,
            "api_key": None,  # YOU_API_KEY (same as You.com)
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "country_code": "us",
                "safe_search": True,
            },
        },
        # Perplexity
        PPLX: {
            "enabled": True,
            "api_key": None,  # PPLX_API_KEY
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "focus": None,  # None, "research", "writing", "coding", "scholar", "wolfram", "youtube"
            },
        },
        # Critique
        CRITIQUE: {
            "enabled": True,
            "api_key": None,  # CRITIQUE_API_KEY
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "relevance_adjustment": 0.5,
            },
        },
        # Brave News
        BRAVE_NEWS: {
            "enabled": True,
            "api_key": None,  # BRAVE_API_KEY (same as Brave Search)
            "default_params": {
                "country": "US",
                "language": "en-US",
                "freshness": "last7days",
            },
        },
        # Google HasData Light
        GOOGLE_HASDATA: {
            "enabled": True,
            "api_key": None,  # HASDATA_API_KEY
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "language": "en",
            },
        },
        # Google HasData Full
        GOOGLE_HASDATA_FULL: {
            "enabled": True,
            "api_key": None,  # HASDATA_API_KEY (same as Google HasData)
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
                "language": "en",
            },
        },
        # SerpAPI (Google)
        GOOGLE_SERPAPI: {
            "enabled": True,
            "api_key": None,
            "default_params": {
                "country": "us",
                "language": "en",
                "safe_search": True,
            },
        },
        # Google Scraper
        GOOGLE_SCRAPER: {
            "enabled": True,
            "api_key": None,  # No API key required, it's a scraper
            "default_params": {"num_results": DEFAULT_NUM_RESULTS, "language": "en", "safe": True},
        },
        # Bing Scraper
        BING_SCRAPER: {
            "enabled": True,
            "api_key": None,  # No API key required, it's a scraper
            "default_params": {"num_pages": 1, "delay": 0.5},
        },
        # Falla-based engines
        GOOGLE_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        BING_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        DUCKDUCKGO_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        YAHOO_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        ASK_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        AOL_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        DOGPILE_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        GIBIRU_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        MOJEEK_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        QWANT_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
        YANDEX_FALLA: {
            "enabled": True,
            "api_key": None,  # No API key required
            "default_params": {
                "num_results": DEFAULT_NUM_RESULTS,
            },
        },
    },
}


# Environment variable mapping - simple mapping for single path assignments
ENV_VAR_MAP: dict[str, str | list[str]] = {
    # General
    "TWAT_SEARCH_LOG_LEVEL": "log_level",
    # API keys for unique engines
    "SERPAPI_API_KEY": ["engines", GOOGLE_SERPAPI, "api_key"],
    "TAVILY_API_KEY": ["engines", TAVILY, "api_key"],
    "PPLX_API_KEY": ["engines", PPLX, "api_key"],
    "CRITIQUE_API_KEY": ["engines", CRITIQUE, "api_key"],
    # Engine-specific config
    "BRAVE_DEFAULT_PARAMS": ["engines", BRAVE, "default_params"],
}

# Additional environment variables that map to multiple paths
# Each entry is a tuple of (env_var, list of config paths)
MULTI_PATH_ENV_VARS = [
    (
        "BRAVE_API_KEY",
        [
            ["engines", BRAVE, "api_key"],
            ["engines", BRAVE_NEWS, "api_key"],
        ],
    ),
    (
        "YOU_API_KEY",
        [
            ["engines", YOU, "api_key"],
            ["engines", YOU_NEWS, "api_key"],
        ],
    ),
    (
        "HASDATA_API_KEY",
        [
            ["engines", GOOGLE_HASDATA, "api_key"],
            ["engines", GOOGLE_HASDATA_FULL, "api_key"],
        ],
    ),
]


# Type definitions
class EngineConfig(BaseModel):
    """Configuration for a single search engine."""

    enabled: bool = True
    api_key: str | None = None
    default_params: dict[str, Any] = Field(default_factory=dict)
    engine_code: str | None = None  # Added for reference during validation

    def __init__(self, **data: Any) -> None:
        """
        Initialize the engine configuration with API key from environment variables if needed.

        Args:
            **data: Configuration data
        """
        # Call parent init first
        super().__init__(**data)

        # If no API key is provided but we have an engine code, try to get it from environment variables
        if self.api_key is None and self.engine_code:
            logger.debug(f"No API key provided for {self.engine_code}, checking environment variables")
            try:
                from twat_search.web.engines.base import get_registered_engines

                engine_class = get_registered_engines().get(self.engine_code)
                if engine_class and hasattr(engine_class, "env_api_key_names") and engine_class.env_api_key_names:
                    logger.debug(
                        f"Engine '{self.engine_code}' requires API key from env vars: {engine_class.env_api_key_names}",
                    )
                    # Try to get API key from environment variables
                    for env_var in engine_class.env_api_key_names:
                        env_value = os.environ.get(env_var)
                        logger.debug(f"Checking env var '{env_var}' in __init__: {env_value is not None}")
                        if env_value:
                            logger.debug(f"Using API key from environment variable '{env_var}'")
                            self.api_key = env_value
                            break
            except (ImportError, AttributeError) as e:
                logger.debug(f"Couldn't check API key requirements for {self.engine_code}: {e}")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str | None, info: Any) -> str | None:
        """
        Validate the API key for the engine.

        If the engine requires an API key (has env_api_key_names), ensure it's set.
        This validator runs during config loading, so we don't have the actual
        engine instance yet - we'll do more thorough validation when creating
        engine instances.
        """
        engine_code = info.data.get("engine_code")
        logger.debug(f"Validating API key for engine '{engine_code}', current value: {v is not None}")

        if engine_code and v is None:
            # We have an engine code but no API key - we'll check in the registry
            # if this engine requires an API key
            try:
                from twat_search.web.engines.base import get_registered_engines

                engine_class = get_registered_engines().get(engine_code)
                logger.debug(f"Found engine class for '{engine_code}': {engine_class is not None}")

                # If we found the engine class and it requires an API key,
                # check environment variables
                if engine_class and hasattr(engine_class, "env_api_key_names") and engine_class.env_api_key_names:
                    logger.debug(
                        f"Engine '{engine_code}' requires API key from env vars: {engine_class.env_api_key_names}",
                    )
                    # Try to get API key from environment variables
                    for env_var in engine_class.env_api_key_names:
                        env_value = os.environ.get(env_var)
                        logger.debug(f"Checking env var '{env_var}': {env_value is not None}")
                        if env_value:
                            logger.debug(f"Using API key from environment variable '{env_var}'")
                            return env_value

                    # If we get here, no environment variables were set
                    logger.warning(
                        f"Engine '{engine_code}' may require an API key. "
                        f"Please set one of these environment variables: {', '.join(engine_class.env_api_key_names)}",
                    )
            except (ImportError, AttributeError) as e:
                # Can't access the engine registry yet - this happens during
                # initial import. We'll validate again when creating the engine.
                logger.debug(f"Couldn't check API key requirements for {engine_code}: {e}")

        return v


class Config(BaseModel):
    """Main configuration model for the web search module."""

    engines: dict[str, EngineConfig] = Field(default_factory=dict)
    config_path: ClassVar[str | None] = None

    @classmethod
    def get_config_path(cls) -> Path:
        """
        Determine the configuration file path.

        Checks the following locations in order:
        1. TWAT_SEARCH_CONFIG_PATH environment variable
        2. ~/.twat/search_config.json
        3. ~/.config/twat/search_config.json
        """
        # Get from environment variable if set
        if cls.config_path:
            return Path(cls.config_path)

        env_path = os.environ.get("TWAT_SEARCH_CONFIG_PATH")
        if env_path:
            return Path(env_path)

        # Check ~/.twat/search_config.json
        home_config = Path.home() / ".twat" / "search_config.json"
        if home_config.exists():
            return home_config

        # Check ~/.config/twat/search_config.json
        xdg_config = Path.home() / ".config" / "twat" / "search_config.json"
        if xdg_config.exists():
            return xdg_config

        # Default to ~/.twat/search_config.json (may not exist yet)
        return home_config

    def __init__(self, **data: Any) -> None:
        """
        Initialize configuration with default values and overrides.

        Args:
            **data: Configuration override values
        """
        # Start with default configuration
        config_data = {}

        # Only load default configuration if not in test mode
        if "_TEST_ENGINE" not in os.environ:
            config_data = json.loads(json.dumps(DEFAULT_CONFIG))  # Deep copy

        # Load from config file if it exists
        config_path = self.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    file_config = json.load(f)
                self._merge_config(config_data, file_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")

        # Apply environment variable overrides
        _apply_env_overrides(config_data)

        # Apply explicit overrides
        if data:
            self._merge_config(config_data, data)

        # Initialize with the final configuration
        super().__init__(**config_data)

    def _merge_config(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """
        Recursively merge the source configuration into the target.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value

    def add_engine(
        self,
        engine_name: str,
        enabled: bool = True,
        api_key: str | None = None,
        default_params: dict[str, Any] | None = None,
    ) -> None:
        """
        Add or update an engine configuration.

        Args:
            engine_name: Name of the engine
            enabled: Whether the engine is enabled
            api_key: API key for the engine
            default_params: Default parameters for the engine
        """
        if default_params is None:
            default_params = {}

        if engine_name in self.engines:
            # Update existing engine config
            engine_config = self.engines[engine_name]
            engine_config.enabled = enabled
            if api_key is not None:
                engine_config.api_key = api_key
            engine_config.default_params.update(default_params)
        else:
            # Create new engine config
            self.engines[engine_name] = EngineConfig(
                enabled=enabled,
                api_key=api_key,
                default_params=default_params,
                engine_code=engine_name,
            )


def _apply_env_overrides(config_data: dict[str, Any]) -> None:
    """
    Apply overrides from environment variables to the configuration.

    Args:
        config_data: Configuration data to update
    """
    # Process simple mappings
    for env_var, config_path in ENV_VAR_MAP.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Handle special cases for boolean/numeric values
            value = _parse_env_value(env_value)

            # Apply the value to the config
            if isinstance(config_path, str):
                # Top-level key
                config_data[config_path] = value
            else:
                # Nested path
                _set_nested_value(config_data, config_path, value)

    # Process multi-path mappings
    for env_var, paths in MULTI_PATH_ENV_VARS:
        env_value = os.environ.get(env_var)
        if env_value is not None:
            value = _parse_env_value(env_value)
            for path in paths:
                _set_nested_value(config_data, path, value)


def _parse_env_value(env_value: str) -> Any:
    """Parse environment variable value with type conversion."""
    # Try to parse as JSON first (for default_params and other complex values)
    if env_value.startswith("{") and env_value.endswith("}"):
        try:
            return json.loads(env_value)
        except json.JSONDecodeError:
            # Not valid JSON, continue with other parsing methods
            pass

    if env_value.lower() in ("true", "yes", "1"):
        return True
    if env_value.lower() in ("false", "no", "0"):
        return False
    if env_value.isdigit():
        return int(env_value)
    if env_value.replace(".", "", 1).isdigit():
        return float(env_value)
    return env_value


def _set_nested_value(config_data: dict[str, Any], path: list[str], value: Any) -> None:
    """
    Set a value in a nested dictionary structure.

    Args:
        config_data: The dictionary to update
        path: List of keys forming the path to the target
        value: The value to set
    """
    current = config_data
    for i, path_part in enumerate(path):
        if i == len(path) - 1:
            current[path_part] = value
        else:
            # Create path if it doesn't exist
            if path_part not in current or not isinstance(current[path_part], dict):
                current[path_part] = {}
            current = current[path_part]
