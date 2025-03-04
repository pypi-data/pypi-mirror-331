## SpecStory

## Update config.py to Use Engine Constants (26/02/2025, 12:11:22)

_**User**_

In @config.py use constants defined in @__init__.py  

---

_**Assistant**_

<think>The user wants me to update the `config.py` file to use constants defined in the `__init__.py` file for the engine names, rather than using string literals. Looking at the two files:

1. `src/twat_search/web/engines/__init__.py` defines engine name constants like `BRAVE`, `BRAVE_NEWS`, etc.
2. `src/twat_search/web/config.py` uses string literals like `"brave"`, `"brave_news"` in the `DEFAULT_CONFIG` dictionary.

The task is to replace these string literals with the constants defined in `__init__.py`. This will make the code more maintainable and less prone to errors from typos.

Looking at the linter errors, there are some issues with the `__init__.py` file, including undefined variables in `__all__` and some type incompatibilities. However, our primary task is to update `config.py` to use the constants from `__init__.py`, not to fix all the linter errors in the `__init__.py` file.

Let's proceed by updating the `config.py` file to use the constants from `__init__.py`.</think>I'll update the `config.py` file to use the engine name constants defined in `engines/__init__.py` instead of string literals in the `DEFAULT_CONFIG` dictionary. This will make the code more maintainable and reduce the risk of typos.

Let me first search for the relevant code in the engines module to identify the constants:

---

_****_

<details>
            <summary>Searched codebase "engine name constants in twat_search.web.engines" • **24** results</summary>
        
| File | Lines |
|------|-------|
| `src/twat_search/web/engines/__init__.py` | L28-81 |
| `src/twat_search/web/engines/__init__.py` | L81-151 |
| `src/twat_search/web/engines/__init__.py` | L346-355 |
| `src/twat_search/web/engines/__init__.py` | L1-28 |
| `src/twat_search/web/engines/base.py` | L67-105 |
| `src/twat_search/web/engines/base.py` | L105-125 |
| `src/twat_search/web/engines/__init__.py` | L331-346 |
| `src/twat_search/web/engines/brave.py` | L138-147 |
| `twat_search.txt` | L487-524 |
| `src/twat_search/web/engines/searchit.py` | L1-25 |
| `src/twat_search/web/engines/base.py` | L125-135 |
| `src/twat_search/web/engines/__init__.py` | L355-367 |
| `src/twat_search/web/engines/base.py` | L1-54 |
| `src/twat_search/web/engines/__init__.py` | L151-219 |
| `src/twat_search/web/engines/anywebsearch.py` | L1-25 |
| `src/twat_search/web/cli.py` | L97-137 |
| `src/twat_search/web/engines/searchit.py` | L675-717 |
| `twat_search.txt` | L1164-1200 |
| `src/twat_search/web/exceptions.py` | L21-36 |
| `src/twat_search/web/engines/__init__.py` | L278-331 |
| `twat_search.txt` | L1040-1074 |
| `src/twat_search/web/engines/brave.py` | L147-156 |
| `src/twat_search/web/engines/anywebsearch.py` | L645-678 |
| `twat_search.txt` | L1231-1271 |

</details>

---

_****_



Now, I'll look at the config file to understand how I need to update it:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_



Now that I have a good understanding of both files, I'll update the `config.py` file to use the engine name constants defined in `engines/__init__.py` instead of string literals in the `DEFAULT_CONFIG` dictionary.

---

_****_

```diff
  
  from pydantic import BaseModel, Field
+ 
+ # Import engine name constants
+ from .engines import (
+     BING_SCRAPER, BRAVE, BRAVE_NEWS, CRITIQUE, DUCKDUCKGO,
+     GOOGLE_HASDATA, GOOGLE_SERPAPI, PPLX, TAVILY, YOU, YOU_NEWS
+ )
  
  logger = logging.getLogger(__name__)
      "engines": {
          # Brave Search
-         "brave": {
+         BRAVE: {
              "enabled": True,
              "api_key": None,
              },
          },
-         "brave_news": {
+         BRAVE_NEWS: {
              "enabled": True,
              "api_key": None,
          },
          # SerpAPI (Google)
-         "serpapi": {
+         GOOGLE_SERPAPI: {
              "enabled": True,
              "api_key": None,
          },
          # Tavily Search
-         "tavily": {
+         TAVILY: {
              "enabled": True,
              "api_key": None,
          },
          # Perplexity AI
-         "pplx": {
+         PPLX: {
              "enabled": True,
              "api_key": None,
          },
          # You.com Search
-         "you": {
+         YOU: {
              "enabled": True,
              "api_key": None,
              "default_params": {},
          },
-         "you_news": {
+         YOU_NEWS: {
              "enabled": True,
              "api_key": None,
              "default_params": {},
          },
          # Critique Labs
-         "critique": {
+         CRITIQUE: {
              "enabled": True,
              "api_key": None,
          },
          # DuckDuckGo
-         "duckduckgo": {
+         DUCKDUCKGO: {
              "enabled": True,
              "api_key": None,  # DuckDuckGo doesn't require an API key
              "default_params": {"timeout": 10},
          },
          # Bing Scraper
-         "bing_scraper": {
+         BING_SCRAPER: {
              "enabled": True,
              "api_key": None,  # No API key required, it's a scraper
              "default_params": {"num_pages": 1, "delay": 0.5},
          },
          # HasData Google
-         "hasdata_google": {
+         GOOGLE_HASDATA: {
              "enabled": True,
              "api_key": None,
```

---

_****_



I need to fix the issue with `hasdata_google_light` too. Looking at the linter errors, there seems to be an issue with the `hasdata_google_light` constant in the `__init__.py` file. Let me check the hasdata module to see what's available:

---

_****_

<details>
            <summary>Grep search for "GOOGLE_HASDATA_FULL|GOOGLE_HASDATA_LIGHT|hasdata_google_light" • **14** files</summary>
        
