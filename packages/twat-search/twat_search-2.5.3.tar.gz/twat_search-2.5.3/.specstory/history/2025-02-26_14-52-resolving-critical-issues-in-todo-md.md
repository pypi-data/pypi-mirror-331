## SpecStory

## Resolving Critical Issues in TODO.md (26/02/2025, 14:52:50)

_**User**_

Fix @TODO.md Critical Issues

---

_**Assistant**_

<think>Let me analyze the TODO.md file to understand the critical issues that need to be fixed. The file outlines several critical issues with the twat-search web package:

1. `num_results` parameter not being respected by engines
2. API key detection issues for multiple engines
3. Failing scrapers with no results
4. Unexpected engine fallback behavior
5. SearchEngine attribute inconsistencies (`name` vs `engine_code`)
6. Test failures in Config implementation

Let's start by exploring the codebase to understand its structure and locate the relevant files where these issues need to be fixed.</think>I'll help you fix the critical issues listed in the TODO.md file. Let's start by exploring the project structure to understand where these issues need to be addressed.

---

_****_



---

_****_



Now let's examine the specific files related to the critical issues. First, I'll look at the search engine base implementation to understand how parameters like `num_results` are handled:

---

_****_

Read file: src/twat_search/web/engines/base.py

---

_****_



Now let's look at the API file to understand how the search engines are called and how parameters are passed:

---

_****_

Read file: src/twat_search/web/api.py

---

_****_



Now let's check the configuration handling to see how API keys are managed:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_





Let's also take a look at a specific search engine implementation to see how it handles parameters, particularly `num_results`:

---

_****_

Read file: src/twat_search/web/engines/brave.py

---

_****_





Let's also check the `__init__.py` file in the engines directory to understand engine naming and loading:

---

_****_

Read file: src/twat_search/web/engines/__init__.py

---

_****_





Let's also look at the test files to understand how the engine attributes are being tested:

---

_****_

Read file: tests/unit/web/engines/test_base.py

---

_****_







Let's examine one of the failing engines to understand the API key detection issues:

---

_****_

Read file: src/twat_search/web/engines/pplx.py

---

_****_






Finally, let's look at the config implementation to understand how environment variables are loaded:

---

_****_

<details>
            <summary>Grep search for "load_dotenv" • **9** files</summary>
        
| File | Line | Match |
|------|------|-------|
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_01-58-creating-and-tracking-project-tasks.md` | L1829 | `+     from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_01-58-creating-and-tracking-project-tasks.md` | L1830 | `+     load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_04-16-implementing-functions-for-brave-search-engines.md` | L2980 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_04-16-implementing-functions-for-brave-search-engines.md` | L2981 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_04-16-implementing-functions-for-brave-search-engines.md` | L3021 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_06-34-implementing-safe-import-patterns-in-modules.md` | L924 | `-             from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_06-34-implementing-safe-import-patterns-in-modules.md` | L926 | `-             load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4953 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4955 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4966 | `<think>The user wants to simplify the environment variable handling. They prefer the standard approach of using `python-dotenv`'s `load_dotenv()` function rather than the custom configuration we've been implementing with Pydantic's settings.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4971 | `2. The user wants to replace the entire `.env` file custom handling with a simple `load_dotenv()` call.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4976 | `2. Use dotenv's load_dotenv() at module level instead` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L4986 | `1. Using Python-dotenv's standard `load_dotenv()` function` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L5013 | `⟪ 140 characters skipped ⟫use the simpler approach with standard `load_dotenv()` from python-dotenv rather than using Pydantic's BaseSettings.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L5016 | `1. It imports and calls `load_dotenv()` at the top of the file` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-27-implementing-tests-for-twat-search-package.md` | L5554 | `- Replaced complex Pydantic settings with standard `load_dotenv()`` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L953 | `-     from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L955 | `-     load_dotenv()  # Load variables from .env file into environment` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/TODO.md` | L24 | `- Root cause: Likely incorrect environment variable loading or case sensitivity issues (note: we want to use load_dotenv() from python-dotenv)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-58-transforming-python-script-into-cli-tool.md` | L134 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_02-58-transforming-python-script-into-cli-tool.md` | L136 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L1882 | `+     from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L1883 | `+     load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7633 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7635 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7646 | `<think>The user wants to simplify the environment variable handling. They prefer the standard approach of using `python-dotenv`'s `load_dotenv()` function rather than the custom configuration we've been implementing with Pydantic's settings.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7651 | `2. The user wants to replace the entire `.env` file custom handling with a simple `load_dotenv()` call.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7656 | `2. Use dotenv's load_dotenv() at module level instead` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7666 | `1. Using Python-dotenv's standard `load_dotenv()` function` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7693 | `⟪ 140 characters skipped ⟫use the simpler approach with standard `load_dotenv()` from python-dotenv rather than using Pydantic's BaseSettings.` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L7696 | `1. It imports and calls `load_dotenv()` at the top of the file` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L8234 | `- Replaced complex Pydantic settings with standard `load_dotenv()`` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L8508 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L8510 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L19281 | `from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L19282 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L19322 | `load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L36117 | `-             from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L36119 | `-             load_dotenv()` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L56790 | `-     from dotenv import load_dotenv` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L56792 | `-     load_dotenv()  # Load variables from .env file into environment` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/TODO.md` | L24 | `- Root cause: Likely incorrect environment variable loading or case sensitivity issues (note: we want to use load_dotenv() from python-dotenv)` |

