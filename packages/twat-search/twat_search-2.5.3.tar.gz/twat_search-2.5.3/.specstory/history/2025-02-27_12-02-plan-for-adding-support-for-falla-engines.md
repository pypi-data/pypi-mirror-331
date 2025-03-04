## SpecStory

## Plan for Adding Support for *-falla Engines (27/02/2025, 12:02:35)

_**User**_

Analyze @NEXTENGINES.md and make a detailed plan in @TODO.md that describes specific steps needed to add support and tests for the `*-falla` engines. Then add specific action items to @PROGRESS.md 

---

_**Assistant**_

I'll analyze the NEXTENGINES.md file to understand what's needed for implementing the `*-falla` engines, then create a detailed plan in TODO.md and add specific action items to PROGRESS.md.

Let me first examine the NEXTENGINES.md file more closely to understand what's required.

---

_****_

Read file: NEXTENGINES.md

---

_****_



Let me get more information about the Falla project by examining the GitHub repository.

---

_****_



---

_****_



Let me try to understand the structure of the Falla project by looking at the file tree provided in NEXTENGINES.md.

Based on the information in NEXTENGINES.md, I can see that Falla is a search engine scraper that supports multiple search engines like Google, Bing, DuckDuckGo, etc. The project has a core module with separate Python files for each search engine implementation, all inheriting from a base `Falla` class.

Now, let me update the TODO.md file with a detailed plan for implementing the `*-falla` engines:

---

_****_

