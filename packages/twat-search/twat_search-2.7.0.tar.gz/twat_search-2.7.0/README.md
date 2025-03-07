---
this_file: README.md
---

# Twat Search

A multi-engine web search aggregator that provides a unified interface for searching across various search engines.

## Features

- **Multi-engine search**: Search across various providers including Brave, Google (via SerpAPI), Bing, and more
- **Asynchronous operation**: Uses `asyncio` for efficient concurrent searches
- **Rate limiting**: Built-in rate limiting to prevent API throttling
- **Strong typing**: Pydantic validation for all data models
- **Robust error handling**: Graceful handling of engine failures and empty engine lists
- **Flexible configuration**: Configure via environment variables, `.env` files, or directly in code
- **CLI interface**: Interactive command-line interface with rich output formatting
- **JSON output**: Standardized JSON output format for all search results
- **Modern path handling**: Uses `pathlib` for cross-platform path operations
- **Secure temp files**: Uses `tempfile` for secure temporary file operations

## Recent Improvements

- Enhanced error handling for search engines, including proper handling of empty engine lists
- Standardized engine names for more consistent lookups
- Detailed logging for search engine initialization and execution
- Improved environment variable handling for engine configuration
- Fixed issues with mock engine result count handling
- Added proper JSON string parsing for engine default parameters
- Fixed error handling in `get_engine` function to use the correct exception type
- Improved handling of engine-specific parameters in the search function
- Enhanced configuration system with better environment variable support

## Installation

```bash
pip install twat-search
```

## Usage

### Basic Usage

```python
import asyncio
from twat_search.web.api import search

async def main():
    results = await search("Python programming", engines=["brave", "google"])
    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Description: {result.description}")
        print("---")

asyncio.run(main())
```

### Configuration

You can configure the search engines using environment variables:

```bash
# Enable/disable engines
export BRAVE_ENABLED=true
export GOOGLE_ENABLED=false

# Set API keys
export SERPAPI_API_KEY=your_api_key
export TAVILY_API_KEY=your_api_key

# Configure engine parameters
export BRAVE_DEFAULT_PARAMS='{"count": 10, "country": "US"}'
```

Or directly in code:

```python
from twat_search.web.config import Config

config = Config(
    brave={"enabled": True, "default_params": {"count": 10}},
    google={"enabled": False}
)
```

### Command Line Interface

```bash
# Basic search
twat-search web q "Python programming"

# Specify engines
twat-search web q "Python programming" --engines brave,google

# Get JSON output
twat-search web q "Python programming" --json

# List available engines
twat-search web info --plain
```

## Error Handling

The package provides robust error handling with custom exception classes:

- `SearchError`: Base exception for all search-related errors
- `EngineError`: Raised when there's an issue with a specific engine

Example:

```python
from twat_search.web.api import search
from twat_search.web.exceptions import SearchError, EngineError

try:
    results = await search("Python programming")
except EngineError as e:
    print(f"Engine error: {e}")
except SearchError as e:
    print(f"Search error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Documentation

The project maintains several key documentation files:

- **README.md**: This file, containing an overview of the project, installation instructions, and usage examples.
- **CHANGELOG.md**: Documents all notable changes to the project, organized by version.
- **TODO.md**: Contains a prioritized list of tasks and improvements planned for the project.
- **LICENSE**: The project's license information.

## Development Workflow

When contributing to this project, please follow these guidelines:

1. Check the **TODO.md** file for prioritized tasks that need attention.
2. Run `./cleanup.py status` regularly to check for linting errors and test failures.
3. Document all changes in **CHANGELOG.md** under the appropriate version section.
4. Add comprehensive tests for new features and bug fixes.
5. Ensure all code passes linting and type checking before submitting.

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Ruff**: For linting and formatting Python code
- **Mypy**: For static type checking
- **Pytest**: For running tests
- **Pre-commit hooks**: To ensure code quality before commits

Run these tools regularly during development:

```bash
# Format code
ruff format --respect-gitignore --target-version py312 .

# Lint code
ruff check --output-format=github --fix --unsafe-fixes .

# Run tests
python -m pytest
```

## Quick start guide

### Python API

```python
import asyncio
from twat_search.web import search

async def main():
    # Search across all configured engines
    results = await search("quantum computing applications")

    # Print results
    for result in results:
        print(f"[{result.source}] {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}\n")