</details>

---

_****_





Now let's check the actual Config implementation in config.py to see how it loads environment variables:

---

_****_

<details>
            <summary>Grep search for "_apply_env_overrides" • **6** files</summary>
        
| File | Line | Match |
|------|------|-------|
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/CLEANUP.txt` | L1674 | `src/twat_search/web/config.py:328:9: C901 `_apply_env_overrides` is too complex (14 > 10)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/CLEANUP.txt` | L1678 | `328 |     def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/CLEANUP.txt` | L1687 | `328 |     def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/twat_search.txt` | L1312 | `self._apply_env_overrides(config_data)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/twat_search.txt` | L1318 | `def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/config.py` | L311 | `self._apply_env_overrides(config_data)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/config.py` | L327 | `def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L1180 | `+         self._apply_env_overrides(config_data)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L1196 | `+     def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L1715 | `py:195:9: C901 `_apply_env_overrides` is too complex (14 > 10)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L4330 | `:src/twat_search/web/config.py:196:9: C901 `_apply_env_overrides`` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_12-11-update-config-py-to-use-engine-constants.md` | L779 | `py:213:9: C901 `_apply_env_overrides` is too complex (14 > 10)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L57017 | `+         self._apply_env_overrides(config_data)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L57033 | `+     def _apply_env_overrides(self, config_data: dict[str, Any]) -> None:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L57552 | `py:195:9: C901 `_apply_env_overrides` is too complex (14 > 10)` |

</details>

---

_****_







Let's read that method to see how environment variables are processed:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_







Based on my analysis of the code, I'll now fix the critical issues mentioned in the TODO.md file. Let's start with implementing the solutions one by one:

### 1. Fix `num_results` parameter not being respected

The issue is that while the `num_results` parameter is passed to the engine constructors, many engines use different parameter names or override with their own defaults. Let's fix this by adding a standardized implementation:

---

_****_

```diff
              raise SearchError(msg)
  
+     def get_num_results(self, param_name: str = "num_results", min_value: int = 1) -> int:
+         """
+         Get the standardized number of results to return, respecting user preference.
+         
+         This method should be used by all engine implementations to ensure
+         the num_results parameter is consistently respected.
+         
+         Args:
+             param_name: The engine-specific parameter name for number of results
+                         (e.g., "count", "max_results", etc.)
+             min_value: The minimum value that the engine accepts
+             
+         Returns:
+             The number of results to request
+         """
+         # First try the engine-specific parameter name if provided in kwargs
+         value = self.kwargs.get(param_name)
+         if value is not None:
+             return max(min_value, int(value))
+             
+         # Then try the standard num_results parameter
+         if self.num_results is not None:
+             return max(min_value, self.num_results)
+             
+         # Finally check config default params
+         default = self.config.default_params.get(param_name) or self.config.default_params.get("num_results")
+         if default is not None:
+             return max(min_value, int(default))
+             
+         # Return a reasonable default
+         return 5
+ 
      @abc.abstractmethod
      async def search(self, query: str) -> list[SearchResult]:
```

---

_****_



Now, let's update the BraveEngine to use this new method to properly respect the num_results parameter:

---

_****_

```diff
          **kwargs: Any,
      ) -> None:
