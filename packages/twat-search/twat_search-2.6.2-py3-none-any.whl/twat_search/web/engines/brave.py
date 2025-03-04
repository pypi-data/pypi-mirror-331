from __future__ import annotations

from typing import Any, ClassVar

import httpx
from pydantic import BaseModel, HttpUrl, ValidationError
from twat_cache import ucache

from twat_search.web.config import EngineConfig
from twat_search.web.engine_constants import DEFAULT_NUM_RESULTS
from twat_search.web.engines import BRAVE, BRAVE_NEWS, ENGINE_FRIENDLY_NAMES
from twat_search.web.engines.base import SearchEngine, register_engine
from twat_search.web.exceptions import EngineError
from twat_search.web.models import SearchResult


# Pydantic models for individual results
class BraveResult(BaseModel):
    title: str
    url: HttpUrl
    description: str


class BraveNewsResult(BaseModel):
    title: str
    url: HttpUrl
    description: str
    published_time: str | None = None
    publisher: str | None = None


# Base class that encapsulates common functionality for both search and news engines.
class BaseBraveEngine(SearchEngine):
    env_api_key_names: ClassVar[list[str]] = ["BRAVE_API_KEY"]
    base_url: str  # Must be defined by subclass.
    response_key: str  # "web" for normal search, "news" for news search.
    result_model: type[BaseModel]  # Either BraveResult or BraveNewsResult.

    def __init__(
        self,
        config: EngineConfig,
        num_results: int = DEFAULT_NUM_RESULTS,
        country: str | None = None,
        language: str | None = None,
        safe_search: bool = False,
        time_frame: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Brave Search engine."""
        super().__init__(
            config=config,
            num_results=num_results,
            country=country,
            language=language,
            safe_search=safe_search,
            time_frame=time_frame,
            **kwargs,
        )
        # Maximum allowed results from Brave Search API is 20
        self.max_brave_results = 20

        # Initialize the language attributes
        self.search_lang = language
        self.ui_lang = language
        # Initialize the freshness attribute from time_frame
        self.freshness = time_frame

        if not self.config.api_key:
            raise EngineError(self.engine_code, "API key is required")
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.config.api_key,
        }

    @ucache(maxsize=500, ttl=3600)  # Cache 500 searches for 1 hour
    async def search(self, query: str) -> list[SearchResult]:
        # Request at most 20 (API limit), respect the requested number exactly
        count_param = min(self.max_brave_results, self.num_results)
        params: dict[str, Any] = {"q": query, "count": count_param}
        if self.country:
            params["country"] = self.country
        if self.search_lang:
            params["search_lang"] = self.search_lang
        if self.ui_lang:
            params["ui_lang"] = self.ui_lang
        if self.freshness:
            params["freshness"] = self.freshness
        if self.safe_search is not None:
            params["safe_search"] = str(self.safe_search).lower()

        # Add debug logging to see the exact params we're sending

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()
                results = []
                section = data.get(self.response_key, {})
                if section.get("results"):
                    for result in section["results"]:
                        try:
                            parsed = self.result_model(**result)
                            results.append(self.convert_result(parsed, result))

                            # Break early if we've hit the requested number of results
                            if len(results) >= self.num_results:
                                break
                        except ValidationError:
                            continue
                # Apply limit_results to ensure we respect num_results
                return self.limit_results(results)

            except httpx.RequestError as exc:
                raise EngineError(
                    self.engine_code,
                    f"HTTP Request failed: {exc}",
                ) from exc
            except httpx.HTTPStatusError as exc:
                raise EngineError(
                    self.engine_code,
                    f"HTTP Status error: {exc.response.status_code} - {exc.response.text}",
                ) from exc
            except ValidationError as exc:
                raise EngineError(
                    self.engine_code,
                    f"Response parsing error: {exc}",
                ) from exc

    def convert_result(self, parsed: BaseModel, raw: dict[str, Any]) -> SearchResult:
        snippet = getattr(parsed, "description", "")
        # For news results, append publisher and published_time information if available.
        if self.response_key == "news":
            publisher = getattr(parsed, "publisher", None)
            published_time = getattr(parsed, "published_time", None)
            if publisher and published_time:
                snippet = f"{snippet} - {publisher} ({published_time})"
            elif publisher:
                snippet = f"{snippet} - {publisher}"

        # Use getattr to safely access properties, but ensure we have a valid HttpUrl for the URL
        # The URL should already be a HttpUrl since the model validation would have ensured this
        url = getattr(parsed, "url", None)
        if not url:
            # Fallback to prevent errors
            from pydantic import HttpUrl

            url = HttpUrl("https://brave.com")

        return SearchResult(
            title=getattr(parsed, "title", ""),
            url=url,
            snippet=snippet,
            source=self.engine_code,
            raw=raw,
        )

    async def _make_api_call(self, query: str) -> dict[str, Any]:
        """Make API call to Brave Search API."""
        if not query:
            raise EngineError(self.engine_code, "Search query cannot be empty")

        url = self.base_url
        params = {
            "q": query,
            "count": min(
                self.max_brave_results,
                self.num_results,
            ),  # Use API limit or requested number, whichever is smaller
            "country": self.country or "US",
            "safe_search": "strict" if self.safe_search else "off",
        }

        # Add debug logging to see what count is being used in the API call

        if hasattr(self, "freshness") and self.freshness:
            params["freshness"] = self.freshness

        # Ensure headers are correctly typed as dict[str, str]
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.config.api_key or "",
        }

        response = await self.make_http_request(
            url=url,
            method="GET",
            params=params,
            headers=headers,
        )

        try:
            # Explicitly cast the JSON response to dict[str, Any]
            data: dict[str, Any] = response.json()
            return data
        except Exception as e:
            raise EngineError(
                self.engine_code,
                f"Failed to parse response from Brave Search API: {e}",
            ) from e

    def limit_results(self, results: list[SearchResult]) -> list[SearchResult]:
        """
        Override base limit_results method to ensure we respect the user's requested number of results.

        Args:
            results: The list of search results to limit

        Returns:
            A limited list of results based on the desired number of results
        """
        if not results:
            return results

        # Add debug logging

        # Use the num_results value directly
        return results[: self.num_results]


@register_engine
class BraveSearchEngine(BaseBraveEngine):
    """Implementation of the Brave Search API for web search."""

    engine_code = BRAVE
    friendly_engine_name = ENGINE_FRIENDLY_NAMES[BRAVE]
    base_url = "https://api.search.brave.com/res/v1/web/search"
    response_key = "web"
    result_model = BraveResult

    async def search(self, query: str) -> list[SearchResult]:
        """Perform a web search using Brave Search API."""
        data = await self._make_api_call(query)

        # Add debug logging of raw API response for debugging

        results = []
        try:
            web_result = data.get("web", {})
            items = web_result.get("results", [])

            # Add debug for items extracted

            for _idx, item in enumerate(items, start=1):
                title = item.get("title", "")
                url = item.get("url", "")
                description = item.get("description", "")

                if not (title and url):
                    continue

                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=description,
                        source=self.engine_code,
                        raw=item,
                    ),
                )

                # Break early if we've hit the requested number of results
                if len(results) >= self.num_results:
                    break

            # Use the limit_results method to enforce num_results
            return self.limit_results(results)
        except Exception as e:
            raise EngineError(
                self.engine_code,
                f"Failed to process results from Brave Search API: {e}",
            ) from e


@register_engine
class BraveNewsSearchEngine(BaseBraveEngine):
    """Implementation of the Brave Search API for news search."""

    engine_code = BRAVE_NEWS
    friendly_engine_name = ENGINE_FRIENDLY_NAMES[BRAVE_NEWS]
    base_url = "https://api.search.brave.com/res/v1/news/search"
    response_key = "news"
    result_model = BraveNewsResult
    freshness = "last7days"  # Default to news from the last 7 days

    async def search(self, query: str) -> list[SearchResult]:
        """Perform a news search using Brave Search API."""
        data = await self._make_api_call(query)

        # Add debug logging of raw API response

        results = []
        try:
            # FIX: News results are in the top-level 'results' key, not in 'news.results'
            # Before: news_results = data.get("news", {})
            # items = news_results.get("results", [])

            # Directly access the top-level 'results' array
            items = data.get("results", [])

            # Add debug for items extracted

            for _idx, item in enumerate(items, start=1):
                title = item.get("title", "")
                url = item.get("url", "")
                description = item.get("description", "")

                if not (title and url):
                    continue

                # Add source and age to snippet if available
                if item.get("age") or item.get("source", {}).get("name"):
                    source_name = item.get("source", {}).get("name", "")
                    age = item.get("age", "")
                    if source_name and age:
                        description = f"{description} - {source_name} ({age})"
                    elif source_name:
                        description = f"{description} - {source_name}"
                # If no source name but we have age, append just the age
                elif item.get("age"):
                    description = f"{description} - {item.get('age')}"

                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=description,
                        source=self.engine_code,
                        raw=item,
                    ),
                )

                # Break early if we've hit the requested number of results
                if len(results) >= self.num_results:
                    break

            # Use the limit_results method to enforce num_results
            return self.limit_results(results)
        except Exception as e:
            raise EngineError(
                self.engine_code,
                f"Failed to process results from Brave News API: {e}",
            ) from e


async def brave(
    query: str,
    num_results: int = DEFAULT_NUM_RESULTS,
    country: str | None = None,
    language: str | None = None,
    safe_search: bool | str | None = True,
    time_frame: str | None = None,
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    Search Brave web search.

    Args:
        query: Search query string
        num_results: Number of results to return (1-20)
        country: Country code (e.g., "US", "GB", "FR")
        language: Language code (e.g., "en", "fr", "de")
        safe_search: Safe search level (True = strict, False = off, or "moderate")
        time_frame: Time filter (e.g., "past_day", "past_week", "past_month")
        api_key: Optional API key (otherwise use environment variable)

    Returns:
        List of search results
    """
    config = EngineConfig(api_key=api_key, enabled=True)

    # Convert safe_search to bool if it's a string or None
    safe_search_bool = safe_search in (True, "strict", "moderate", None)

    engine = BraveSearchEngine(
        config,
        num_results=num_results,
        country=country,
        language=language,
        safe_search=safe_search_bool,
        time_frame=time_frame,
    )
    return await engine.search(query)


async def brave_news(
    query: str,
    num_results: int = DEFAULT_NUM_RESULTS,
    country: str | None = None,
    language: str | None = None,
    safe_search: bool | str | None = True,
    time_frame: str | None = None,
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    Search Brave news.

    Args:
        query: Search query string
        num_results: Number of results to return (1-20)
        country: Country code (e.g., "US", "GB", "FR")
        language: Language code (e.g., "en", "fr", "de")
        safe_search: Safe search level (True = strict, False = off, or "moderate")
        time_frame: Time filter (e.g., "past_hour", "past_day", "past_week")
        api_key: Optional API key (otherwise use environment variable)

    Returns:
        List of search results
    """
    config = EngineConfig(api_key=api_key, enabled=True)

    # Convert safe_search to bool if it's a string or None
    safe_search_bool = safe_search in (True, "strict", "moderate", None)

    engine = BraveNewsSearchEngine(
        config,
        num_results=num_results,
        country=country,
        language=language,
        safe_search=safe_search_bool,
        time_frame=time_frame,
    )
    return await engine.search(query)