| File | Line | Match |
|------|------|-------|
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/CLEANUP.txt` | L1546 | `1166 |     async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/CLEANUP.txt` | L1824 | `110 |         hasdata_google_light,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/config.py` | L129 | `"hasdata_google_light": {` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/cli.py` | L119 | `engines = ["duckduckgo", "hasdata_google_light"]` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/cli.py` | L1206 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/twat_search.txt` | L799 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/twat_search.txt` | L1263 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L24 | `hasdata_google_light,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L28 | `available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L34 | `"hasdata_google_light",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L740 | `- HASDATA_GOOGLE_LIGHT = "hasdata-google-light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L742 | `+ HASDATA_GOOGLE_LIGHT = "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L748 | `-     available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L750 | `+     available_engine_functions["hasdata_google_light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L813 | `+                 engines = ["duckduckgo", "hasdata_google_light"]` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L1065 | `+         "hasdata_google_light": {` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L2587 | `"HASDATA_GOOGLE_LIGHT",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L2927 | `HASDATA_GOOGLE_LIGHT = "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L2937 | `HASDATA_GOOGLE_LIGHT,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L2948 | `HASDATA_GOOGLE_LIGHT: "HasData Google Light",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L3778 | `hasdata_google_light': Unknown search engine: hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L3827 | `type': 'desktop'}), 'hasdata_google_light': EngineConfig(enabled=T` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L4983 | `ogle_scraper', 'hasdata', 'hasdata_google', 'hasdata_google_light'` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_10-55-standardizing-engine-naming-conventions.md` | L5028 | `hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L814 | `10. hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L1324 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L1345 | `Finally, let's update the hasdata_google_light method:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L2700 | `- hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L2795 | `- hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L2886 | `⟪ 104 characters skipped ⟫ch/twat_search.txt` | L799 | `async def hasdata_google_light(` |` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L2917 | `⟪ 105 characters skipped ⟫h/twat_search.txt` | L1263 | `async def hasdata_google_light(` |` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L3132 | `+ HASDATA_GOOGLE_LIGHT = "hasdata-google-light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L3147 | `+     HASDATA_GOOGLE_LIGHT,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L3162 | `+     HASDATA_GOOGLE_LIGHT: "HasData Google Light",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_09-54-implementing-plain-option-for-search-commands.md` | L3171 | `+     "CRITIQUE", "DUCKDUCKGO", "BING_SCRAPER", "HASDATA_GOOGLE", "HASDATA_GOOGLE_LIGHT",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_11-30-untitled.md` | L32 | `HASDATA_GOOGLE_LIGHT = "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-26_11-30-untitled.md` | L48 | `- "hasdata_google_light" = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L18 | `GOOGLE_HASDATA_FULL)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L174 | `engine_code = GOOGLE_HASDATA_FULL` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L175 | `friendly_engine_name = ENGINE_FRIENDLY_NAMES[GOOGLE_HASDATA_FULL]` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L507 | `+ async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L555 | `+         hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L559 | `+     available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L564 | `+         "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L733 | `- Helper functions `hasdata_google()` and `hasdata_google_light()`` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L751 | `from twat_search.web.engines import hasdata_google, hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L762 | `results = await hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L810 | `name = "hasdata_google_light"  # Using underscore` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L818 | `available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L852 | `-     name = "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L882 | `-     available_engine_functions["hasdata_google_light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L884 | `+     available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L1146 | `105 |         hasdata_google_light,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L1392 | `+     async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L1468 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L3025 | `800 |     async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L6887 | `- `hasdata_google_light` method` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L7176 | `hasdata_google_light() - Search using HasData Google SERP Light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L7192 | `hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history/2025-02-25_07-34-integrating-hasdata-google-serp-apis.md` | L7193 | `results = await hasdata_google_light("your search query")` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L42 | `GOOGLE_HASDATA_FULL = "google_hasdata_full"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L67 | `GOOGLE_HASDATA_FULL,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L93 | `GOOGLE_HASDATA_FULL: "Full Google scraper via HasData with API key",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L118 | `"HASDATA_GOOGLE_LIGHT",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L282 | `hasdata_google, hasdata_google_light)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L285 | `available_engine_functions["hasdata_google_light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L291 | `"hasdata_google_light",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41496 | `+ async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41544 | `+         hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41548 | `+     available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41553 | `+         "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41722 | `- Helper functions `hasdata_google()` and `hasdata_google_light()`` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41740 | `from twat_search.web.engines import hasdata_google, hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41751 | `results = await hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41799 | `name = "hasdata_google_light"  # Using underscore` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41807 | `available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41841 | `-     name = "hasdata_google_light"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41871 | `-     available_engine_functions["hasdata_google_light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L41873 | `+     available_engine_functions["hasdata-google-light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L42135 | `105 |         hasdata_google_light,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L42381 | `+     async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L42457 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L44014 | `800 |     async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L47876 | `- `hasdata_google_light` method` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L48165 | `hasdata_google_light() - Search using HasData Google SERP Light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L48181 | `hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L48182 | `results = await hasdata_google_light("your search query")` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L52567 | `10. hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L53077 | `async def hasdata_google_light(` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/.specstory/history.txt` | L53098 | `Finally, let's update the hasdata_google_light method:` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L18 | `GOOGLE_HASDATA_FULL)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L174 | `engine_code = GOOGLE_HASDATA_FULL` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/hasdata.py` | L175 | `friendly_engine_name = ENGINE_FRIENDLY_NAMES[GOOGLE_HASDATA_FULL]` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L42 | `GOOGLE_HASDATA_FULL = "google_hasdata_full"` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L67 | `GOOGLE_HASDATA_FULL,` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L93 | `GOOGLE_HASDATA_FULL: "Full Google scraper via HasData with API key",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L118 | `"HASDATA_GOOGLE_LIGHT",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L282 | `hasdata_google, hasdata_google_light)` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L285 | `available_engine_functions["hasdata_google_light"] = hasdata_google_light` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/engines/__init__.py` | L291 | `"hasdata_google_light",` |
| `file:///Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/web/config.py` | L129 | `"hasdata_google_light": {` |

</details>

---

_****_





Let me look at the hasdata.py file to better understand the constants:

---

_****_

Read file: src/twat_search/web/engines/hasdata.py

---

_****_



I notice from the linter errors and the file inspection that there's a discrepancy in naming. In the `__init__.py` file, we have:

1. `GOOGLE_HASDATA` - for light Google scraper via HasData
2. `GOOGLE_HASDATA_FULL` - for full Google scraper via HasData

But in the config.py, we have:
1. `"hasdata_google"` - mapped to `GOOGLE_HASDATA`
2. `"hasdata_google_light"` - which should be using `GOOGLE_HASDATA` too (based on the hasdata.py file)

Let me update the config.py file to correctly use the constants:

---

_****_

```diff
      DUCKDUCKGO,
      GOOGLE_HASDATA,
+     GOOGLE_HASDATA_FULL,
      GOOGLE_SERPAPI,
      PPLX,
              "default_params": {"num_pages": 1, "delay": 0.5},
          },
-         # HasData Google
-         GOOGLE_HASDATA: {
+         # HasData Google (Full version)
+         GOOGLE_HASDATA_FULL: {
              "enabled": True,
              "api_key": None,
              },
          },
-         "hasdata_google_light": {
+         # HasData Google (Light version)
+         GOOGLE_HASDATA: {
              "enabled": True,
              "api_key": None,
```

---

_****_





Now let's run the linter to see if we've resolved the issues:

---

_****_

```bash
cd /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search && ruff check --output-format=github --fix --unsafe-fixes . && ruff format --respect-gitignore --target-version py312 .
```

```
src/twat_search/web/cli.py:700:9: FBT002 Boolean default positional argument in
function definition                                 ::error title=Ruff (PLR0913)
,file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=759,col=15,endLine=759,endColumn=20::src/twat_search/web/cli.py
:759:15: PLR0913 Too many arguments in function definition (10 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=765,col=9,endLine=765,endColumn=20::src/twat_search/web/cli.py:7
65:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=768,col=9,endLine=768,endColumn=16::src/twat_search/web/cli.py:7
68:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=768,col=9,endLine=768,endColumn=16::src/twat_search/web/cli.py:7
68:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=769,col=9,endLine=769,endColumn=13::src/twat_search/web/cli.py:7
69:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=769,col=9,endLine=769,endColumn=13::src/twat_search/web/cli.py:7
69:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=770,col=9,endLine=770,endColumn=14::src/twat_search/web/cli.py:7
70:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=770,col=9,endLine=770,endColumn=14::src/twat_search/web/cli.py:7
70:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=807,col=15,endLine=807,endColumn=25::src/twat_search/web/cli.py
:807:15: PLR0913 Too many arguments in function definition (10 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=813,col=9,endLine=813,endColumn=20::src/twat_search/web/cli.py:8
13:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=816,col=9,endLine=816,endColumn=16::src/twat_search/web/cli.py:8
16:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=816,col=9,endLine=816,endColumn=16::src/twat_search/web/cli.py:8
16:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=817,col=9,endLine=817,endColumn=13::src/twat_search/web/cli.py:8
17:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=817,col=9,endLine=817,endColumn=13::src/twat_search/web/cli.py:8
17:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=818,col=9,endLine=818,endColumn=14::src/twat_search/web/cli.py:8
18:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=818,col=9,endLine=818,endColumn=14::src/twat_search/web/cli.py:8
18:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=857,col=15,endLine=857,endColumn=22::src/twat_search/web/cli.py
:857:15: PLR0913 Too many arguments in function definition (10 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=863,col=9,endLine=863,endColumn=20::src/twat_search/web/cli.py:8
63:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=866,col=9,endLine=866,endColumn=16::src/twat_search/web/cli.py:8
66:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=866,col=9,endLine=866,endColumn=16::src/twat_search/web/cli.py:8
66:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=867,col=9,endLine=867,endColumn=13::src/twat_search/web/cli.py:8
67:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=867,col=9,endLine=867,endColumn=13::src/twat_search/web/cli.py:8
67:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=868,col=9,endLine=868,endColumn=14::src/twat_search/web/cli.py:8
68:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=868,col=9,endLine=868,endColumn=14::src/twat_search/web/cli.py:8
68:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=905,col=15,endLine=905,endColumn=21::src/twat_search/web/cli.py
:905:15: PLR0913 Too many arguments in function definition (13 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=911,col=9,endLine=911,endColumn=20::src/twat_search/web/cli.py:9
11:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=917,col=9,endLine=917,endColumn=16::src/twat_search/web/cli.py:9
17:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=917,col=9,endLine=917,endColumn=16::src/twat_search/web/cli.py:9
17:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=918,col=9,endLine=918,endColumn=13::src/twat_search/web/cli.py:9
18:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=918,col=9,endLine=918,endColumn=13::src/twat_search/web/cli.py:9
18:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=919,col=9,endLine=919,endColumn=14::src/twat_search/web/cli.py:9
19:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=919,col=9,endLine=919,endColumn=14::src/twat_search/web/cli.py:9
19:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=967,col=15,endLine=967,endColumn=19::src/twat_search/web/cli.py
:967:15: PLR0913 Too many arguments in function definition (11 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=973,col=9,endLine=973,endColumn=20::src/twat_search/web/cli.py:9
73:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=977,col=9,endLine=977,endColumn=16::src/twat_search/web/cli.py:9
77:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=977,col=9,endLine=977,endColumn=16::src/twat_search/web/cli.py:9
77:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=978,col=9,endLine=978,endColumn=13::src/twat_search/web/cli.py:9
78:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=978,col=9,endLine=978,endColumn=13::src/twat_search/web/cli.py:9
78:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=979,col=9,endLine=979,endColumn=14::src/twat_search/web/cli.py:9
79:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=979,col=9,endLine=979,endColumn=14::src/twat_search/web/cli.py:9
79:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=1017,col=15,endLine=1017,endColumn=18::src/twat_search/web/cli.
py:1017:15: PLR0913 Too many arguments in function definition (10 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1023,col=9,endLine=1023,endColumn=20::src/twat_search/web/cli.py
:1023:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1026,col=9,endLine=1026,endColumn=16::src/twat_search/web/cli.py
:1026:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1026,col=9,endLine=1026,endColumn=16::src/twat_search/web/cli.py
:1026:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1027,col=9,endLine=1027,endColumn=13::src/twat_search/web/cli.py
:1027:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1027,col=9,endLine=1027,endColumn=13::src/twat_search/web/cli.py
:1027:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1028,col=9,endLine=1028,endColumn=14::src/twat_search/web/cli.py
:1028:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1028,col=9,endLine=1028,endColumn=14::src/twat_search/web/cli.py
:1028:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=1064,col=15,endLine=1064,endColumn=23::src/twat_search/web/cli.
py:1064:15: PLR0913 Too many arguments in function definition (10 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1070,col=9,endLine=1070,endColumn=20::src/twat_search/web/cli.py
:1070:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1073,col=9,endLine=1073,endColumn=16::src/twat_search/web/cli.py
:1073:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1073,col=9,endLine=1073,endColumn=16::src/twat_search/web/cli.py
:1073:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1074,col=9,endLine=1074,endColumn=13::src/twat_search/web/cli.py
:1074:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1074,col=9,endLine=1074,endColumn=13::src/twat_search/web/cli.py
:1074:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1075,col=9,endLine=1075,endColumn=14::src/twat_search/web/cli.py
:1075:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1075,col=9,endLine=1075,endColumn=14::src/twat_search/web/cli.py
:1075:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=1113,col=15,endLine=1113,endColumn=25::src/twat_search/web/cli.
py:1113:15: PLR0913 Too many arguments in function definition (11 > 5)
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1118,col=9,endLine=1118,endColumn=17::src/twat_search/web/cli.py
:1118:9: ARG002 Unused method argument: `language`
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1119,col=9,endLine=1119,endColumn=20::src/twat_search/web/cli.py
:1119:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1123,col=9,endLine=1123,endColumn=16::src/twat_search/web/cli.py
:1123:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1123,col=9,endLine=1123,endColumn=16::src/twat_search/web/cli.py
:1123:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1124,col=9,endLine=1124,endColumn=13::src/twat_search/web/cli.py
:1124:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1124,col=9,endLine=1124,endColumn=13::src/twat_search/web/cli.py
:1124:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1125,col=9,endLine=1125,endColumn=14::src/twat_search/web/cli.py
:1125:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1125,col=9,endLine=1125,endColumn=14::src/twat_search/web/cli.py
:1125:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=1164,col=15,endLine=1164,endColumn=29::src/twat_search/web/cli.
py:1164:15: PLR0913 Too many arguments in function definition (8 > 5)
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1171,col=9,endLine=1171,endColumn=16::src/twat_search/web/cli.py
:1171:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1171,col=9,endLine=1171,endColumn=16::src/twat_search/web/cli.py
:1171:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1172,col=9,endLine=1172,endColumn=13::src/twat_search/web/cli.py
:1172:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1172,col=9,endLine=1172,endColumn=13::src/twat_search/web/cli.py
:1172:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1173,col=9,endLine=1173,endColumn=14::src/twat_search/web/cli.py
:1173:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1173,col=9,endLine=1173,endColumn=14::src/twat_search/web/cli.py
:1173:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/cli.py,line=1207,col=15,endLine=1207,endColumn=35::src/twat_search/web/cli.
py:1207:15: PLR0913 Too many arguments in function definition (7 > 5)
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1213,col=9,endLine=1213,endColumn=16::src/twat_search/web/cli.py
:1213:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1213,col=9,endLine=1213,endColumn=16::src/twat_search/web/cli.py
:1213:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1214,col=9,endLine=1214,endColumn=13::src/twat_search/web/cli.py
:1214:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1214,col=9,endLine=1214,endColumn=13::src/twat_search/web/cli.py
:1214:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1215,col=9,endLine=1215,endColumn=14::src/twat_search/web/cli.py
:1215:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1215,col=9,endLine=1215,endColumn=14::src/twat_search/web/cli.py
:1215:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (ARG005),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/cli.py,line=1249,col=39,endLine=1249,endColumn=42::src/twat_search/web/cli.p
y:1249:39: ARG005 Unused lambda argument: `out`
                        ::error title=Ruff (E402),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/config.py,line=151,col=1,endLine=151,endColumn=45::src/twat_search/web/config.
py:151:1: E402 Module level import not at top of file
                        ::error title=Ruff (C901),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/config.py,line=213,col=9,endLine=213,endColumn=29::src/twat_search/web/config.
py:213:9: C901 `_apply_env_overrides` is too complex (14 > 10)
                        ::error title=Ruff (PLR0912),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/config.py,line=213,col=9,endLine=213,endColumn=29::src/twat_search/web/conf
ig.py:213:9: PLR0912 Too many branches (13 > 12)
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/config.py,line=294,col=9,endLine=294,endColumn=16::src/twat_search/web/confi
g.py:294:9: FBT001 Boolean-typed positional argument in function definition
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/config.py,line=294,col=9,endLine=294,endColumn=16::src/twat_search/web/confi
g.py:294:9: FBT002 Boolean default positional argument in function definition
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=10,col=8,endLine=10,endColumn=15::src/twat_search/web
/engines/__init__.py:10:8: F401 `logging` imported but unused
                        ::error title=Ruff (UP035),file=/Users/adam/Developer/vc
s/github.t
wardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/w
eb/engines/__init__.py,line=12,col=1,endLine=12,endColumn=64::src/twat_search/we
b/engines/__init__.py:12:1: UP035 `typing.Dict` is deprecated, use `dict` instea
d                       ::error title=Ruff (UP035),file=/Users/adam/Developer/vc
s/github.t
wardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/w
eb/engines/__init__.py,line=12,col=1,endLine=12,endColumn=64::src/twat_search/we
b/engines/__init__.py:12:1: UP035 `typing.List` is deprecated, use `list` instea
d                       ::error title=Ruff (UP035),file=/Users/adam/Developer/vc
s/github.t
wardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/w
eb/engines/__init__.py,line=12,col=1,endLine=12,endColumn=64::src/twat_search/we
b/engines/__init__.py:12:1: UP035 `typing.Set` is deprecated, use `set` instead
                        ::error title=Ruff (UP035),file=/Users/adam/Developer/vc
s/github.t
wardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/w
eb/engines/__init__.py,line=12,col=1,endLine=12,endColumn=64::src/twat_search/we
b/engines/__init__.py:12:1: UP035 `typing.Tuple` is deprecated, use `tuple` inst
ead                     ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=25,endLine=12,endColumn=29::src/twat_search/we
b/engines/__init__.py:12:25: F401 `typing.Dict` imported but unused
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=31,endLine=12,endColumn=35::src/twat_search/we
b/engines/__init__.py:12:31: F401 `typing.List` imported but unused
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=37,endLine=12,endColumn=45::src/twat_search/we
b/engines/__init__.py:12:37: F401 `typing.Optional` imported but unused
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=47,endLine=12,endColumn=50::src/twat_search/we
b/engines/__init__.py:12:47: F401 `typing.Set` imported but unused
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=52,endLine=12,endColumn=57::src/twat_search/we
b/engines/__init__.py:12:52: F401 `typing.Tuple` imported but unused
                        ::error title=Ruff (F401),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/__init__.py,line=12,col=59,endLine=12,endColumn=64::src/twat_search/we
b/engines/__init__.py:12:59: F401 `typing.Union` imported but unused
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/__init__.py,line=259,col=36,endLine=259,endColumn=41::src/twat_searc
h/web/engines/__init__.py:259:36: ARG002 Unused method argument: `query`
                        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/anywebsearch.py,line=55,col=13,endLine=55,endColumn=18::src/twat_sea
rch/web/engines/anywebsearch.py:55:13: FBT001 Boolean-typed positional argument
in function definition  ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/anywebsearch.py,line=55,col=13,endLine=55,endColumn=18::src/twat_sea
rch/web/engines/anywebsearch.py:55:13: FBT002 Boolean default positional argumen
t in function definition::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/anywebsearch.py,line=134,col=9,endLine=134,endColumn=17::src/twat_s
earch/web/engines/anywebsearch.py:134:9: PLR0913 Too many arguments in function
definition (6 > 5)      ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/anywebsearch.py,line=140,col=9,endLine=140,endColumn=20::src/twat_se
arch/web/engines/anywebsearch.py:140:9: FBT002 Boolean default positional argume
nt in function definition
          ::error title=Ruff (ARG002),file=/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/bing_scraper.py,line=45,col=26,endLine=45,endColumn=31::src/twat_sea
rch/web/engines/bing_scraper.py:45:26: ARG002 Unused method argument: `query`
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/bing_scraper.py,line=45,col=38,endLine=45,endColumn=49::src/twat_sea
rch/web/engines/bing_scraper.py:45:38: ARG002 Unused method argument: `num_resul
ts`                     ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/bing_scraper.py,line=105,col=9,endLine=105,endColumn=17::src/twat_s
earch/web/engines/bing_scraper.py:105:9: PLR0913 Too many arguments in function
definition (6 > 5)      ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/bing_scraper.py,line=111,col=9,endLine=111,endColumn=20::src/twat_se
arch/web/engines/bing_scraper.py:111:9: FBT002 Boolean default positional argume
nt in function definition
          ::error title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/brave.py,line=36,col=9,endLine=36,endColumn=17::src/twat_search/web
/engines/brave.py:36:9: PLR0913 Too many arguments in function definition (6 > 5
)                       ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/brave.py,line=42,col=9,endLine=42,endColumn=20::src/twat_search/web/
engines/brave.py:42:9: FBT002 Boolean default positional argument in function de
finition                ::error title=Ruff (C901),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/brave.py,line=77,col=15,endLine=77,endColumn=21::src/twat_search/web/e
ngines/brave.py:77:15: C901 `search` is too complex (12 > 10)
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/brave.py,line=159,col=11,endLine=159,endColumn=16::src/twat_search/
web/engines/brave.py:159:11: PLR0913 Too many arguments in function definition (
7 > 5)                  ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/brave.py,line=164,col=5,endLine=164,endColumn=16::src/twat_search/we
b/engines/brave.py:164:5: FBT002 Boolean default positional argument in function
 definition             ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/brave.py,line=195,col=11,endLine=195,endColumn=21::src/twat_search/
web/engines/brave.py:195:11: PLR0913 Too many arguments in function definition (
7 > 5)                  ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/brave.py,line=200,col=5,endLine=200,endColumn=16::src/twat_search/we
b/engines/brave.py:200:5: FBT002 Boolean default positional argument in function
 definition             ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/critique.py,line=54,col=9,endLine=54,endColumn=17::src/twat_search/
web/engines/critique.py:54:9: PLR0913 Too many arguments in function definition
(11 > 5)                ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/critique.py,line=60,col=9,endLine=60,endColumn=20::src/twat_search/w
eb/engines/critique.py:60:9: FBT002 Boolean default positional argument in funct
ion definition          ::error title=Ruff (B904),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/critique.py,line=109,col=13,endLine=109,endColumn=81::src/twat_search/
web/engines/critique.py:109:13: B904 Within an `except` clause, raise exceptions
 with `raise ... from err` or `raise ... from None` to distinguish them from err
ors in exception handling                                                   ::er
ror title=Ruff (B904),file=/Users/adam/Developer/vcs/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/critique.py,line=111,col=13,endLine=111,endColumn=73::src/twat_search/
web/engines/critique.py:111:13: B904 Within an `except` clause, raise exceptions
 with `raise ... from err` or `raise ... from None` to distinguish them from err
ors in exception handling                                                   ::er
ror title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/critique.py,line=215,col=11,endLine=215,endColumn=19::src/twat_sear
ch/web/engines/critique.py:215:11: PLR0913 Too many arguments in function defini
tion (12 > 5)           ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/critique.py,line=220,col=5,endLine=220,endColumn=16::src/twat_search
/web/engines/critique.py:220:5: FBT002 Boolean default positional argument in fu
nction definition       ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/duckduckgo.py,line=47,col=9,endLine=47,endColumn=17::src/twat_searc
h/web/engines/duckduckgo.py:47:9: PLR0913 Too many arguments in function definit
ion (6 > 5)             ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/duckduckgo.py,line=53,col=9,endLine=53,endColumn=20::src/twat_search
/web/engines/duckduckgo.py:53:9: FBT002 Boolean default positional argument in f
unction definition      ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/duckduckgo.py,line=87,col=9,endLine=87,endColumn=25::src/twat_searc
h/web/engines/duckduckgo.py:87:9: PLR0913 Too many arguments in function definit
ion (7 > 5)             ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/duckduckgo.py,line=175,col=11,endLine=175,endColumn=21::src/twat_se
arch/web/engines/duckduckgo.py:175:11: PLR0913 Too many arguments in function de
finition (8 > 5)        ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/duckduckgo.py,line=180,col=5,endLine=180,endColumn=16::src/twat_sear
ch/web/engines/duckduckgo.py:180:5: FBT001 Boolean-typed positional argument in
function definition     ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/duckduckgo.py,line=180,col=5,endLine=180,endColumn=16::src/twat_sear
ch/web/engines/duckduckgo.py:180:5: FBT002 Boolean default positional argument i
n function definition   ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/google_scraper.py,line=103,col=9,endLine=103,endColumn=17::src/twat
_search/web/engines/google_scraper.py:103:9: PLR0913 Too many arguments in funct
ion definition (6 > 5)  ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/google_scraper.py,line=109,col=9,endLine=109,endColumn=20::src/twat_
search/web/engines/google_scraper.py:109:9: FBT002 Boolean default positional ar
gument in function definition
          ::error title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/google_scraper.py,line=296,col=11,endLine=296,endColumn=25::src/twa
t_search/web/engines/google_scraper.py:296:11: PLR0913 Too many arguments in fun
ction definition (9 > 5)::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/google_scraper.py,line=301,col=5,endLine=301,endColumn=16::src/twat_
search/web/engines/google_scraper.py:301:5: FBT001 Boolean-typed positional argu
ment in function definition
          ::error title=Ruff (FBT002),file=/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/google_scraper.py,line=301,col=5,endLine=301,endColumn=16::src/twat_
search/web/engines/google_scraper.py:301:5: FBT002 Boolean default positional ar
gument in function definition
          ::error title=Ruff (FBT001),file=/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/google_scraper.py,line=305,col=5,endLine=305,endColumn=11::src/twat_
search/web/engines/google_scraper.py:305:5: FBT001 Boolean-typed positional argu
ment in function definition
          ::error title=Ruff (FBT002),file=/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/google_scraper.py,line=305,col=5,endLine=305,endColumn=11::src/twat_
search/web/engines/google_scraper.py:305:5: FBT002 Boolean default positional ar
gument in function definition
          ::error title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/pplx.py,line=44,col=9,endLine=44,endColumn=17::src/twat_search/web/
engines/pplx.py:44:9: PLR0913 Too many arguments in function definition (7 > 5)
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/pplx.py,line=50,col=9,endLine=50,endColumn=20::src/twat_search/web/e
ngines/pplx.py:50:9: FBT002 Boolean default positional argument in function defi
nition                  ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/pplx.py,line=137,col=11,endLine=137,endColumn=15::src/twat_search/w
eb/engines/pplx.py:137:11: PLR0913 Too many arguments in function definition (8
> 5)                    ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/pplx.py,line=142,col=5,endLine=142,endColumn=16::src/twat_search/web
/engines/pplx.py:142:5: FBT002 Boolean default positional argument in function d
efinition               ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=54,col=13,endLine=54,endColumn=21::src/twat_search
/web/engines/searchit.py:54:13: PLR0913 Too many arguments in function definitio
n (7 > 5)               ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/searchit.py,line=96,col=32,endLine=96,endColumn=39::src/twat_search/
web/engines/searchit.py:96:32: ARG002 Unused method argument: `request`
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/searchit.py,line=120,col=32,endLine=120,endColumn=39::src/twat_searc
h/web/engines/searchit.py:120:32: ARG002 Unused method argument: `request`
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/searchit.py,line=144,col=32,endLine=144,endColumn=39::src/twat_searc
h/web/engines/searchit.py:144:32: ARG002 Unused method argument: `request`
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/searchit.py,line=168,col=32,endLine=168,endColumn=39::src/twat_searc
h/web/engines/searchit.py:168:32: ARG002 Unused method argument: `request`
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=232,col=9,endLine=232,endColumn=17::src/twat_searc
h/web/engines/searchit.py:232:9: PLR0913 Too many arguments in function definiti
on (6 > 5)              ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/searchit.py,line=238,col=9,endLine=238,endColumn=20::src/twat_search
/web/engines/searchit.py:238:9: FBT002 Boolean default positional argument in fu
nction definition       ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=679,col=11,endLine=679,endColumn=26::src/twat_sear
ch/web/engines/searchit.py:679:11: PLR0913 Too many arguments in function defini
tion (6 > 5)            ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=720,col=11,endLine=720,endColumn=26::src/twat_sear
ch/web/engines/searchit.py:720:11: PLR0913 Too many arguments in function defini
tion (6 > 5)            ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=761,col=11,endLine=761,endColumn=25::src/twat_sear
ch/web/engines/searchit.py:761:11: PLR0913 Too many arguments in function defini
tion (6 > 5)            ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/searchit.py,line=802,col=11,endLine=802,endColumn=24::src/twat_sear
ch/web/engines/searchit.py:802:11: PLR0913 Too many arguments in function defini
tion (6 > 5)            ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/serpapi.py,line=53,col=9,endLine=53,endColumn=17::src/twat_search/w
eb/engines/serpapi.py:53:9: PLR0913 Too many arguments in function definition (6
 > 5)                   ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/serpapi.py,line=59,col=9,endLine=59,endColumn=20::src/twat_search/we
b/engines/serpapi.py:59:9: FBT002 Boolean default positional argument in functio
n definition            ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/serpapi.py,line=170,col=11,endLine=170,endColumn=25::src/twat_searc
h/web/engines/serpapi.py:170:11: PLR0913 Too many arguments in function definiti
on (8 > 5)              ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/serpapi.py,line=175,col=5,endLine=175,endColumn=16::src/twat_search/
web/engines/serpapi.py:175:5: FBT002 Boolean default positional argument in func
tion definition         ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/tavily.py,line=57,col=9,endLine=57,endColumn=17::src/twat_search/we
b/engines/tavily.py:57:9: PLR0913 Too many arguments in function definition (12
> 5)                    ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=63,col=9,endLine=63,endColumn=20::src/twat_search/web
/engines/tavily.py:63:9: FBT002 Boolean default positional argument in function
definition              ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=68,col=9,endLine=68,endColumn=23::src/twat_search/web
/engines/tavily.py:68:9: FBT001 Boolean-typed positional argument in function de
finition                ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=68,col=9,endLine=68,endColumn=23::src/twat_search/web
/engines/tavily.py:68:9: FBT002 Boolean default positional argument in function
definition              ::error title=Ruff (FBT003),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=96,col=77,endLine=96,endColumn=82::src/twat_search/we
b/engines/tavily.py:96:77: FBT003 Boolean positional value in function call
                        ::error title=Ruff (B904),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/tavily.py,line=175,col=17,endLine=175,endColumn=65::src/twat_search/we
b/engines/tavily.py:175:17: B904 Within an `except` clause, raise exceptions wit
h `raise ... from err` or `raise ... from None` to distinguish them from errors
in exception handling                                                       ::er
ror title=Ruff (B904),file=/Users/adam/Developer/vcs/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/tavily.py,line=177,col=17,endLine=177,endColumn=68::src/twat_search/we
b/engines/tavily.py:177:17: B904 Within an `except` clause, raise exceptions wit
h `raise ... from err` or `raise ... from None` to distinguish them from errors
in exception handling                                                       ::er
ror title=Ruff (B904),file=/Users/adam/Developer/vcs/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/engines/tavily.py,line=179,col=17,endLine=179,endColumn=62::src/twat_search/we
b/engines/tavily.py:179:17: B904 Within an `except` clause, raise exceptions wit
h `raise ... from err` or `raise ... from None` to distinguish them from errors
in exception handling                                                       ::er
ror title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/tavily.py,line=197,col=11,endLine=197,endColumn=17::src/twat_search
/web/engines/tavily.py:197:11: PLR0913 Too many arguments in function definition
 (13 > 5)               ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=202,col=5,endLine=202,endColumn=16::src/twat_search/w
eb/engines/tavily.py:202:5: FBT002 Boolean default positional argument in functi
on definition           ::error title=Ruff (FBT001),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=207,col=5,endLine=207,endColumn=19::src/twat_search/w
eb/engines/tavily.py:207:5: FBT001 Boolean-typed positional argument in function
 definition             ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=207,col=5,endLine=207,endColumn=19::src/twat_search/w
eb/engines/tavily.py:207:5: FBT002 Boolean default positional argument in functi
on definition           ::error title=Ruff (RUF002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/tavily.py,line=215,col=18,endLine=215,endColumn=19::src/twat_search/
web/engines/tavily.py:215:18: RUF002 Docstring contains ambiguous `’` (RIGHT SIN
GLE QUOTATION MARK). Did you mean ``` (GRAVE ACCENT)?
          ::error title=Ruff (PLR0913),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/you.py,line=43,col=9,endLine=43,endColumn=17::src/twat_search/web/e
ngines/you.py:43:9: PLR0913 Too many arguments in function definition (6 > 5)
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=48,col=9,endLine=48,endColumn=17::src/twat_search/web/en
gines/you.py:48:9: ARG002 Unused method argument: `language`
                        ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=49,col=9,endLine=49,endColumn=20::src/twat_search/web/en
gines/you.py:49:9: FBT002 Boolean default positional argument in function defini
tion                    ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=50,col=9,endLine=50,endColumn=19::src/twat_search/web/en
gines/you.py:50:9: ARG002 Unused method argument: `time_frame`
                        ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=51,col=11,endLine=51,endColumn=17::src/twat_search/web/e
ngines/you.py:51:11: ARG002 Unused method argument: `kwargs`
                        ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/you.py,line=191,col=11,endLine=191,endColumn=14::src/twat_search/we
b/engines/you.py:191:11: PLR0913 Too many arguments in function definition (7 >
5)                      ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=196,col=5,endLine=196,endColumn=16::src/twat_search/web/
engines/you.py:196:5: FBT002 Boolean default positional argument in function def
inition                 ::error title=Ruff (PLR0913),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/engines/you.py,line=213,col=11,endLine=213,endColumn=19::src/twat_search/we
b/engines/you.py:213:11: PLR0913 Too many arguments in function definition (7 >
5)                      ::error title=Ruff (FBT002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/
web/engines/you.py,line=218,col=5,endLine=218,endColumn=16::src/twat_search/web/
engines/you.py:218:5: FBT002 Boolean default positional argument in function def
inition                 ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search
/web/utils.py,line=48,col=33,endLine=48,endColumn=36::src/twat_search/web/utils.
py:48:33: PLR2004 Magic value used in comparison, consider replacing `0.1` with
a constant variable     ::error title=Ruff (ARG002),file=/Users/adam/Developer/v
cs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/e
ngines/test_base.py,line=89,col=32,endLine=89,endColumn=37::tests/unit/web/engin
es/test_base.py:89:32: ARG002 Unused method argument: `query`
                        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
engines/test_base.py,line=138,col=40,endLine=138,endColumn=42::tests/unit/web/en
gines/test_base.py:138:40: PLR2004 Magic value used in comparison, consider repl
acing `30` with a constant variable
          ::error title=Ruff (PLR2004),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
test_api.py,line=103,col=28,endLine=103,endColumn=29::tests/unit/web/test_api.py
:103:28: PLR2004 Magic value used in comparison, consider replacing `2` with a c
onstant variable        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
test_api.py,line=118,col=28,endLine=118,endColumn=29::tests/unit/web/test_api.py
:118:28: PLR2004 Magic value used in comparison, consider replacing `3` with a c
onstant variable        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
test_api.py,line=130,col=28,endLine=130,endColumn=29::tests/unit/web/test_api.py
:130:28: PLR2004 Magic value used in comparison, consider replacing `4` with a c
onstant variable        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
test_exceptions.py,line=64,col=31,endLine=64,endColumn=32::tests/unit/web/test_e
xceptions.py:64:31: PLR2004 Magic value used in comparison, consider replacing `
2` with a constant variable
          ::error title=Ruff (PLR2004),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/unit/web/
test_utils.py,line=28,col=40,endLine=28,endColumn=42::tests/unit/web/test_utils.
py:28:40: PLR2004 Magic value used in comparison, consider replacing `10` with a
 constant variable      ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=68,col=25,endLine=68,endColumn=52::tests/web/test_bing_scraper
.py:68:25: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=71,col=38,endLine=71,endColumn=39::tests/web/test_bing_scra
per.py:71:38: PLR2004 Magic value used in comparison, consider replacing `5` wit
h a constant variable   ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=72,col=38,endLine=72,endColumn=39::tests/web/test_bing_scra
per.py:72:38: PLR2004 Magic value used in comparison, consider replacing `3` wit
h a constant variable   ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=81,col=9,endLine=81,endColumn=36::tests/web/test_bing_scraper.
py:81:9: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=95,col=32,endLine=95,endColumn=33::tests/web/test_bing_scra
per.py:95:32: PLR2004 Magic value used in comparison, consider replacing `2` wit
h a constant variable   ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=110,col=44,endLine=110,endColumn=71::tests/web/test_bing_scrap
er.py:110:44: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=142,col=15,endLine=142,endColumn=42::tests/web/test_bing_scrap
er.py:142:15: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=203,col=46,endLine=203,endColumn=48::tests/web/test_bing_sc
raper.py:203:46: PLR2004 Magic value used in comparison, consider replacing `10`
 with a constant variable
          ::error title=Ruff (PLR2004),file=/Users/adam/Developer/vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=204,col=59,endLine=204,endColumn=60::tests/web/test_bing_sc
raper.py:204:59: PLR2004 Magic value used in comparison, consider replacing `5`
with a constant variable::error title=Ruff (PLR2004),file=/Users/adam/Developer/
vcs/github
.twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_
bing_scraper.py,line=205,col=70,endLine=205,endColumn=73::tests/web/test_bing_sc
raper.py:205:70: PLR2004 Magic value used in comparison, consider replacing `2.0
` with a constant variable
          ::error title=Ruff (N803),file=/Users/adam/Developer/vcs/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=210,col=15,endLine=210,endColumn=42::tests/web/test_bing_scrap
er.py:210:15: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=223,col=15,endLine=223,endColumn=42::tests/web/test_bing_scrap
er.py:223:15: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=239,col=15,endLine=239,endColumn=42::tests/web/test_bing_scrap
er.py:239:15: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=256,col=15,endLine=256,endColumn=42::tests/web/test_bing_scrap
er.py:256:15: N803 Argument name `mock_BingScraper` should be lowercase
                        ::error title=Ruff (N803),file=/Users/adam/Developer/vcs
/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/tests/web/test_bin
g_scraper.py,line=273,col=15,endLine=273,endColumn=42::tests/web/test_bing_scrap
er.py:273:15: N803 Argument name `mock_BingScraper` should be lowercase
                        %
          

```

---

_****_





There are many linter errors in the codebase, but let's focus on the linter error related to the import in `config.py`:

```
::error title=Ruff (E402),file=/Users/adam/Developer/vcs/github.tw
ardoch/pub/twat-packages/_good/twat/plugins/repos/twat_search/src/twat_search/we
b/config.py,line=151,col=1,endLine=151,endColumn=45::src/twat_search/web/config.
py:151:1: E402 Module level import not at top of file
```

This is because we still have the `from .engines import standardize_engine_name` import after the class definitions. Let's move that to the top of the file:

---

_****_

```diff
      YOU,
      YOU_NEWS,
+     standardize_engine_name
  )
  
      default_params: dict[str, Any] = Field(default_factory=dict)
  
- 
- # Import standardize_engine_name only after defining all classes to avoid circular imports
- from .engines import standardize_engine_name
- 
  
  # Main configuration model
```

---

_****_





Great! I've successfully updated the config.py file to use the engine name constants from engines/__init__.py. Here's a summary of the changes made:

1. Added imports for all the engine name constants (BRAVE, BRAVE_NEWS, etc.) from `.engines`
2. Added import for `standardize_engine_name` along with the constants
3. Replaced all string literals in DEFAULT_CONFIG with the corresponding constants
4. Updated the "hasdata_google" entry to use GOOGLE_HASDATA_FULL
5. Updated the "hasdata_google_light" entry to use GOOGLE_HASDATA
6. Added comments to clarify which is the full version and which is the light version
7. Moved the `standardize_engine_name` import to the top to fix the E402 linter error

These changes make the code more maintainable by ensuring consistent naming between modules and reducing the risk of typos in engine names. It also improves IDE support with better auto-completion and refactoring capabilities when engine names change.

Wait, but I should check to make sure I've used the right constants for the HasData engines...

Based on my review of the `hasdata.py` file, I correctly mapped:
- "hasdata_google" to GOOGLE_HASDATA_FULL 
- "hasdata_google_light" to GOOGLE_HASDATA

This matches the implementation in the `hasdata.py` file where:
- HasDataGoogleEngine has engine_code = GOOGLE_HASDATA_FULL
- HasDataGoogleLightEngine has engine_code = GOOGLE_HASDATA

The changes should help with code maintenance and ensure consistent engine naming throughout the codebase.

---

_**User**_

We have new engines that should have default configs in @config.py 

---

_**Assistant**_

<think>The user is indicating that there are new search engines that should have default configurations in the `config.py` file. I should first identify what these new engines are by looking at the engines module, particularly at the engine name constants defined in `__init__.py`.

I can see from the previous search results that there are engine constants defined in the engines `__init__.py` file, such as:
- BING_ANYWS
- BING_SCRAPER
- BING_SEARCHIT
- BRAVE
- BRAVE_ANYWS
- BRAVE_NEWS
- CRITIQUE
- DUCKDUCKGO
- GOOGLE_ANYWS
- GOOGLE_HASDATA
- GOOGLE_HASDATA_FULL
- GOOGLE_SCRAPER
- GOOGLE_SEARCHIT
- GOOGLE_SERPAPI
- PPLX
- QWANT_ANYWS
- QWANT_SEARCHIT
- TAVILY
- YANDEX_ANYWS
- YANDEX_SEARCHIT
- YOU
- YOU_NEWS

But in the `config.py` file, we only have configurations for:
- BRAVE
- BRAVE_NEWS
- GOOGLE_SERPAPI
- TAVILY
- PPLX
- YOU
- YOU_NEWS
- CRITIQUE
- DUCKDUCKGO
- BING_SCRAPER
- GOOGLE_HASDATA_FULL
- GOOGLE_HASDATA

This means we're missing default configurations for several engines:
- BING_ANYWS
- BING_SEARCHIT
- BRAVE_ANYWS
- GOOGLE_ANYWS
- GOOGLE_SCRAPER
- GOOGLE_SEARCHIT
- QWANT_ANYWS
- QWANT_SEARCHIT
- YANDEX_ANYWS
- YANDEX_SEARCHIT

I should look at the implementations of these engines to understand what default parameters they might need, then add those to the DEFAULT_CONFIG in config.py.</think>I see that we need to add default configurations for the new engines that have been added to the codebase. Let's first identify which engines are missing from the config.py file by comparing the engine constants in the engines module with those already in the configuration.

---

_****_

Read file: src/twat_search/web/engines/__init__.py

---

_****_



Now, let's look at the anywebsearch module to understand what default parameters it needs:

---

_****_

Read file: src/twat_search/web/engines/anywebsearch.py

---

_****_



Now, let's look at the SearchIT module to understand its default parameters:

---

_****_

Read file: src/twat_search/web/engines/searchit.py

---

_****_



Now, let's read the `google_scraper.py` file to understand the default settings for the Google scraper:

---

_****_

Read file: src/twat_search/web/engines/google_scraper.py

---

_****_





Let me examine the current configuration file to understand how the default configurations are structured:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_



Let's read the rest of the config.py file to understand how it manages configurations:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_





Now, let's update the config.py file to add the missing default configurations for the new search engines:

---

_****_

```diff
  # Import engine name constants
  from .engines import (
+     BING_ANYWS,
      BING_SCRAPER,
+     BING_SEARCHIT,
      BRAVE,
+     BRAVE_ANYWS,
      BRAVE_NEWS,
      CRITIQUE,
      DUCKDUCKGO,
+     GOOGLE_ANYWS,
      GOOGLE_HASDATA,
      GOOGLE_HASDATA_FULL,
+     GOOGLE_SCRAPER,
+     GOOGLE_SEARCHIT,
      GOOGLE_SERPAPI,
      PPLX,
+     QWANT_ANYWS,
+     QWANT_SEARCHIT,
      TAVILY,
+     YANDEX_ANYWS,
+     YANDEX_SEARCHIT,
      YOU,
      YOU_NEWS,
              },
          },