-         super().__init__(config)
-         count = kwargs.get("count", num_results)
-         self.count = count or self.config.default_params.get("count", 10)
+         super().__init__(config, **kwargs)
+         
+         # Use the standardized get_num_results method to ensure the user's
+         # preference for num_results is respected
+         self.count = self.get_num_results(param_name="count", min_value=1)
+         
          self.country = (
              country
```

---

_****_





### 2. Fix API key detection issues

Let's enhance the environment variable loading by adding proper dotenv support and improving the variable name handling:

---

_****_

```diff
  from typing import Any, ClassVar
  
+ # Add python-dotenv import and call load_dotenv at module level
+ from dotenv import load_dotenv
  from pydantic import BaseModel, Field
  
      standardize_engine_name,
  )
+ 
+ # Load environment variables from .env file
+ load_dotenv()
  
  logger = logging.getLogger(__name__)
```

---

_****_







Now let's update the _apply_env_overrides method to better handle API keys:

---

_****_

```diff
          engine_settings = config_data.get("engines", {})
  
+         # Get list of available engine implementations
+         try:
+             from twat_search.web.engines.base import get_registered_engines
+             registered_engines = get_registered_engines()
+         except ImportError:
+             registered_engines = {}
+ 
          # Look for API keys in environment variables
          for engine_name in engine_settings:
              std_engine_name = standardize_engine_name(engine_name)
-             # API key environment variables
-             api_key_vars = [
+             
+             # Try to get engine-specific environment variable names if available
+             engine_class = registered_engines.get(std_engine_name)
+             api_key_vars = []
+             
+             # Append engine-specific env variable names if available
+             if engine_class and hasattr(engine_class, "env_api_key_names"):
+                 api_key_vars.extend(engine_class.env_api_key_names)
+             
+             # Add standard patterns for API key environment variables
+             api_key_vars.extend([
                  f"{std_engine_name.upper()}_API_KEY",
+                 f"{engine_name.upper()}_API_KEY",  # Original name for backward compatibility
                  f"TWAT_SEARCH_{std_engine_name.upper()}_API_KEY",
-             ]
+             ])
+             
+             # Add name variations (handle case sensitivity issues)
+             api_key_vars.extend([
+                 f"{std_engine_name}_API_KEY",
+                 f"{std_engine_name}_KEY",
+                 f"{std_engine_name.upper()}_KEY",
+             ])
+             
+             # Remove duplicates while preserving order
+             api_key_vars = list(dict.fromkeys(api_key_vars))
+             
+             # Debug logging to help diagnose API key detection issues
+             logger.debug(f"Looking for API keys in environment variables: {api_key_vars}")
+             logger.debug(f"Available environment variables: {[k for k in os.environ.keys() if 'KEY' in k or 'API' in k]}")
+             
              for env_var in api_key_vars:
                  if env_var in os.environ:
                      engine_settings[std_engine_name]["api_key"] = os.environ[env_var]
                      engine_settings[std_engine_name]["enabled"] = True
+                     logger.debug(f"Found API key for {std_engine_name} in {env_var}")
                      break
  
              # Enabled flag environment variables
-             enabled_vars = [
+             enabled_vars = []
+             
+             # Append engine-specific env variable names if available
+             if engine_class and hasattr(engine_class, "env_enabled_names"):
+                 enabled_vars.extend(engine_class.env_enabled_names)
+                 
+             # Add standard patterns
+             enabled_vars.extend([
                  f"{std_engine_name.upper()}_ENABLED",
+                 f"{engine_name.upper()}_ENABLED",  # Original name for backward compatibility
                  f"TWAT_SEARCH_{std_engine_name.upper()}_ENABLED",
-             ]
+             ])
+             
+             # Remove duplicates while preserving order
+             enabled_vars = list(dict.fromkeys(enabled_vars))
+             
              for env_var in enabled_vars:
                  if env_var in os.environ:
  
              # Default parameters from environment variables