```diff
  *   **`@field_validator("api_key", mode="before")`:**  This validator runs *before* the `api_key` field is assigned.  This is crucial because we need to check if the key is required *before* Pydantic's default value logic kicks in.  We use `values.data.get('engine_code')` to safely access the engine code *during* validation, even if it hasn't been fully assigned yet.
  *   **`get_registered_engines()`:** We call the `get_registered_engines()` function to access the registry.
- *   **`KeyError` Handling:** The code now includes a `try...except KeyError` block. This is important.  During the *initial* loading of the configuration, the `EngineConfig` for an engine might be created *before* the engine class itself is registered.  In this case, looking up the engine class in `_engine_registry` would raise a `KeyError`.  The `try...except` handles this gracefully, skipping the API key check if the engine isn't registered yet.  This prevents a chicken-and-egg problem during startup.
+ *   **`KeyError` Handling:** The code now includes a `try...except KeyError` block. This is important.  During the *initial* loading of the configuration, the `EngineConfig` for an engine might be created *before* the engine class itself is registered.  In this case, looking up the engine class in `_engine_registry` would raise a `KeyError`.  The `try...except` handles this gracefully, skipping the API key check if the engine isn't registered yet.
  * **Clear Error Message:**  The `ValueError` now provides a very specific message, telling the user *exactly* which environment variable(s) they need to set.
  * No longer need for the map with environment variables.
  By systematically applying these steps, the code will become more robust, maintainable, and consistent. The detailed plan and code samples will guide you through the refactoring process. Remember to execute `cleanup.py status` regularly and run `pytest` to check for any errors or regressions introduced during the modifications.  Address *all* Ruff and Mypy issues.
  
- 
- 
- 
- 
- 
- 
- 
- 
- 
+ ## 9. Implementing Falla-based Search Engines
+ 
+ Based on the NEXTENGINES.md file, we need to implement search engines based on the [Falla project](https://github.com/Sanix-Darker/falla), which is a search engine scraper supporting multiple search engines.
+ 
+ ### 9.1. Understanding Falla Architecture
+ 
+ Falla is a Python-based search engine scraper that supports multiple search engines including Google, Bing, DuckDuckGo, and others. Each search engine has its own implementation file in the `app/core/` directory, inheriting from a base `Falla` class.
+ 
+ The key components of Falla are:
+ 1. A base `Falla` class that handles common scraping functionality
+ 2. Individual engine classes (Google, Bing, etc.) that define engine-specific parameters
+ 3. A common interface for searching and result parsing
+ 
+ ### 9.2. Implementation Plan for *-falla Engines
+ 
+ #### 9.2.1. Setup and Dependencies
+ 
+ 1. Create a new module `src/twat_search/web/engines/falla.py` to implement Falla-based engines
+ 2. Add necessary dependencies to `pyproject.toml`:
+    - `selenium` for browser automation
+    - `lxml` for HTML parsing
+    - Optional: Consider if we need Docker/Splash for some engines
+ 
+ #### 9.2.2. Base Implementation
+ 
+ 1. Create a base `FallaSearchEngine` class that:
+    - Inherits from `SearchEngine`
+    - Implements the common functionality for all Falla-based engines
+    - Handles initialization of Falla components
+    - Provides methods for converting Falla results to `SearchResult` objects
+ 
+ 2. Implement a factory function to create specific Falla engine instances based on the engine code
+ 
+ #### 9.2.3. Engine-Specific Implementations
+ 
+ Implement the following Falla-based engines:
+ 1. `google-falla`: Google search using Falla
+ 2. `bing-falla`: Bing search using Falla
+ 3. `duckduckgo-falla`: DuckDuckGo search using Falla
+ 4. `aol-falla`: AOL search using Falla
+ 5. `ask-falla`: Ask.com search using Falla
+ 6. `dogpile-falla`: DogPile search using Falla
+ 7. `gibiru-falla`: Gibiru search using Falla
+ 8. `mojeek-falla`: Mojeek search using Falla
+ 9. `qwant-falla`: Qwant search using Falla
+ 10. `yahoo-falla`: Yahoo search using Falla
+ 11. `yandex-falla`: Yandex search using Falla
+ 
+ For each engine:
+ - Create a specific engine class that inherits from `FallaSearchEngine`
+ - Configure engine-specific parameters (URLs, selectors, etc.)
+ - Register the engine with the `register_engine` decorator
+ 
+ #### 9.2.4. Error Handling and Robustness
+ 
+ 1. Implement proper error handling for common Falla issues:
+    - Network errors
+    - Parsing errors
+    - Captcha detection
+    - Rate limiting
+ 2. Add retry logic with exponential backoff
+ 3. Implement fallback mechanisms when a specific engine fails
+ 
+ #### 9.2.5. Testing
+ 
+ 1. Create unit tests for each Falla-based engine:
+    - Test initialization
+    - Test search functionality with mocked responses
+    - Test error handling
+ 2. Create integration tests that perform actual searches (with limited scope)
+ 3. Create a test utility to verify all Falla engines are working correctly
+ 
+ ### 9.3. Implementation Challenges and Considerations
+ 
+ 1. **Dependency Management**: Falla requires Selenium and potentially Docker/Splash. We need to decide if these should be optional dependencies or required for all users.
+ 
+ 2. **Rate Limiting and IP Blocking**: Search engines may block IPs that perform too many automated searches. We need to implement proper rate limiting and potentially proxy rotation.
+ 
+ 3. **Maintenance Overhead**: Web scraping is fragile and requires frequent updates as search engine UIs change. We need to consider the maintenance burden of supporting these engines.
+ 
+ 4. **Legal Considerations**: Scraping search engines may violate their Terms of Service. We should include appropriate disclaimers and usage guidelines.
+ 
+ ### 9.4. Implementation Timeline
+ 
+ 1. **Week 1**: Setup and base implementation
+    - Create the base `FallaSearchEngine` class
+    - Implement the factory function
+    - Implement 2-3 initial engines (e.g., Google, Bing, DuckDuckGo)
+ 
+ 2. **Week 2**: Complete engine implementations
+    - Implement the remaining engines
+    - Add comprehensive error handling
+    - Create basic tests
+ 
+ 3. **Week 3**: Testing and refinement
+    - Complete test suite
+    - Refine error handling and robustness
+    - Document usage and limitations
+ 
+ ### 9.5. Success Criteria
+ 
+ The implementation will be considered successful when:
+ 1. All specified Falla-based engines are implemented and registered
+ 2. Each engine can successfully perform searches and return results
+ 3. The implementation handles errors gracefully
+ 4. The test suite passes for all engines
+ 5. The implementation is well-documented with usage examples and limitations
  
```

---

_****_



Now, let me update the PROGRESS.md file with specific action items for implementing the Falla-based engines:

---

_****_

