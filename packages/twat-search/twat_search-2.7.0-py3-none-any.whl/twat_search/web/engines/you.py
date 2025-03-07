from __future__ import annotations

import logging
from typing import Any, ClassVar

from pydantic import BaseModel, Field, HttpUrl, ValidationError

from twat_search.web.config import EngineConfig
from twat_search.web.engine_constants import DEFAULT_NUM_RESULTS
from twat_search.web.engines import ENGINE_FRIENDLY_NAMES, YOU, YOU_NEWS
from twat_search.web.engines.base import SearchEngine, register_engine
from twat_search.web.exceptions import EngineError
from twat_search.web.models import SearchResult

# Initialize logger
logger = logging.getLogger(__name__)


class YouSearchHit(BaseModel):
    title: str
    url: HttpUrl
    snippet: str = Field(alias="description")


class YouSearchResponse(BaseModel):
    hits: list[YouSearchHit]
    search_id: str | None = Field(None, alias="searchId")


class YouNewsArticle(BaseModel):
    title: str
    url: HttpUrl
    snippet: str = Field(alias="description")
    source: str | None = None
    published_date: str | None = None


class YouNewsResponse(BaseModel):
    articles: list[YouNewsArticle]
    search_id: str | None = Field(None, alias="searchId")


class YouBaseEngine(SearchEngine):
    """Base class for You.com search engines, handling common API interaction logic."""

    env_api_key_names: ClassVar[list[str]] = ["YOUCOM_API_KEY", "YOU_API_KEY"]
    base_url: str = ""  # Will be overridden by subclasses
    num_results_param: str = ""  # Will be overridden by subclasses

    def __init__(
        self,
        config: EngineConfig,
        **kwargs: Any,
    ) -> None:
        """Initialize the base engine with common parameters."""
        super().__init__(config, **kwargs)

        # Set up API headers using the api_key from base class
        self.headers = {
            "X-API-Key": self.api_key if self.api_key is not None else "",
            "Accept": "application/json",
        }

        # Get country code
        self.country_code = kwargs.get("country") or self.config.default_params.get(
            "country_code",
            None,
        )

    async def _make_api_call(self, query: str) -> Any:
        """Handle the common API call logic."""
        params: dict[str, Any] = {
            "query": query,
            self.num_results_param: self.max_results,
        }

        if self.country_code:
            params["country_code"] = self.country_code
        if self.safe_search is not None:
            params["safesearch"] = str(self.safe_search).lower()

        logger.debug(f"Making You.com API request to {self.base_url} with params: {params}")

        try:
            response = await self.make_http_request(
                url=self.base_url,
                method="GET",
                headers=self.headers,
                params=params,
            )
            return response.json()
        except EngineError as e:
            raise EngineError(self.engine_code, f"API request failed: {str(e)!s}")
        except Exception as e:
            raise EngineError(self.engine_code, f"Unexpected error: {str(e)!s}")


@register_engine
class YouSearchEngine(YouBaseEngine):
    """Implementation of the You.com Web Search API."""

    engine_code = YOU
    friendly_engine_name = ENGINE_FRIENDLY_NAMES[YOU]
    # base_url = "https://chat-api.you.com/search"
    base_url = "https://api.ydc-index.io/search"
    num_results_param = "num_web_results"

    async def search(self, query: str) -> list[SearchResult]:
        """Perform a web search using the You.com Search API."""
        if not query:
            raise EngineError(self.engine_code, "Search query cannot be empty")

        data = await self._make_api_call(query)
        try:
            you_response = YouSearchResponse(**data)
            results = []
            for hit in you_response.hits:
                try:
                    results.append(
                        SearchResult(
                            title=hit.title,
                            url=hit.url,
                            snippet=hit.snippet,
                            source=self.engine_code,
                            raw=hit.model_dump(by_alias=True),
                        ),
                    )
                    # Respect num_results limit
                    if len(results) >= self.max_results:
                        break
                except ValidationError as e:
                    logger.warning(f"Invalid result from You.com: {e}")
                    continue
            return self.limit_results(results)
        except ValidationError as exc:
            raise EngineError(
                self.engine_code,
                f"Response parsing error: {exc}",
            ) from exc


@register_engine
class YouNewsSearchEngine(YouBaseEngine):
    """Implementation of the You.com News Search API."""

    engine_code = YOU_NEWS
    friendly_engine_name = ENGINE_FRIENDLY_NAMES[YOU_NEWS]
    base_url = "https://chat-api.you.com/news"
    num_results_param = "num_news_results"

    async def search(self, query: str) -> list[SearchResult]:
        """Perform a news search using the You.com News API."""
        if not query:
            raise EngineError(self.engine_code, "Search query cannot be empty")

        data = await self._make_api_call(query)
        try:
            you_response = YouNewsResponse(**data)
            results = []
            for article in you_response.articles:
                try:
                    snippet = article.snippet
                    if article.source and article.published_date:
                        snippet = f"{snippet} - {article.source} ({article.published_date})"
                    elif article.source:
                        snippet = f"{snippet} - {article.source}"
                    results.append(
                        SearchResult(
                            title=article.title,
                            url=article.url,
                            snippet=snippet,
                            source=self.engine_code,
                            raw=article.model_dump(by_alias=True),
                        ),
                    )
                    # Respect num_results limit
                    if len(results) >= self.max_results:
                        break
                except ValidationError as e:
                    logger.warning(f"Invalid news result from You.com: {e}")
                    continue
            return self.limit_results(results)
        except ValidationError as exc:
            raise EngineError(
                self.engine_code,
                f"Response parsing error: {exc}",
            ) from exc


async def you(
    query: str,
    num_results: int = DEFAULT_NUM_RESULTS,
    country: str | None = None,
    language: str | None = None,
    safe_search: bool | None = True,
    time_frame: str | None = None,
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    Search the web using You.com.

    Args:
        query: The search query
        num_results: Maximum number of results to return
        country: Country code (e.g., "us", "gb")
        language: Language code (e.g., "en", "es")
        safe_search: Whether to filter adult content
        time_frame: Time frame for results (e.g., "day", "week", "month")
        api_key: You.com API key (if not set via environment variable)

    Returns:
        List of search results
    """
    config = EngineConfig(
        api_key=api_key,
        enabled=True,
        engine_code=YOU,
    )

    engine = YouSearchEngine(
        config,
        num_results=num_results,
        country=country,
        language=language,
        safe_search=safe_search,
        time_frame=time_frame,
    )

    return await engine.search(query)


async def you_news(
    query: str,
    num_results: int = DEFAULT_NUM_RESULTS,
    country: str | None = None,
    language: str | None = None,
    safe_search: bool | None = True,
    time_frame: str | None = None,
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    Search news articles using You.com News.

    Args:
        query: The search query
        num_results: Maximum number of results to return
        country: Country code (e.g., "us", "gb")
        language: Language code (e.g., "en", "es")
        safe_search: Whether to filter adult content
        time_frame: Time frame for news (e.g., "day", "week", "month")
        api_key: You.com API key (if not set via environment variable)

    Returns:
        List of search results
    """
    config = EngineConfig(
        api_key=api_key,
        enabled=True,
        engine_code=YOU_NEWS,
    )

    engine = YouNewsSearchEngine(
        config,
        num_results=num_results,
        country=country,
        language=language,
        safe_search=safe_search,
        time_frame=time_frame,
    )

    return await engine.search(query)