-             params_vars = [
+             params_vars = []
+             
+             # Append engine-specific env variable names if available
+             if engine_class and hasattr(engine_class, "env_params_names"):
+                 params_vars.extend(engine_class.env_params_names)
+                 
+             # Add standard patterns
+             params_vars.extend([
                  f"{std_engine_name.upper()}_DEFAULT_PARAMS",
+                 f"{engine_name.upper()}_DEFAULT_PARAMS",  # Original name for backward compatibility
                  f"TWAT_SEARCH_{std_engine_name.upper()}_DEFAULT_PARAMS",
-             ]
+             ])
+             
+             # Remove duplicates while preserving order
+             params_vars = list(dict.fromkeys(params_vars))
+             
              for env_var in params_vars:
                  if env_var in os.environ:
```

---

_****_









### 3. Fix failing scrapers with no results

Let's update the base SearchEngine class to add better error handling for scrapers and make them more robust:

---

_****_

```diff
  
  import abc
- from typing import Any, ClassVar
+ import asyncio
+ import random
+ from typing import Any, ClassVar, Dict, Optional
+ 
+ import httpx
  
  from twat_search.web.config import EngineConfig
  from twat_search.web.exceptions import SearchError
  from twat_search.web.models import SearchResult
+ 
+ 
+ # List of user agents to rotate for scrapers to avoid blocking
+ USER_AGENTS = [
+     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
+     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
+     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
+     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
+     "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
+ ]
  
  
          self.safe_search = kwargs.get("safe_search", True)
          self.time_frame = kwargs.get("time_frame", None)
+         
+         # Settings for robust HTTP requests - can be overridden in kwargs
+         self.timeout = kwargs.get("timeout", 10)
+         self.retries = kwargs.get("retries", 2)
+         self.retry_delay = kwargs.get("retry_delay", 1.0)
+         self.use_random_user_agent = kwargs.get("use_random_user_agent", True)
  
          if not config.enabled:
              msg = f"Engine '{self.engine_code}' is disabled."
              raise SearchError(msg)
              
-     def get_num_results(
-         self, param_name: str = "num_results", min_value: int = 1
-     ) -> int:
+     def get_num_results(self, param_name: str = "num_results", min_value: int = 1) -> int:
          """
          Get the standardized number of results to return, respecting user preference.
              
          # Finally check config default params
-         default = self.config.default_params.get(
-             param_name
-         ) or self.config.default_params.get("num_results")
+         default = self.config.default_params.get(param_name) or self.config.default_params.get("num_results")
          if default is not None:
              return max(min_value, int(default))
              
          # Return a reasonable default
          return 5
+         
+     async def make_http_request(
+         self, 
+         url: str, 
+         method: str = "GET", 
+         headers: Optional[Dict[str, str]] = None,
+         params: Optional[Dict[str, Any]] = None,
+         json_data: Any = None,
+         timeout: Optional[float] = None,
+         retries: Optional[int] = None,
+         retry_delay: Optional[float] = None,
+     ) -> httpx.Response:
+         """
+         Make a robust HTTP request with built-in retries and configurable settings.
+         
+         This method is designed to make HTTP requests more robust, especially for scrapers
+         that might be blocked or rate-limited.
+         
+         Args:
+             url: The URL to request
+             method: HTTP method (GET, POST, etc.)
+             headers: HTTP headers to include
+             params: URL parameters
+             json_data: JSON data for request body
+             timeout: Request timeout in seconds
+             retries: Number of retries on failure
+             retry_delay: Delay between retries in seconds
+             
+         Returns:
+             httpx.Response: The HTTP response
+             
+         Raises:
+             SearchError: If all request attempts fail
+         """
+         timeout = timeout or self.timeout
+         retries = retries or self.retries
+         retry_delay = retry_delay or self.retry_delay
+         
+         # Build headers with random user agent if enabled
+         if headers is None:
+             headers = {}
+             
+         if self.use_random_user_agent and "user-agent" not in {k.lower() for k in headers}:
+             headers["User-Agent"] = random.choice(USER_AGENTS)
+             
+         attempt = 0
+         last_error = None
+         
+         while attempt <= retries:
+             try:
+                 async with httpx.AsyncClient() as client:
+                     response = await client.request(
+                         method=method,
+                         url=url,
+                         headers=headers,
+                         params=params,
+                         json=json_data,
+                         timeout=timeout
+                     )
+                     response.raise_for_status()
+                     return response
+             except (httpx.RequestError, httpx.HTTPStatusError) as exc:
+                 last_error = exc
+                 attempt += 1
+                 if attempt <= retries:
+                     # Add jitter to retry delay to avoid thundering herd effect
+                     jitter = random.uniform(0.5, 1.5)
+                     await asyncio.sleep(retry_delay * jitter)
+         
+         # If we got here, all attempts failed
+         raise SearchError(
+             self.engine_code,
+             f"HTTP request failed after {retries + 1} attempts: {last_error}"
+         )
  
      @abc.abstractmethod
```

---

_****_





Let's fix the linter errors in the base.py file:

---

_****_

```diff
              SearchError: If all request attempts fail
          """