```diff
    - [ ] Test with the problem case command
    - [ ] Ensure all engines return proper results
+ 
+ ## 9. Implement Falla-based Search Engines
+ 
+ - [ ] Setup and dependencies
+   - [ ] Create new module `src/twat_search/web/engines/falla.py`
+   - [ ] Add necessary dependencies to `pyproject.toml` (selenium, lxml)
+   - [ ] Determine if Docker/Splash is needed and document requirements
+ 
+ - [ ] Create base `FallaSearchEngine` class
+   - [ ] Inherit from `SearchEngine`
+   - [ ] Implement common functionality for all Falla-based engines
+   - [ ] Create methods for initializing Falla components
+   - [ ] Implement result conversion to `SearchResult` objects
+   - [ ] Add proper error handling and retries
+ 
+ - [ ] Implement factory function for Falla engines
+   - [ ] Create function to instantiate specific Falla engine based on engine code
+   - [ ] Add validation for supported engines
+   - [ ] Handle configuration parameters
+ 
+ - [ ] Implement specific Falla-based engines
+   - [ ] `google-falla`: Google search using Falla
+   - [ ] `bing-falla`: Bing search using Falla
+   - [ ] `duckduckgo-falla`: DuckDuckGo search using Falla
+   - [ ] `aol-falla`: AOL search using Falla
+   - [ ] `ask-falla`: Ask.com search using Falla
+   - [ ] `dogpile-falla`: DogPile search using Falla
+   - [ ] `gibiru-falla`: Gibiru search using Falla
+   - [ ] `mojeek-falla`: Mojeek search using Falla
+   - [ ] `qwant-falla`: Qwant search using Falla
+   - [ ] `yahoo-falla`: Yahoo search using Falla
+   - [ ] `yandex-falla`: Yandex search using Falla
+ 
+ - [ ] Implement robust error handling
+   - [ ] Handle network errors gracefully
+   - [ ] Detect and handle captchas
+   - [ ] Implement rate limiting protection
+   - [ ] Add fallback mechanisms for failed engines
+ 
+ - [ ] Create comprehensive tests
+   - [ ] Unit tests for each Falla-based engine
+   - [ ] Integration tests with limited scope
+   - [ ] Test utility to verify all engines
+   - [ ] Test error handling and edge cases
+ 
+ - [ ] Documentation and examples
+   - [ ] Document usage of Falla-based engines
+   - [ ] Add examples to README
+   - [ ] Document limitations and considerations
+   - [ ] Add appropriate disclaimers regarding web scraping
  
```

---

_****_



Now, let me gather more information about the project structure to ensure my implementation plan is aligned with the existing codebase.

---

_****_

<details>
            <summary>Listed current directory • **30** results</summary>
        
| Name |
|-------|
| 📄 `PROGRESS.md` |
| 📄 `TODO.md` |
| 📁 `.mypy_cache` |
| 📁 `.venv` |
| 📄 `CLEANUP.txt` |
| 📄 `twat_search.txt` |
| 📁 `.git` |
| 📄 `.DS_Store` |
| 📁 `resources` |
| 📁 `_private` |
| 📄 `.pre-commit-config.yaml` |
| 📁 `.idea` |
| 📁 `tests` |
| 📄 `pyproject.toml` |
| 📄 `cleanup.py` |
| 📄 `LICENSE` |
| 📄 `NEXTENGINES.md` |
| 📁 `.ruff_cache` |
| 📄 `uv.lock` |
| 📄 `README.md` |
| 📄 `CHANGELOG.md` |
| 📁 `.specstory` |
| 📁 `dist` |
| 📁 `src` |
| 📁 `.benchmarks` |
| 📁 `.cursor` |
| 📄 `VERSION.txt` |
| 📁 `.pytest_cache` |
| 📁 `.github` |
| 📄 `.gitignore` |

</details>

---

_****_





Let me check the source directory structure to understand how the engines are organized:

---

_****_

<details>
            <summary>Listed directory src/twat_search/web/engines • **15** results</summary>
        
| Name |
|-------|
| 📄 `tavily.py` |
| 📁 `__pycache__` |
| 📄 `you.py` |
| 📄 `pplx.py` |
| 📄 `searchit.py` |
| 📄 `serpapi.py` |
| 📄 `duckduckgo.py` |
| 📄 `google_scraper.py` |
| 📄 `hasdata.py` |
| 📄 `base.py` |
| 📄 `bing_scraper.py` |
| 📄 `brave.py` |
| 📄 `critique.py` |
| 📄 `__init__.py` |
| 📄 `.DS_Store` |

</details>

---

_****_





Let me also check the base.py file to understand the base SearchEngine class:

---

_****_

Read file: src/twat_search/web/engines/base.py

---

_****_





