# this_file: src/twat_search/web/models.py
"""
Pydantic models for the web search API.

This module defines the data models used for inputs and outputs
in the web search API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator


class SearchResult(BaseModel):
    """
    Represents a single search result from any search engine.

    Attributes:
        title: The title of the search result.
        url: The URL of the search result.
        snippet: A short excerpt or description of the search result.
        source: The name of the search engine that produced this result.
        rank: Optional ranking position (for future ranking functionality).
        raw: The raw, unparsed response from the search engine (for debugging).
    """

    title: str
    url: HttpUrl  # Use Pydantic's HttpUrl for URL validation
    snippet: str
    source: str
    rank: int | None = None  # For future ranking functionality
    raw: dict[str, Any] | None = None  # Store the raw API response

    @field_validator("source")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that source field is not empty."""
        if not v or not v.strip():
            msg = "Source field cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("title", "snippet")
    @classmethod
    def ensure_string(cls, v: str) -> str:
        """Ensure string fields are not None and convert to empty string if None."""
        return v.strip() if v and v.strip() else ""