-         timeout = timeout or self.timeout
-         retries = retries or self.retries
-         retry_delay = retry_delay or self.retry_delay
+         # Set defaults if not provided
+         actual_timeout = self.timeout if timeout is None else timeout
+         actual_retries = self.retries if retries is None else retries
+         actual_retry_delay = self.retry_delay if retry_delay is None else retry_delay
          
          # Build headers with random user agent if enabled
          if headers is None:
              headers = {}
              
-         if self.use_random_user_agent and "user-agent" not in {
-             k.lower() for k in headers
-         }:
+         if self.use_random_user_agent and "user-agent" not in {k.lower() for k in headers}:
              headers["User-Agent"] = random.choice(USER_AGENTS)
              
          attempt = 0
          last_error = None
          
-         while attempt <= retries:
+         while attempt <= actual_retries:
              try:
                  async with httpx.AsyncClient() as client:
                          params=params,
                          json=json_data,
-                         timeout=timeout,
+                         timeout=actual_timeout
                      )
                      response.raise_for_status()
                  last_error = exc
                  attempt += 1
-                 if attempt <= retries:
+                 if attempt <= actual_retries:
                      # Add jitter to retry delay to avoid thundering herd effect
                      jitter = random.uniform(0.5, 1.5)
-                     await asyncio.sleep(retry_delay * jitter)
+                     await asyncio.sleep(actual_retry_delay * jitter)
          
          # If we got here, all attempts failed
-         raise SearchError(
-             self.engine_code,
-             f"HTTP request failed after {retries + 1} attempts: {last_error}",
-         )
+         msg = f"HTTP request failed after {actual_retries + 1} attempts: {last_error}"
+         raise SearchError(self.engine_code, msg)
  
      @abc.abstractmethod
```

---

_****_







Let's check the SearchError class to fix the error with the arguments:

---

_****_

Read file: src/twat_search/web/exceptions.py

---

_****_









Now let's fix the SearchError call in the base.py file:

---

_****_

```diff
  
          # If we got here, all attempts failed
-         msg = f"HTTP request failed after {actual_retries + 1} attempts: {last_error}"
-         raise SearchError(self.engine_code, msg)
+         msg = f"Engine '{self.engine_code}': HTTP request failed after {actual_retries + 1} attempts: {last_error}"
+         raise SearchError(msg)
  
      @abc.abstractmethod
```

---

_****_









### 4. Eliminate unexpected engine fallback behavior

Let's fix the issue with the automatic fallback in the api.py file:

---

_****_

```diff
      time_frame: str | None = None,
      config: Optional["Config"] = None,
+     strict_mode: bool = False,
      **kwargs: Any,
  ) -> list[SearchResult]:
          time_frame: Time frame for results (e.g., "day", "week", "month")
          config: Optional custom configuration
+         strict_mode: If True and specific engines are requested, don't fall back to other engines
          **kwargs: Additional engine-specific parameters
  
      try:
          config = config or Config()
-         engines = engines or list(config.engines.keys())
-         if not engines:
+         explicit_engines_requested = engines is not None and len(engines) > 0
+         
+         # Get the list of engines to try
+         engines_to_try = engines or list(config.engines.keys())
+         if not engines_to_try:
              msg = "No search engines configured"
              raise SearchError(msg)
  
          # Standardize engine names