+         # Brave AnyWebSearch
+         BRAVE_ANYWS: {
+             "enabled": True,
+             "api_key": None,  # BRAVE_API_KEY
+             "default_params": {
+                 "language": "en",
+                 "num_results": 10,
+                 "merge": True,
+             },
+         },
          # SerpAPI (Google)
          GOOGLE_SERPAPI: {
              },
          },
+         # Google AnyWebSearch
+         GOOGLE_ANYWS: {
+             "enabled": True,
+             "api_key": None,
+             "default_params": {
+                 "language": "en",
+                 "num_results": 10,
+                 "merge": True,
+             },
+         },
+         # Google Scraper
+         GOOGLE_SCRAPER: {
+             "enabled": True,
+             "api_key": None,  # No API key required
+             "default_params": {
+                 "language": "en",
+                 "region": "us",
+                 "safe": "active",
+                 "sleep_interval": 0.0,
+                 "ssl_verify": True,
+                 "proxy": None,
+                 "unique": True,
+             },
+         },
+         # Google SearchIT
+         GOOGLE_SEARCHIT: {
+             "enabled": True,
+             "api_key": None,  # No API key required
+             "default_params": {
+                 "language": "en",
+                 "domain": "com",
+                 "sleep_interval": 0,
+                 "proxy": None,
+             },
+         },
          # Tavily Search
          TAVILY: {
              "default_params": {"num_pages": 1, "delay": 0.5},
          },
