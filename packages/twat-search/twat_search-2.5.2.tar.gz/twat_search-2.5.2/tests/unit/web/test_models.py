#!/usr/bin/env python
# this_file: tests/unit/web/test_models.py
"""
Unit tests for the twat_search.web.models module.

This module tests the data models used in the web search API,
particularly the SearchResult model and its validation.
"""

from __future__ import annotations

import pytest
from pydantic import HttpUrl, ValidationError

from twat_search.web.models import SearchResult


def test_search_result_valid_data() -> None:
    """Test creating a SearchResult with valid data."""
    # Convert string to HttpUrl using Pydantic's model validation
    url = HttpUrl("https://example.com")
    result = SearchResult(
        title="Test Result",
        url=url,
        snippet="This is a test result",
        source="test_engine",
    )

    assert result.title == "Test Result"
    assert str(result.url) == "https://example.com/"
    assert result.snippet == "This is a test result"
    assert result.source == "test_engine"
    assert result.rank is None
    assert result.raw is None


def test_search_result_with_optional_fields() -> None:
    """Test creating a SearchResult with all fields."""
    raw_data = {"key": "value"}
    url = HttpUrl("https://example.com")
    result = SearchResult(
        title="Test Result",
        url=url,
        snippet="This is a test result",
        source="test_engine",
        rank=1,
        raw=raw_data,
    )

    assert result.rank == 1
    assert result.raw == raw_data


def test_search_result_invalid_url() -> None:
    """Test that invalid URLs raise validation errors."""
    with pytest.raises(ValidationError):
        # This will fail at validation inside SearchResult model
        SearchResult.model_validate(
            {
                "title": "Test Result",
                "url": "not-a-valid-url",  # Invalid URL as string
                "snippet": "This is a test result",
                "source": "test_engine",
            },
        )


def test_search_result_empty_fields() -> None:
    """Test that empty source field raises validation error, but empty title and snippet are allowed."""
    url = HttpUrl("https://example.com")

    # Test empty source (should still raise error)
    with pytest.raises(ValidationError):
        SearchResult(
            title="Test Title",
            url=url,
            snippet="Test snippet",
            source="",  # Empty source should raise error
        )

    # Test empty title and snippet (should be allowed now)
    result = SearchResult(
        title="",
        url=url,
        snippet="",
        source="test_source",
    )
    assert result.title == ""
    assert result.snippet == ""
    assert result.source == "test_source"


def test_search_result_serialization() -> None:
    """Test that SearchResult can be serialized to dict and json."""
    url = HttpUrl("https://example.com")
    result = SearchResult(
        title="Test Result",
        url=url,
        snippet="This is a test result",
        source="test_engine",
        rank=1,
    )

    # Test dict serialization
    result_dict = result.model_dump()
    assert result_dict["title"] == "Test Result"
    # In Pydantic v2, the URL is serialized as a HttpUrl object
    assert str(result_dict["url"]) == "https://example.com/"
    assert result_dict["snippet"] == "This is a test result"
    assert result_dict["source"] == "test_engine"
    assert result_dict["rank"] == 1

    # Test JSON serialization
    result_json = result.model_dump_json()
    assert isinstance(result_json, str)
    assert "Test Result" in result_json
    assert "https://example.com/" in result_json


def test_search_result_deserialization() -> None:
    """Test that SearchResult can be deserialized from dict."""
    data = {
        "title": "Test Result",
        "url": "https://example.com",  # String URL is OK for deserialization
        "snippet": "This is a test result",
        "source": "test_engine",
        "rank": 1,
    }

    result = SearchResult.model_validate(data)
    assert result.title == "Test Result"
    assert str(result.url) == "https://example.com/"
    assert result.snippet == "This is a test result"
    assert result.source == "test_engine"
    assert result.rank == 1