# Run the async function
asyncio.run(main())
```

### Command line interface

```bash
# Search using all available engines
twat-search web q "climate change solutions"

# Search with specific engines
twat-search web q "machine learning frameworks" -e brave,tavily

# Get json output
twat-search web q "renewable energy" --json

# Use engine-specific command
twat-search web q -e brave "web development trends" --count 10
```

## Core architecture

### Module structure

```
twat_search/
└── web/
    ├── engines/            # Individual search engine implementations
    │   ├── __init__.py     # Engine registration and availability checks
    │   ├── base.py         # Base SearchEngine class definition
    │   ├── brave.py        # Brave search implementation
    │   ├── bing_scraper.py # Bing scraper implementation
    │   └── ...             # Other engine implementations
    │   └── lib_falla/      # Falla-based search engine implementations
    │       ├── core/       # Core Falla functionality
    │       │   ├── falla.py    # Base Falla class
    │       │   ├── google.py   # Google search implementation
    │       │   └── ...         # Other Falla-based implementations
    ├── __init__.py         # Module exports
    ├── api.py              # Main search API
    ├── cli.py              # Command-line interface
    ├── config.py           # Configuration handling
    ├── exceptions.py       # Custom exceptions
    ├── models.py           # Data models
    └── utils.py            # Utility functions
```

## Supported search engines

Twat Search provides a consistent interface to the following search engines:

| Engine | Module | API Key Required | Description | Package Extra |
| --- | --- | --- | --- | --- |
| Brave | `brave` | Yes | Web search via Brave Search API | `brave` |
| Brave News | `brave_news` | Yes | News search via Brave API | `brave` |
| You.com | `you` | Yes | Web search via You.com API | - |
| You.com News | `you_news` | Yes | News search via You.com API | - |
| Tavily | `tavily` | Yes | Research-focused search API | `tavily` |
| Perplexity | `pplx` | Yes | AI-powered search with detailed answers | `pplx` |
| SerpAPI | `serpapi` | Yes | Google search results via SerpAPI | `serpapi` |
| HasData Google | `hasdata-google` | Yes | Google search results via HasData API | `hasdata` |
| HasData Google Light | `hasdata-google-light` | Yes | Light version of HasData API | `hasdata` |
| Critique | `critique` | Yes | Visual and textual search capabilities | - |
| DuckDuckGo | `duckduckgo` | No | Privacy-focused search results | `duckduckgo` |
| Bing Scraper | `bing_scraper` | No | Web scraping of Bing search results | `bing_scraper` |
| Google Falla | `google_falla` | No | Google search via Playwright-based scraping | `falla` |

## Configuration management

### Environment variables

Configure engines using environment variables:

```bash
# Api keys
BRAVE_API_KEY=your_brave_api_key
TAVILY_API_KEY=your_tavily_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
YOU_API_KEY=your_you_api_key
SERPAPI_API_KEY=your_serpapi_api_key
CRITIQUE_API_KEY=your_critique_api_key
HASDATA_API_KEY=your_hasdata_api_key

# Engine enablement
BRAVE_ENABLED=true
TAVILY_ENABLED=true
PERPLEXITY_ENABLED=true
YOU_ENABLED=true
SERPAPI_ENABLED=true
CRITIQUE_ENABLED=true
DUCKDUCKGO_ENABLED=true
BING_SCRAPER_ENABLED=true
HASDATA_GOOGLE_ENABLED=true

# Default parameters (json format)
BRAVE_DEFAULT_PARAMS='{"count": 10, "safesearch": "off"}'
TAVILY_DEFAULT_PARAMS='{"max_results": 5, "search_depth": "basic"}'
PERPLEXITY_DEFAULT_PARAMS='{"model": "pplx-7b-online"}'
YOU_DEFAULT_PARAMS='{"safe_search": true, "count": 8}'
SERPAPI_DEFAULT_PARAMS='{"num": 10, "gl": "us"}'
HASDATA_GOOGLE_DEFAULT_PARAMS='{"location": "Austin,Texas,United States", "device_type": "desktop"}'
DUCKDUCKGO_DEFAULT_PARAMS='{"max_results": 10, "safesearch": "moderate", "time": "d"}'
BING_SCRAPER_DEFAULT_PARAMS='{"max_retries": 3, "delay_between_requests": 1.0}'

