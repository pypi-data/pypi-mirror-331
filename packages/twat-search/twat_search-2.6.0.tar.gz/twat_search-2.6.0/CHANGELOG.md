---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

## Unreleased Changes

### Added
- Added error handling in `init_engine_task` to prevent task cancellation issues
- Improved error messages for better debugging
- Added detailed logging for search engine initialization and execution
- Added check for empty engines list in `search` function, raising a `SearchError` with appropriate message
- Added proper handling of mock engine parameters, ensuring correct result count

### Changed
- Enhanced error handling in `get_engine` function to raise `SearchError` with correct message
- Improved mock engine handling in `search` function to properly set `result_count`
- Modified `Config` class to check for `_TEST_ENGINE` environment variable
- Enhanced `_parse_env_value` function to handle JSON strings for engine default parameters
- Added `BRAVE_DEFAULT_PARAMS` to `ENV_VAR_MAP` for proper configuration
- Standardized engine names for more consistent lookups
- Improved error handling patterns across the codebase

### Fixed
- Fixed issue with environment variable parsing for engine default parameters
- Fixed handling of empty engines list in search function
- Fixed mock engine result count handling
- Fixed error handling in `get_engine` function to use the correct exception type
- Fixed environment variable application to engine configurations

## 0.1.2 (2024-05-15)

### Fixed
- Fixed linting errors in `google.py` and `test_google_falla_debug.py`
- Replaced insecure usage of temporary file directory `/tmp` with `tempfile.gettempdir()`
- Replaced `os.path` functions with `pathlib.Path` methods for better path handling
- Removed unused imports (`os` and `NavigableString`) from `google.py`

## 0.1.1 (2024-05-10)

### Added
- Added support for Falla-based search engines
- Added refactored search engine initialization
- Added wrapper coroutine to handle exceptions during search process
- Added detailed logging for engine initialization and search processes

### Changed
- Improved error handling for search engines
- Enhanced configuration system
- Standardized engine names for more consistent lookups

## 0.1.0 (2024-05-01)

### Added
- Initial release
- Support for multiple search engines
- Asynchronous search capabilities
- Rate limiting
- Strong typing with Pydantic validation

### Changed
- Updated the `config.py` file to correctly import BaseSettings from the pydantic-settings package
- Updated the `pyproject.toml` file to add pydantic-settings as a dependency
- Updated the example usage in `example.py`
- Completed the implementation of the web search functionality as specified in TODO.md
- Planned comprehensive tests for the package

### 2024-02-25 - Initial Development

- Created initial project structure and files
- Created a preliminary TODO.md, PROGRESS.md, and research.txt

---