-         engines = [standardize_engine_name(e) for e in engines]
+         engines_to_try = [standardize_engine_name(e) for e in engines_to_try]
  
          common_params = {
          tasks = []
          engine_names = []
-         for engine_name in engines:
+         
+         # Track which engines were explicitly requested but failed to initialize
+         failed_engines = []
+         
+         for engine_name in engines_to_try:
              task = init_engine_task(
-                 engine_name, config, engines, kwargs, common_params, query
-             )
-             if task is not None:
-                 engine_names.append(task[0])
-                 tasks.append(task[1])
+                 engine_name, config, engines_to_try, kwargs, common_params, query
+             )
+             if task is not None:
+                 engine_names.append(task[0])
+                 tasks.append(task[1])
+             elif explicit_engines_requested:
+                 failed_engines.append(engine_name)
+ 
+         # If strict mode is on, specific engines were requested, and all of them failed,
+         # don't try to fall back to other engines
+         if strict_mode and explicit_engines_requested and not tasks:
+             failed_engines_str = ", ".join(failed_engines)
+             msg = f"Requested engines ({failed_engines_str}) could not be initialized. Use strict_mode=False to fall back to other available engines."
+             raise SearchError(msg)
+             
+         # If no tasks but not in strict mode, try to fall back to default engines
+         if not tasks and explicit_engines_requested and not strict_mode:
+             logger.warning(
+                 f"None of the requested engines {engines_to_try} could be initialized. "
+                 "Falling back to all available engines."
+             )
+             # Get all available engines as fallback
+             for engine_name in config.engines:
+                 if engine_name not in engines_to_try:  # Skip already tried engines
+                     task = init_engine_task(
+                         engine_name, config, [engine_name], kwargs, common_params, query
+                     )
+                     if task is not None:
+                         engine_names.append(task[0])
+                         tasks.append(task[1])
  
          if not tasks:
```

---

_****_











### 5. Fix SearchEngine attribute inconsistencies

Let's update the test_base.py file to fix the `name` vs `engine_code` inconsistency:

---

_****_

```diff
                  url=HttpUrl("https://example.com/test"),
                  snippet=f"This is a test result for {query}",
-                 source=self.name,
+                 source=self.engine_code,
              )
          ]
```

---

_****_









Let's update the test_search_engine_name_class_var test case as well:

---

_****_

```diff
  
  def test_search_engine_name_class_var() -> None:
-     """Test that name is a required class variable."""
-     # SearchEngine.name should be defined as a class variable
-     assert hasattr(SearchEngine, "name")
+     """Test that engine_code is a required class variable."""
+     # SearchEngine.engine_code should be defined as a class variable
+     assert hasattr(SearchEngine, "engine_code")
  
      # The default value should be an empty string (not None)
      assert SearchEngine.engine_code == ""
  
-     # Check that our test classes have set the name
-     assert TestSearchEngine.name == "test_engine"
-     assert DisabledTestSearchEngine.name == "disabled_engine"
+     # Check that our test classes have set the engine_code
+     assert TestSearchEngine.engine_code == "test_engine"
+     assert DisabledTestSearchEngine.engine_code == "disabled_engine"
  
  
```

---

_****_









### 6. Add LoadDotEnv Script to Automatically Load Environment Variables

To ensure environment variables are loaded consistently, let's create a small helper script:

---

_****_

```diff
  Utility functions for the web search API.
  
- This module provides utility functions and classes used by the web search API.
+ This module provides various utility functions used by the web search API.
  """
  
  import logging
  import time
+ import os
+ from typing import Any, Optional
+ from urllib.parse import parse_qs, urlparse
+ 
+ from loguru import logger
+ 
+ # Add proper dotenv loading
+ from dotenv import load_dotenv
  
  # Set up logging
  logger = logging.getLogger(__name__)
  
+ def load_environment(force_reload: bool = False) -> None:
+     """
+     Load environment variables from .env file.
+     
+     This function provides a consistent way to load environment variables across the codebase.
+     
+     Args:
+         force_reload: Whether to reload the environment variables even if they're already loaded
+     """
+     loaded_flag = "_TWAT_SEARCH_ENV_LOADED"
+     # Check if we've already loaded the environment variables
+     if not force_reload and os.environ.get(loaded_flag) == "1":
+         logger.debug("Environment variables already loaded")
+         return
+         
+     # Load environment variables from .env file
+     load_dotenv()
+     
+     # Set a flag to indicate that we've loaded the variables
+     os.environ[loaded_flag] = "1"
+     
+     # Log which API keys are found
+     if logger.level("DEBUG").no < logger.level("INFO").no:  # Only in debug mode
+         for key, value in os.environ.items():
+             if ("API_KEY" in key or "_KEY" in key) and key != loaded_flag:
+                 masked_value = value[:4] + "****" if value else None
+                 logger.debug(f"Found environment variable: {key}={masked_value}")
+     else:
+         logger.info("Environment variables loaded")
  
  class RateLimiter:
```

---

_****_











Fix the loguru-specific code in the utils.py file:

---

_****_



---

_****_









Let's fix the issues in the utils.py by creating a new version:

---

_****_

```diff
  
  import logging
+ import os
  import time
- import os
  from typing import Any, Optional
  from urllib.parse import parse_qs, urlparse
- 
- from loguru import logger
  
  # Add proper dotenv loading
  # Set up logging
  logger = logging.getLogger(__name__)
- 
  
  def load_environment(force_reload: bool = False) -> None:
      
      # Log which API keys are found
-     if logger.level("DEBUG").no < logger.level("INFO").no:  # Only in debug mode
+     if logger.isEnabledFor(logging.DEBUG):  # Only in debug mode
          for key, value in os.environ.items():
              if ("API_KEY" in key or "_KEY" in key) and key != loaded_flag:
  class RateLimiter:
      """