# Global default for all engines
NUM_RESULTS=5
```

You can store these in a `.env` file in your project directory, which will be automatically loaded by the library using `python-dotenv`.

### Programmatic configuration

Configure engines programmatically when using the Python API:

```python
from twat_search.web import Config, EngineConfig, search

# Create custom configuration
config = Config(
    engines={
        "brave": EngineConfig(
            api_key="your_brave_api_key",
            enabled=True,
            default_params={"count": 10, "country": "US"}
        ),
        "bing_scraper": EngineConfig(
            enabled=True,
            default_params={"max_retries": 3, "delay_between_requests": 1.0}
        ),
        "tavily": EngineConfig(
            api_key="your_tavily_api_key",
            enabled=True,
            default_params={"search_depth": "advanced"}
        )
    }
)

# Use the configuration
results = await search("quantum computing", config=config)
```

## Error Handling Framework

Twat Search provides a robust error handling framework to ensure graceful failure and clear error messages:

### Exception Hierarchy

- `SearchError`: Base exception for all search-related errors
- `EngineError`: Specific exception for engine-related issues

### Key Error Handling Features

- **Empty Engine List Detection**: The search function now checks for empty engine lists and raises a clear error
- **Standardized Error Messages**: All error messages follow a consistent format for better debugging
- **Detailed Logging**: Comprehensive logging throughout the search process
- **Graceful Engine Failures**: Individual engine failures don't crash the entire search process
- **Environment Variable Validation**: Proper parsing and validation of environment variables

### Example Error Scenarios

```python
# No engines configured
try:
    results = await search("query", engines=[])
except SearchError as e:
    print(e)  # "No search engines specified or available"

# Non-existent engine
try:
    results = await search("query", engines=["nonexistent_engine"])
except SearchError as e:
    print(e)  # "Engine 'nonexistent_engine': not found"

# Disabled engine
try:
    results = await search("query", engines=["disabled_engine"])
except SearchError as e:
    print(e)  # "Engine 'disabled_engine': is disabled"
```

## Recent Fixes and Improvements

The latest version includes several important fixes and improvements:

1. **Fixed Environment Variable Parsing**: Properly handles JSON strings in environment variables for engine default parameters
2. **Empty Engine List Handling**: Added explicit check and error for empty engine lists
3. **Mock Engine Parameter Handling**: Improved handling of mock engine parameters for testing
4. **Standardized Error Messages**: Enhanced error messages for better debugging
5. **Config Class Improvements**: Modified to properly check for test environment variables
6. **Enhanced Logging**: Added detailed logging throughout the search process
7. **Improved Exception Handling**: Better handling of exceptions during engine initialization and search

These improvements make the package more robust, easier to debug, and more reliable in various usage scenarios.

## Development Status

The project is actively maintained and regularly updated. All unit tests are passing, and the codebase is continuously improved based on user feedback and identified issues.

Current focus areas include:
- Fixing Falla-based search engines
- Addressing type errors in the codebase
- Improving integration with Playwright
- Enhancing documentation and standardizing JSON output formats

For a complete list of planned improvements, see the TODO.md file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Appendix: available engines and requirements

| Engine | Package Extra | API Key Required | Environment Variable | Notes |
| --- | --- | --- | --- | --- |
| Brave | `brave` | Yes | `BRAVE_API_KEY` | General web search engine |
| Brave News | `brave` | Yes | `BRAVE_API_KEY` | News-specific search |
| You.com | - | Yes | `YOU_API_KEY` | AI-powered web search |
| You.com News | - | Yes | `YOU_API_KEY` | News-specific search |
| Tavily | `tavily` | Yes | `TAVILY_API_KEY` | Research-focused search |
| Perplexity | `pplx` | Yes | `PPLX_API_KEY` | AI-powered search with detailed answers |
| SerpAPI | `serpapi` | Yes | `SERPAPI_API_KEY` | Google search results API |
| HasData Google | `hasdata` | Yes | `HASDATA_API_KEY` | Google search results API |
| HasData Google Light | `hasdata` | Yes | `HASDATA_API_KEY` | Lightweight Google search API |
| Critique | - | Yes | `CRITIQUE_API_KEY` | Supports image analysis |
| DuckDuckGo | `duckduckgo` | No | - | Privacy-focused search |
| Bing Scraper | `bing_scraper` | No | - | Uses web scraping techniques |