+         # Bing AnyWebSearch
+         BING_ANYWS: {
+             "enabled": True,
+             "api_key": None,
+             "default_params": {
+                 "language": "en",
+                 "num_results": 10,
+                 "merge": True,
+             },
+         },
+         # Bing SearchIT
+         BING_SEARCHIT: {
+             "enabled": True,
+             "api_key": None,  # No API key required
+             "default_params": {
+                 "language": "en",
+                 "domain": "com",
+                 "sleep_interval": 0,
+                 "proxy": None,
+             },
+         },
+         # Qwant AnyWebSearch
+         QWANT_ANYWS: {
+             "enabled": True,
+             "api_key": None,
+             "default_params": {
+                 "language": "en",
+                 "num_results": 10,
+                 "merge": True,
+             },
+         },
+         # Qwant SearchIT
+         QWANT_SEARCHIT: {
+             "enabled": True,
+             "api_key": None,  # No API key required
+             "default_params": {
+                 "language": "en",
+                 "geo": "us",
+                 "sleep_interval": 0,
+                 "proxy": None,
+             },
+         },
+         # Yandex AnyWebSearch
+         YANDEX_ANYWS: {
+             "enabled": True,
+             "api_key": None,  # YA_KEY and YA_FLDID environment variables
+             "default_params": {
+                 "language": "en",
+                 "num_results": 10,
+                 "merge": True,
+             },
+         },
+         # Yandex SearchIT
+         YANDEX_SEARCHIT: {
+             "enabled": True,
+             "api_key": None,  # No API key required
+             "default_params": {
+                 "language": "en",
+                 "country": "us",
+                 "sleep_interval": 0,
+                 "proxy": None,
+             },
+         },
          # HasData Google (Full version)
          GOOGLE_HASDATA_FULL: {
```

---

_****_





Now let's run the linter to check for any errors:

---

_****_



---

_****_



---



---