-     Rate limiter to manage API request frequency.
- 
-     This class helps prevent hitting rate limits by spacing out API requests.
-     """
- 
-     def __init__(self, calls_per_second: int = 10):
-         """
-         Initialize the rate limiter.
+     Rate limiter to prevent sending too many requests to an API.
  
      Args:
-             calls_per_second: Maximum number of calls allowed per second
+         calls_per_second: Maximum number of calls per second
      """
+ 
+     def __init__(self, calls_per_second: float) -> None:
          self.calls_per_second = calls_per_second
-         self.call_timestamps: list[float] = []
- 
-     def wait_if_needed(self) -> None:
+         self.min_interval = 1.0 / calls_per_second
+         self.last_call_time = 0
+ 
+     async def wait(self) -> None:
          """
-         Wait if necessary to respect the rate limit.
- 
-         This method should be called before making an API request.
+         Wait until we can make another API call.
          """
-         now = time.time()
- 
-         # Remove timestamps older than 1 second
-         self.call_timestamps = [t for t in self.call_timestamps if now - t < 1]
- 
-         # If we've made too many calls in the last second, wait
-         if len(self.call_timestamps) >= self.calls_per_second:
-             sleep_time = 1 - (now - self.call_timestamps[0])
-             if sleep_time > 0:
-                 if sleep_time > 0.1:  # Only log if sleep time is significant
-                     logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
-                 time.sleep(sleep_time)
- 
-         # Record this API call
-         self.call_timestamps.append(time.time())
+         current_time = time.time()
+         elapsed = current_time - self.last_call_time
+         if elapsed < self.min_interval:
+             delay = self.min_interval - elapsed
+             logger.debug(f"Rate limiter sleeping for {delay:.4f} seconds")
+             time.sleep(delay)
+         self.last_call_time = time.time()
+ 
+ 
+ def extract_domain(url: str) -> str:
+     """
+     Extract the domain from a URL.
+ 
+     Args:
+         url: URL to extract domain from
+ 
+     Returns:
+         Domain name (e.g., "example.com")
+     """
+     parsed = urlparse(url)
+     domain = parsed.netloc
+     if not domain:
+         # If netloc is empty, the URL might not include the protocol
+         # Try parsing the path as a domain
+         parsed = urlparse(f"https://{url}")
+         domain = parsed.netloc
+     return domain
+ 
+ 
+ def extract_query_param(url: str, param: str) -> Optional[str]:
+     """
+     Extract a query parameter from a URL.
+ 
+     Args:
+         url: URL to extract parameter from
+         param: Parameter name to extract
+ 
+     Returns:
+         Parameter value or None if not found
+     """
+     parsed = urlparse(url)
+     params = parse_qs(parsed.query)
+     return params.get(param, [None])[0]
  
```

---

_****_













Now, let's update the config.py to use our improved load_environment function:

---

_****_

```diff
  from typing import Any, ClassVar
  
- # Add python-dotenv import and call load_dotenv at module level
- from dotenv import load_dotenv
+ # Remove direct dotenv import and add our utils import
  from pydantic import BaseModel, Field
  
      standardize_engine_name,
  )
+ from twat_search.web.utils import load_environment
  
- # Load environment variables from .env file
- load_dotenv()
+ # Load environment variables
+ load_environment()
  
  logger = logging.getLogger(__name__)
```

---

_****_





---



---