Now, let me check an example of an existing engine implementation to understand the pattern:

---

_****_

Read file: src/twat_search/web/engines/google_scraper.py

---

_****_







Let me also check the __init__.py file to understand how engines are registered:

---

_****_

Read file: src/twat_search/web/engines/__init__.py

---

_****_







Based on my analysis of the codebase, I now have a clear understanding of how to implement the Falla-based engines. Let me update the TODO.md file with a more detailed implementation plan:

---

_****_



---

_****_





Let me update the PROGRESS.md file with more specific action items based on the detailed implementation plan:

---

_****_

```diff
  - [ ] Setup and dependencies
    - [ ] Create new module `src/twat_search/web/engines/falla.py`
-   - [ ] Add necessary dependencies to `pyproject.toml` (selenium, lxml)
-   - [ ] Determine if Docker/Splash is needed and document requirements
+   - [ ] Add necessary dependencies to `pyproject.toml` (selenium, lxml, requests)
+   - [ ] Define engine constants in `src/twat_search/web/engine_constants.py`
+   - [ ] Update `src/twat_search/web/engines/__init__.py` to import and register new engines
+   - [ ] Create utility function to check if Falla is installed and accessible
  
  - [ ] Create base `FallaSearchEngine` class
    - [ ] Inherit from `SearchEngine`
-   - [ ] Implement common functionality for all Falla-based engines
-   - [ ] Create methods for initializing Falla components
-   - [ ] Implement result conversion to `SearchResult` objects
-   - [ ] Add proper error handling and retries
- 
- - [ ] Implement factory function for Falla engines
-   - [ ] Create function to instantiate specific Falla engine based on engine code
-   - [ ] Add validation for supported engines
-   - [ ] Handle configuration parameters
+   - [ ] Define `FallaResult` Pydantic model for result validation
+   - [ ] Implement abstract `_initialize_falla_engine` method
+   - [ ] Create `_convert_result` method to convert Falla results to `SearchResult` objects
+   - [ ] Implement `search` method with proper error handling and retries
+   - [ ] Create fallback implementation for when Falla is not available
  
  - [ ] Implement specific Falla-based engines
    - [ ] `google-falla`: Google search using Falla
+     - [ ] Create `GoogleFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `bing-falla`: Bing search using Falla
+     - [ ] Create `BingFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `duckduckgo-falla`: DuckDuckGo search using Falla
+     - [ ] Create `DuckDuckGoFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `aol-falla`: AOL search using Falla
+     - [ ] Create `AolFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `ask-falla`: Ask.com search using Falla
+     - [ ] Create `AskFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `dogpile-falla`: DogPile search using Falla
+     - [ ] Create `DogpileFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `gibiru-falla`: Gibiru search using Falla
+     - [ ] Create `GibiruFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `mojeek-falla`: Mojeek search using Falla
+     - [ ] Create `MojeekFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `qwant-falla`: Qwant search using Falla
+     - [ ] Create `QwantFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `yahoo-falla`: Yahoo search using Falla
+     - [ ] Create `YahooFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
    - [ ] `yandex-falla`: Yandex search using Falla
+     - [ ] Create `YandexFallaEngine` class
+     - [ ] Implement `_initialize_falla_engine` method
+     - [ ] Register with `@register_engine` decorator
  
  - [ ] Implement robust error handling
    - [ ] Implement rate limiting protection
    - [ ] Add fallback mechanisms for failed engines
+   - [ ] Handle case when Falla is not available
  
  - [ ] Create comprehensive tests
-   - [ ] Unit tests for each Falla-based engine
-   - [ ] Integration tests with limited scope
-   - [ ] Test utility to verify all engines
-   - [ ] Test error handling and edge cases
+   - [ ] Create unit tests for base `FallaSearchEngine` class
+     - [ ] Test initialization
+     - [ ] Test result conversion
+     - [ ] Test error handling
+   - [ ] Create unit tests for each Falla-based engine
+     - [ ] Test initialization
+     - [ ] Test search functionality with mocked responses
+     - [ ] Test error handling
+   - [ ] Create integration tests with limited scope
+     - [ ] Test actual search functionality (skipped if Falla not available)
+     - [ ] Test result formatting
+   - [ ] Create test utility to verify all engines
+     - [ ] Test all engines with a simple query
+     - [ ] Verify results format
  
  - [ ] Documentation and examples
-   - [ ] Document usage of Falla-based engines
-   - [ ] Add examples to README
+   - [ ] Document installation requirements for Falla engines
+   - [ ] Add usage examples to README
    - [ ] Document limitations and considerations
    - [ ] Add appropriate disclaimers regarding web scraping
+   - [ ] Update CLI help text to include new engines
  
```

