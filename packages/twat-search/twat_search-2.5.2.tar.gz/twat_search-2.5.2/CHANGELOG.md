---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Enhanced error handling in `init_engine_task` function to prevent failures from affecting other engines
- Improved error messages during engine initialization failures
- Added standardization of engine names for more consistent lookups
- Added wrapper coroutine to handle exceptions during search process
- Added detailed logging for engine initialization and search processes

### Changed
- Updated `search` function to handle the changes to `init_engine_task`
- Improved handling of failed engine initializations with better logging
- Enhanced result processing with more detailed logging
- Modified error handling to provide more descriptive messages

### Fixed
- Fixed linting errors in the codebase:
  - Replaced `os.path.abspath()` with `Path.resolve()` in `google.py`
  - Replaced `os.path.exists()` with `Path.exists()` in `google.py`
  - Replaced insecure usage of the temporary file directory `/tmp` with `tempfile.gettempdir()` in `test_google_falla_debug.py`
  - Replaced `os.path.join()` with `Path` and the `/` operator in `test_google_falla_debug.py`
  - Removed unused imports (`os` and `NavigableString`) from `google.py`

## [0.1.2] - 2025-03-04

### Fixed
- Fixed linting errors in the codebase:
  - Replaced `os.path.abspath()` with `Path.resolve()` in `google.py`
  - Replaced `os.path.exists()` with `Path.exists()` in `google.py`
  - Replaced insecure usage of the temporary file directory `/tmp` with `tempfile.gettempdir()` in `test_google_falla_debug.py`
  - Replaced `os.path.join()` with `Path` and the `/` operator in `test_google_falla_debug.py`
  - Removed unused imports (`os` and `NavigableString`) from `google.py`

## [0.1.1] - 2025-03-03

### Added
- Added support for Falla-based search engines
- Created new module `src/twat_search/web/engines/falla.py`
- Added necessary dependencies to `pyproject.toml`
- Defined engine constants in `src/twat_search/web/engine_constants.py`
- Updated `src/twat_search/web/engines/__init__.py` to import and register new engines
- Created utility function to check if Falla is installed and accessible

### Changed
- Refactored search engine initialization for better error handling
- Updated result processing for more consistent output

## [0.1.0] - 2025-03-01

### Added
- Initial release of the Twat Search package
- Support for multiple search engines including Brave, Google, Tavily, Perplexity, You.com, and Bing
- Asynchronous search capabilities
- Command-line interface for searching and exploring engine configurations
- Flexible configuration options via environment variables, `.env` files, or directly in code
- Strong typing and Pydantic validation
- Custom exception classes for error handling

### Changed

- Updated the `config.py` file to correctly import BaseSettings from the pydantic-settings package.
- Updated the `pyproject.toml` file to add pydantic-settings as a dependency.
- Updated the example usage in `example.py`.
- Completed the implementation of the web search functionality as specified in TODO.md.
- Planned comprehensive tests for the package.

### 2025-02-25 - Initial Development

- Created initial project structure and files.
- Created a preliminary TODO.md, PROGRESS.md, and research.txt.

---