---

_****_





Based on my analysis of the NEXTENGINES.md file and the existing codebase, I've created a comprehensive implementation plan for adding the Falla-based search engines to the twat-search project. Here's a summary of what I've done:

1. **Detailed Implementation Plan in TODO.md**:
   - Added a new section (Section 9) that outlines the approach for implementing Falla-based engines
   - Provided a thorough understanding of the Falla architecture
   - Created a step-by-step implementation plan with code examples
   - Addressed potential challenges and considerations
   - Established success criteria and a timeline

2. **Specific Action Items in PROGRESS.md**:
   - Added a structured task list with detailed subtasks for each component
   - Broke down the implementation into manageable chunks
   - Included specific tasks for each of the 11 Falla-based engines
   - Added comprehensive testing tasks
   - Included documentation requirements

The implementation plan follows these key steps:

1. **Setup and Dependencies**: Create the necessary module structure and add dependencies
2. **Base Implementation**: Create a `FallaSearchEngine` base class that handles common functionality
3. **Engine-Specific Implementations**: Implement each of the 11 Falla-based engines
4. **Error Handling**: Implement robust error handling for various failure scenarios
5. **Testing**: Create comprehensive unit and integration tests
6. **Documentation**: Document usage, limitations, and considerations

The plan takes into account the existing codebase structure and follows the established patterns for implementing search engines in the twat-search project. It also addresses potential challenges such as dependency management, rate limiting, and maintenance overhead.

Wait, but I should also consider how to handle the installation of Falla itself. Since Falla is an external project, we need a clear strategy for how users will install and use it with twat-search.

Let me update the TODO.md file with a section on Falla installation options:

---

_****_



---

_****_







Let me update the PROGRESS.md file with tasks related to the Falla installation options:

---

_****_

```diff
    - [ ] Handle case when Falla is not available
  
+ - [ ] Implement Falla integration approach
+   - [ ] Decide on integration approach (embedded vs. dependency)
+   - [ ] If embedded:
+     - [ ] Create simplified implementation of Falla core functionality
+     - [ ] Implement key scraping methods
+     - [ ] Ensure proper attribution and licensing
+   - [ ] If dependency:
+     - [ ] Add Falla as optional dependency in pyproject.toml
+     - [ ] Create fallback for when Falla is not installed
+     - [ ] Document installation requirements
+ 
  - [ ] Create comprehensive tests
    - [ ] Create unit tests for base `FallaSearchEngine` class
```

---

_****_





Based on my analysis of the NEXTENGINES.md file and the existing codebase, I've created a comprehensive implementation plan for adding the Falla-based search engines to the twat-search project.

## Summary of Implementation Plan

1. **Understanding Falla Architecture**
   - Falla is a search engine scraper supporting 15+ search engines
   - Each engine inherits from a base Falla class
   - Engines use different scraping methods (requests, selenium, splash)

2. **Implementation Approach**
   - Create a base `FallaSearchEngine` class inheriting from `SearchEngine`
   - Implement specific engine classes for each Falla engine (Google, Bing, etc.)
   - Handle result conversion and error cases
   - Ensure proper integration with the existing codebase

3. **Falla Integration Options**
   - Evaluated four options: direct dependency, optional dependency, embedded implementation, or hybrid approach
   - Recommended embedded implementation for simplicity and control
   - This approach avoids external dependencies and ensures stability

4. **Key Components to Implement**
   - Base `FallaSearchEngine` class with common functionality
   - 11 specific engine implementations (Google, Bing, DuckDuckGo, etc.)
   - Robust error handling and fallback mechanisms
   - Comprehensive test suite

5. **Testing Strategy**
   - Unit tests for base class and each engine
   - Integration tests with limited scope
   - Test utility to verify all engines

The implementation plan is detailed in TODO.md with specific code examples and considerations, while PROGRESS.md contains a structured task list with detailed subtasks for tracking progress.

This approach ensures that the Falla-based engines will be properly integrated into the twat-search project, following the established patterns and best practices of the existing codebase.

---

_****_



---



---

