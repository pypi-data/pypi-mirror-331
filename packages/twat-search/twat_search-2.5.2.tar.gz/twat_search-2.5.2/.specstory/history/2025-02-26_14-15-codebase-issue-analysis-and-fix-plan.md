## SpecStory

## Codebase Issue Analysis and Fix Plan (26/02/2025, 14:15:10)

_**User**_

Analyze the issues listed and the codebase, and then in @TODO.md write a detailed plan on how you will fix the problems and what the problems are. 

twat-search web q --help
INFO: Showing help with the command 'twat-search web q -- --help'.

NAME
    twat-search web q - Search the web using one or more search engines.

SYNOPSIS
    twat-search web q QUERY <flags>

DESCRIPTION
    Search the web using one or more search engines.

POSITIONAL ARGUMENTS
    QUERY
        Type: str
        The search query

FLAGS
    --engines=ENGINES
        Type: Optional[str | list[str] ...
        Default: None
        List of engines to use (comma-separated string or list).
    --engine=ENGINE
        Type: Optional[str | None]
        Default: None
        Alias for engines (--engine flag)
    --e=E
        Type: Optional[str | None]
        Default: None
        Alias for engines (-e flag)
    -n, --num_results=NUM_RESULTS
        Type: int
        Default: 5
        Number of results to return per engine
    -c, --country=COUNTRY
        Type: Optional[str | None]
        Default: None
        Country code for regional results
    -l, --language=LANGUAGE
        Type: Optional[str | None]
        Default: None
        Language code for results
    -s, --safe_search=SAFE_SEARCH
        Type: bool
        Default: True
        Whether to enable safe search filtering
    -t, --time_frame=TIME_FRAME
        Type: Optional[str | None]
        Default: None
        Time frame for results (e.g., "day", "week", "month")
    -v, --verbose=VERBOSE
        Type: bool
        Default: False
        Whether to display verbose output
    -j, --json=JSON
        Type: bool
        Default: False
        Whether to return results as JSON
    -p, --plain=PLAIN
        Type: bool
        Default: False
        Whether to display results in plain text format **kwargs
    Additional flags are accepted.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS


=====

>> for v in $(env|sort); do echo $v | sed s^=.*^...^g; done;

AGNO_API_KEY...
AI21_API_KEY...
AIHORDE_KEY...
AIHORDE_KEY_2...
AIMLAPI_KEY...
AKOOL_API_KEY...
ALEPHALPHA_API_KEY...
ANTHROPIC_API_KEY...
ANTHROPIC_API_KEY_2...
ANYSCALE_API_KEY...
APININJAS_API_KEY...
ASSEMBLYAI_API_KEY...
ASTRA_CLIENT_ID...
ASTRA_SECRET...
ASTRA_TOKEN...
AUTOENHANCE_API_KEY...
AUTOMDEV_API_KEY...
AVIAN_API_KEY...
AZURE_COGNITIVE_API_KEY...
BASETEN_API_KEY...
BFL_API_KEY...
BRAVE_API_KEY...
BRIA_API_KEY...
BROWSEAI_API_KEY...
CEREBRAS_API_KEY...
CLARIFAI_API_KEY...
CLICOLOR...
CLOUDINARY_API_KEY...
CODING_MODEL...
CODING_PROVIDER...
COHERE_API_KEY...
COLORTERM...
COMMAND_MODE...
CRATES_IO_TOKEN...
CRITIQUE_LABS_API_KEY...
DEEPAI_API_KEY...
DEEPGRAM_API_KEY...
DEEPGRAM_API_KEY_2...
DEEPINFRA_API_KEY...
DEEPL_FREE_API_KEY...
DEEPL_FREE_API_KEY_2...
DEEPL_PRO_API_KEY...
DEEPSEEK_API_KEY...
DEEP_IMAGE_API_KEY...
DOCUMENT360_API_TOKEN_01...
DOCUMENT360_API_TOKEN_02...
DOCUMENT360_API_TOKEN_03...
DOCUMENT360_API_TOKEN_04...
DOCUMENT360_API_TOKEN_05...
DOCUMENT360_API_TOKEN_06...
DOCUMENT360_API_TOKEN_07...
DOCUMENT360_API_TOKEN_08...
DOCUMENT360_API_TOKEN_09...
DOCUMENT360_API_TOKEN_10...
DOCUMENT360_API_TOKEN_OLD...
DOCUMENT360_API_USERNAME...
DOCUMENT360_PORTAL_ID...
DROPBOX_ACCESS_TOKEN...
DROPBOX_APP_KEY...
DROPBOX_APP_SECRET...
D_ID_API_KEY...
ELEVENLABS_API_KEY...
ELEVENLABS_API_TOKEN...
ELEVEN_API_KEY...
EVERYPIXEL_CLIENT_ID...
EVERYPIXEL_SECRET...
EXAAI_API_KEY...
FACEPLUSPLUS_API_KEY...
FAL_KEY...
FEATHERLESS_API_KEY...
FIREWORKS_API_KEY...
FREEPIK_API_KEY...
GEMINI_API_KEY...
GIPHY_API_KEY...
GITHUB_API_TOKEN...
GITHUB_TOKEN...
GLAMA_API_KEY...
GOAPI_KEY...
GOBIN...
GOOGLE_AI_API_KEY...
GOOGLE_API_KEY...
GOOGLE_APPLICATION_CREDENTIALS...
GOOGLE_CSE_API_KEY...
GOOGLE_CSE_ID...
GOOGLE_TRANSLATE_API_KEY...
GOPATH...
GROQ_API_KEY...
GUILE_LOAD_COMPILED_PATH...
GUILE_LOAD_PATH...
GUILE_SYSTEM_EXTENSIONS_PATH...
GUILE_TLS_CERTIFICATE_DIRECTORY...
HASDATA_API_KEY...
HATCH_INDEX_AUTH...
HATCH_INDEX_USER...
HAYSTACK_API_KEY...
HELICONE_API_KEY...
HF_API_TOKEN...
HF_TOKEN...
HOME...
HOMEBREW_GITHUB_API_TOKEN...
HUGGINGFACEHUB_API_TOKEN...
HUGGINGFACEHUB_API_TOKEN_2...
HUGGINGFACE_API_KEY...
HYPERBOLIC_API_KEY...
IBM_WATSON_API_KEY...
IMAGEPIPELINE_API_KEY...
IMGIX_API_KEY...
INFERENCE_KEY...
JAVA_HOME...
JINA_API_KEY...
KITS_API_KEY...
KRAKENAI_API_KEY...
KRAKENAI_USER_ID...
LALAL_API_KEY...
LAMINI_API_KEY...
LANG...
LANGDB_API_KEY...
LC_ALL...
LC_CTYPE...
LIMEWIRE_API_KEY...
LINKUP_API_KEY...
LLM_ANYSCALE_ENDPOINTS_KEY...
LLM_GEMINI_KEY...
LLM_HUGGINGFACE_KEY...
LMNT_API_KEY...
LOGNAME...
LSCOLORS...
LUXAND_API_KEY...
MANCER_API_KEY...
MARVIN_OPENAI_API_KEY...
MIDJOURNEY_USER_ID...
MISTRAL_API_KEY...
MIXEDBREAD_API_KEY...
MODAL_API_KEY...
MONSTER_API_KEY...
MYSTIC_API_KEY...
NCURSES_NO_UTF8_ACS...
NLPCLOUD_API_KEY...
NODE_PATH...
NOMIC_KEY...
NORD_PASSWORD...
NORD_USER...
NOVITA_API_KEY...
NPM_PACKAGES...
OLDPWD...
OPENAI_API_KEY...
OPENROUTER_API_KEY...
OPENROUTER_API_KEY_2...
PATH...
PDFLIBLICENSEFILE...
PERPLEXITYAI_API_KEY...
PERPLEXITY_API_KEY...
PEXELS_API_KEY...
PIXABAY_API_KEY...
PIXELBIN_ACCESS_KEY...
PIXELBIN_TOKEN...
PKG_CONFIG_PATH...
POCKET_API_KEY...
PROXYCURL_API_KEY...
PS1...
PWD...
PYPI_TOKEN...
REASONING_MODEL...
REASONING_PROVIDER...
REKA_API_KEY...
REMINI_API_KEY...
REMOVE_BG_API_KEY...
REPLICATE_API_KEY...
REPLICATE_API_KEY_2...
REPLICATE_API_TOKEN...
RUNCOMFY_API_KEY...
RUNPOD_API_KEY...
RUNWAYML_API_KEY...
SAMBANOVA_API_KEY...
SEGMIND_API_KEY...
SERPAPI_API_KEY...
SHELL...
SHLVL...
SHOTSTACK_API_KEY_PROD...
SHOTSTACK_API_KEY_SANDBOX...
SOURCEGRAPH_TOKEN...
SSH_AUTH_SOCK...
SSH_SOCKET_DIR...
STABILITY_API_KEY...
SYNCLABS_API_KEY...
TARGON_API_KEY...
TAVILY_API_KEY...
TENSOROPERA_API_KEY...
TERM...
TERM_PROGRAM...
TERM_PROGRAM_VERSION...
TINEYE_API_KEY...
TMPDIR...
TOGETHERAI_API_KEY...
TULP_OPENAI_API_KEY...
TWILIO_REC...
UNSPLASH_API_KEY...
UNSTRUCTURED_API_KEY...
USER...
UV_NO_PROGRESS...
UV_PUBLISH_TOKEN...
UV_PYTHON...
UV_PYTHON_PREFERENCE...
VANCEAI_API_KEY...
VIRTUAL_ENV...
VIRTUAL_ENV_PROMPT...
VOICEMAKER_API_KEY...
VOYAGE_API_KEY...
WARP_HONOR_PS1...
WARP_IS_LOCAL_SHELL_SESSION...
WARP_USE_SSH_WRAPPER...
WORKON_HOME...
XAI_API_KEY...
XPC_FLAGS...
XPC_SERVICE_NAME...
YOUCOM_API_KEY...
YOUCOM_WEBLLM_API_KEY...
YOUML_API_KEY...
ZENCLI_GITHUBAUTHTOKEN...
ZENCLI_REPONAME...
ZENCLI_REPOOWNER...
ZENCLI_ZENHUBAUTHTOKEN...
ZENHUB_API_TOKEN...
ZHB_AUTH_TOKEN...
ZHB_ORG...
ZHB_REPO...
ZHB_REPO_ID...
ZUKI_API_KEY...
ZYPHRA_API_KEY...


=====

>> uv pip install -e .[dev,test,all]; for engine in $(twat-search web info --plain); do echo "\n\n\n>>> $engine"; twat-search web q -e $engine "Adam Twardoch" -n 1 --verbose; done;

and we got: 

====


>>> bing_anyws
[02/26/25 13:58:55] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['bing_anyws']                                                                              cli.py:168
                    INFO     🔍 Querying engine: bing_anyws                                                                                                  api.py:74
                    INFO     Searching Bing (anywebsearch) with query: 'Adam Twardoch'                                                             anywebsearch.py:366
                    DEBUG    Using max_results=5, language=en                                                                                      anywebsearch.py:367
                    INFO     No results returned from Bing (anywebsearch)                                                                          anywebsearch.py:377
                    INFO     ✅ Engine 'bing_anyws' returned 0 results                                                                                      api.py:160
No results found!


<<< FIXME: I specified -n 1 but we’re using max_results=5 (this also applies to all other) !!! Also problem that we got no results :) 





>>> bing_scraper
[02/26/25 13:58:57] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['bing_scraper']                                                                            cli.py:168
                    DEBUG    Parameters safe_search=True set but not used by Bing Scraper                                                          bing_scraper.py:151
                    INFO     🔍 Querying engine: bing_scraper                                                                                                api.py:74
                    INFO     Searching Bing with query: 'Adam Twardoch'                                                                            bing_scraper.py:227
                    DEBUG    Using max_results=5, max_retries=3, delay=1.0                                                                         bing_scraper.py:228
⠸ Searching for 'Adam Twardoch'...[02/26/25 13:58:58] DEBUG    Received 5 raw results from Bing Scraper                                                                              bing_scraper.py:246
                    INFO     Returning 5 validated results from Bing Scraper                                                                       bing_scraper.py:274
                    INFO     ✅ Engine 'bing_scraper' returned 5 results                                                                                    api.py:160
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Engine       ┃ Status     ┃ Title                                   ┃ URL                                                                    ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ bing_scraper │ ✅ Success │ Adam Twardoch                           │ https://www.twardoch.com/                                              │
│              │ ✅ Success │ Adam Twardoch – Fontlab Ltd. | LinkedIn │ https://pl.linkedin.com/in/twardoch                                    │
│              │ ✅ Success │ Adam Twardoch - Typoteka                │ https://typoteka.pl/pl/designer/adam-twardoch                          │
│              │ ✅ Success │ Adam Twardoch - Typoteka                │ https://typoteka.pl/en/designer/adam-twardoch                          │
│              │ ✅ Success │ Font: cyfrowy nośnik pisma - Twardoch   │ https://www.twardoch.com/download/edupl_technologia_fontow_1_tekst.pdf │
└──────────────┴────────────┴─────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
{
    'engine': 'bing_scraper',
    'status': '✅ Success',
    'url': 'https://www.twardoch.com/',
    'title': 'Adam Twardoch',
(...) 
false}




>>> bing_searchit
[02/26/25 13:59:00] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['bing_searchit']                                                                           cli.py:168
                    DEBUG    Parameters safe_search=True set but not used by bing_searchit                                                             searchit.py:283
                    INFO     🔍 Querying engine: bing_searchit                                                                                               api.py:74
                    INFO     Searching Bing (searchit) with query: 'Adam Twardoch'                                                                     searchit.py:627
                    DEBUG    Using max_results=5, language=en, domain=com, sleep_interval=0, proxy=None                                                searchit.py:628
                    DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    INFO     No results returned from Bing (searchit)                                                                                  searchit.py:651
                    INFO     ✅ Engine 'bing_searchit' returned 0 results                                                                                   api.py:160
No results found!


<<< FIXME: Figure out why this doesn't work



>>> brave
[02/26/25 13:59:02] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['brave']                                                                                   cli.py:168
                    INFO     🔍 Querying engine: brave                                                                                                       api.py:74(...)": false}

<<< GOOD: This works perfectly




>>> brave_anyws
[02/26/25 13:59:05] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['brave_anyws']                                                                             cli.py:168
                    INFO     🔍 Querying engine: brave_anyws                                                                                                 api.py:74
                    ERROR    Search with engine 'brave_anyws' failed: Engine 'brave_anyws': Brave API key is required for Brave search                      api.py:158
No results found!


<<< FIXME: BRAVE_API_KEY is defined in the env



>>> brave_news
[02/26/25 13:59:07] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['brave_news']                                                                              cli.py:168
                    ERROR    Error initializing engine 'brave_news': Engine 'brave_news': Brave API key is required. Set it via one of these env vars:       api.py:82
                             BRAVE_API_KEY                                                                                                                            
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!



<<< FIXME: BRAVE_API_KEY is in the env



>>> critique
[02/26/25 13:59:09] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['critique']                                                                                cli.py:168
                    ERROR    Error initializing engine 'critique': Engine 'critique': Critique Labs API key is required. Set it via one of these env vars:   api.py:82
                             CRITIQUE_LABS_API_KEY, CRITIQUE_API_KEY                                                                                                  
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!


<<< FIXME: CRITIQUE_LABS_API_KEY is defined in the env


>>> duckduckgo
[02/26/25 13:59:11] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['duckduckgo']                                                                              cli.py:168
                    INFO     🔍 Querying engine: duckduckgo                                                                                                  api.py:74
                    DEBUG    Loaded CA certs                                                                                                               utils.rs:34
                    DEBUG    starting new connection: https://lite.duckduckgo.com/                                                                      connect.rs:381
                    DEBUG    resolving lite.duckduckgo.com                                                                                                  dns.rs:126
                    DEBUG    connecting to 52.142.124.215:443                                                                                              http.rs:730
⠋ Searching for 'Adam Twardoch'...                    DEBUG    connected to 52.142.124.215:443                                                                                               http.rs:733
⠙ Searching for 'Adam Twardoch'...                    DEBUG    pooling idle connection for PoolKey { uri: https://lite.duckduckgo.com/, network: default }                                   pool.rs:380
⠙ Searching for 'Adam Twardoch'...[02/26/25 13:59:12] DEBUG    inserting secure cookie 'kl'                                                                                           cookie_store.rs:82
                    INFO     response: https://lite.duckduckgo.com/lite/ 200 16144                                                                          lib.rs:454
                    DEBUG    _get_url() https://lite.duckduckgo.com/lite/ 200 16144                                                           duckduckgo_search.py:135
                    INFO     ✅ Engine 'duckduckgo' returned 5 results                                                                                      api.py:160
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Engine     ┃ Status     ┃ Title                                   ┃ URL                                    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ duckduckgo │ ✅ Success │ Adam Twardoch                           │ https://www.twardoch.com/              │
│            │ ✅ Success │ Adam Twardoch - Fontlab Ltd. | LinkedIn │ https://pl.linkedin.com/in/twardoch    │
│            │ ✅ Success │ twardoch.com | Adam Twardoch | Fonts    │ http://www.twardoch.com/fonts/         │
│            │ ✅ Success │ Adam Twardoch - GitHub                  │ https://github.com/twardoch            │
│            │ ✅ Success │ Adam Twardoch - Facebook                │ https://www.facebook.com/adamtwardoch/ │
└────────────┴────────────┴─────────────────────────────────────────┴────────────────────────────────────────┘
{
    'engine': 'duckduckgo',
    'status': '✅ Success',(...)false}


<<< GOOD! 



>>> google_anyws
[02/26/25 13:59:15] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['google_anyws']                                                                            cli.py:168
                    INFO     🔍 Querying engine: google_anyws                                                                                                api.py:74
                    INFO     Searching Google (anywebsearch) with query: 'Adam Twardoch'                                                           anywebsearch.py:291
                    DEBUG    Using max_results=5, language=en                                                                                      anywebsearch.py:292
                    INFO     No results returned from Google (anywebsearch)                                                                        anywebsearch.py:302
                    INFO     ✅ Engine 'google_anyws' returned 0 results                                                                                    api.py:160
No results found!


<<< FIXME: Figure out why it's not working


>>> google_hasdata
[02/26/25 13:59:17] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    WARNING  Engine 'google_hasdata' is not available. The dependency may not be installed.                                                 cli.py:161
                    DEBUG    Attempting to search with engines: None                                                                                        cli.py:168
                    INFO     🔍 Querying engine: brave                                                                                                       api.py:74
                    ERROR    Error initializing engine 'brave_news': Engine 'brave_news': Brave API key is required. Set it via one of these env vars:       api.py:82
                             BRAVE_API_KEY                                                                                                                            
                    INFO     🔍 Querying engine: brave_anyws                          (...)": false}

<<< FIXME: Figure out why this engine does not work and KILL THE FALLBACK! If it fails it fails. 


>>> google_hasdata_full
[02/26/25 13:59:25] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    WARNING  Engine 'google_hasdata_full' is not available. The dependency may not be installed.                                            cli.py:161
                    DEBUG    Attempting to search with engines: None                                                                                        cli.py:168
                    INFO     🔍 Querying engine: brave                                                      (...)
                    first": false}

<<< FIXME: Same thing, figure out why it fails, and kill the fallback



>>> google_searchit
[02/26/25 13:59:36] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['google_searchit']                                                                         cli.py:168
                    DEBUG    Parameters safe_search=True set but not used by google_searchit                                                           searchit.py:283
                    INFO     🔍 Querying engine: google_searchit                                                                                             api.py:74
                    INFO     Searching Google (searchit) with query: 'Adam Twardoch'                                                                   searchit.py:391
                    DEBUG    Using max_results=5, language=en, domain=com, sleep_interval=0, proxy=None                                                searchit.py:392
                    DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    INFO     No results returned from Google (searchit)                                                                                searchit.py:415
                    INFO     ✅ Engine 'google_searchit' returned 0 results                                                                                 api.py:160
No results found!


<<< FIXME: Figure out why it fails



>>> google_serpapi
[02/26/25 13:59:38] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['google_serpapi']                                                                          cli.py:168
                    ERROR    Error initializing engine 'google_serpapi': Engine 'google_serpapi': SerpApi API key is required. Set it via one of these env   api.py:82
                             vars: SERPAPI_API_KEY                                                                                                                    
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!


<<< FIXME: SERPAPI_API_KEY is defined in the env



>>> pplx
[02/26/25 13:59:40] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['pplx']                                                                                    cli.py:168
                    ERROR    Error initializing engine 'pplx': Engine 'pplx': Perplexity API key is required. Set it via one of these env vars:              api.py:82
                             PERPLEXITYAI_API_KEY, PERPLEXITY_API_KEY.                                                                                                
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!



<<< FIXME: PERPLEXITYAI_API_KEY is defined in the env


>>> qwant_anyws
[02/26/25 13:59:42] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['qwant_anyws']                                                                             cli.py:168
                    INFO     🔍 Querying engine: qwant_anyws                                                                                                 api.py:74
                    INFO     Searching Qwant (anywebsearch) with query: 'Adam Twardoch'                                                            anywebsearch.py:521
                    DEBUG    Using max_results=5, language=en                                                                                      anywebsearch.py:522
                    INFO     No results returned from Qwant (anywebsearch)                                                                         anywebsearch.py:532
                    INFO     ✅ Engine 'qwant_anyws' returned 0 results                                                                                     api.py:160
No results found!



<<< FIXME: Figure out why this fails


>>> qwant_searchit
[02/26/25 13:59:44] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['qwant_searchit']                                                                          cli.py:168
                    DEBUG    Parameters safe_search=True set but not used by qwant_searchit                                                            searchit.py:283
                    INFO     🔍 Querying engine: qwant_searchit                                                                                              api.py:74
                    INFO     Searching Qwant (searchit) with query: 'Adam Twardoch'                                                                    searchit.py:549
                    DEBUG    Using max_results=5, language=en, geo=us, sleep_interval=0, proxy=None                                                    searchit.py:550
                    DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    INFO     No results returned from Qwant (searchit)                                                                                 searchit.py:572
                    INFO     ✅ Engine 'qwant_searchit' returned 0 results                                                                                  api.py:160
No results found!



<<< FIXME: Figure out why this fails



>>> tavily
[02/26/25 13:59:46] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['tavily']                                                                                  cli.py:168
                    INFO     🔍 Querying engine: tavily                                                                                                      api.py:74
                    DEBUG    load_ssl_context verify=True cert=None trust_env=True http2=False                                                           _config.py:79
                    DEBUG    load_verify_locations                                                                                                      _config.py:146
                             cafile='/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/certifi/cacert.pem'                              
                    DEBUG    connect_tcp.started host='api.tavily.com' port=443 local_address=None timeout=10 socket_options=None                         _trace.py:85
⠙ Searching for 'Adam Twardoch'...                    DEBUG    connect_tcp.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x10a66dbb0>                               _trace.py:85
                    DEBUG    start_tls.started ssl_context=<ssl.SSLContext object at 0x10a656d50> server_hostname='api.tavily.com' timeout=10             _trace.py:85
⠸ Searching for 'Adam Twardoch'...                    DEBUG    start_tls.complete return_value=<httpcore._backends.anyio.AnyIOStream object at 0x109804230>                                 _trace.py:85
                    DEBUG    send_request_headers.started request=<Request [b'POST']>                                                                     _trace.py:85
                    DEBUG    send_request_headers.complete                                                                                                _trace.py:85
                    DEBUG    send_request_body.started request=<Request [b'POST']>                                                                        _trace.py:85
                    DEBUG    send_request_body.complete                                                                                                   _trace.py:85
                    DEBUG    receive_response_headers.started request=<Request [b'POST']>                                                                 _trace.py:85
⠙ Searching for 'Adam Twardoch'...[02/26/25 13:59:48] DEBUG    receive_response_headers.complete return_value=(b'HTTP/1.1', 200, b'OK', [(b'Date', b'Wed, 26 Feb 2025 12:59:47 GMT'),       _trace.py:85
                             (b'Content-Type', b'application/json'), (b'Content-Length', b'7091'), (b'Connection', b'keep-alive'), (b'Server', b'nginx'),             
                             (b'content-security-policy', b"default-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src                      
                             'self';base-uri 'self';form-action 'self'; require-trusted-types-for 'script'; upgrade-insecure-requests;"),                             
                             (b'Strict-Transport-Security', b'max-age=31536000 ; includeSubDomains'), (b'X-Content-Type-Options', b'nosniff'),                        
                             (b'X-Frame-Options', b'DENY')])                                                                                                          
                    INFO     HTTP Request: POST https://api.tavily.com/search "HTTP/1.1 200 OK"                                                        _client.py:1729
                    DEBUG    receive_response_body.started request=<Request [b'POST']>                                                                    _trace.py:85
                    DEBUG    receive_response_body.complete                                                                                               _trace.py:85
                    DEBUG    response_closed.started                                                                                                      _trace.py:85
                    DEBUG    response_closed.complete                                                                                                     _trace.py:85
                    DEBUG    close.started                                                                                                                _trace.py:85
                    DEBUG    close.complete                                                                                                               _trace.py:85
                    INFO     ✅ Engine 'tavily' returned 5 results                                                                                          api.py:160
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Engine ┃ Status     ┃ Title                                     ┃ URL                                               ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ tavily │ ✅ Success │ Adam Twardoch - Fontlab Ltd. | LinkedIn   │ https://pl.linkedin.com/in/twardoch               │
│        │ ✅ Success │ Adam Twardoch                             │ https://www.twardoch.com/                         │
│        │ ✅ Success │ Adam Twardoch - MyFonts                   │ https://www.myfonts.com/collections/adam-twardoch │
│        │ ✅ Success │ Adam Twardoch - Typoteka                  │ https://typoteka.pl/en/designer/adam-twardoch     │
│        │ ✅ Success │ Adam Twardoch · Adam Twardoch's test site │ https://twardoch.github.io/                       │
└────────┴────────────┴───────────────────────────────────────────┴───────────────────────────────────────────────────┘
{
    'engine': 'tavily',
    'status': '✅ Success',
    'url': 'https://pl.linkedin.com/in/twardoch',
    'title': 'Adam Twardoch - Fontlab Ltd. | LinkedIn',
    'snippet': 'Adam (...)rst": false}

<<< GOOD, though this gets ignored -n, --num_results=NUM_RESULTS
        Type: int
        Default: 5
        Number of results to return per engine




>>> yandex_anyws
[02/26/25 13:59:50] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['yandex_anyws']                                                                            cli.py:168
                    INFO     🔍 Querying engine: yandex_anyws                                                                                                api.py:74
                    ERROR    Search with engine 'yandex_anyws' failed: Engine 'yandex_anyws': Yandex API key and folder ID are required for Yandex search   api.py:158
No results found!

<<< GOOD: This is legit, as the API key is not specified



>>> yandex_searchit
[02/26/25 13:59:52] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['yandex_searchit']                                                                         cli.py:168
                    DEBUG    Parameters safe_search=True set but not used by yandex_searchit                                                           searchit.py:283
                    INFO     🔍 Querying engine: yandex_searchit                                                                                             api.py:74
                    INFO     Searching Yandex (searchit) with query: 'Adam Twardoch'                                                                   searchit.py:470
                    DEBUG    Using max_results=5, language=en, domain=None, geo=None, sleep_interval=0, proxy=None                                     searchit.py:471
                    DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    INFO     No results returned from Yandex (searchit)                                                                                searchit.py:494
                    INFO     ✅ Engine 'yandex_searchit' returned 0 results                                                                                 api.py:160
No results found!


<<< GOOD: This is legit, as the API key is not specified


>>> you
[02/26/25 13:59:54] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['you']                                                                                     cli.py:168
                    ERROR    Error initializing engine 'you': Engine 'you': You.com API key is required. Set it via one of these env vars: YOU_API_KEY       api.py:82
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!


<<< FIXME: YOU_API_KEY is in the env



>>> you_news
[02/26/25 13:59:56] DEBUG    Using selector: KqueueSelector                                                                                      selector_events.py:64
                    DEBUG    Attempting to search with engines: ['you_news']                                                                                cli.py:168
                    ERROR    Error initializing engine 'you_news': Engine 'you_news': You.com API key is required. Set it via one of these env vars:         api.py:82
                             YOU_API_KEY                                                                                                                              
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  api.py:167
                    ERROR    Search failed: No search engines could be initialized. Make sure at least one engine dependency is installed.                  cli.py:174
                                         ❌ Search Errors                                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ No search engines could be initialized. Make sure at least one engine dependency is installed. │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
No results found!



<<< FIXME: YOU_API_KEY is in the env



---

_**Assistant**_

<think>I need to analyze the issues in the twat-search package based on the output provided. Let me break down the main issues I see:

1. **Number of results issue**: The `-n 1` parameter is not being respected. For example, with `bing_anyws` and others, it's still trying to use `max_results=5` despite the command line specifying only 1 result.

2. **API key issues**: Multiple search engines are failing despite environment variables being set:
   - `brave_anyws` and `brave_news` fail despite `BRAVE_API_KEY` being defined
   - `critique` fails despite `CRITIQUE_LABS_API_KEY` being defined
   - `google_serpapi` fails despite `SERPAPI_API_KEY` being defined
   - `pplx` fails despite `PERPLEXITYAI_API_KEY` being defined
   - `you` and `you_news` fail despite `YOU_API_KEY` being defined

3. **Failed searches with no results**:
   - `bing_anyws`, `bing_searchit`, `google_anyws`, `google_searchit`, `qwant_anyws`, `qwant_searchit` all return no results

4. **Unexpected fallback behavior**: When a search engine is not available, it tries to fall back to other engines instead of simply failing, which is confusing

5. **Working engines**:
   - `bing_scraper`, `brave`, `duckduckgo`, and `tavily` seem to be working correctly (though they still ignore the `-n 1` parameter)

Let me first explore the codebase to understand how it's structured before drafting the detailed TODO plan.</think>I'll explore the codebase to understand the issues mentioned in your test results and create a detailed plan in TODO.md.

---

_****_

<details>
            <summary>Listed current directory • **30** results</summary>
        
| Name |
|-------|
| 📁 `.git` |
| 📁 `.idea` |
| 📄 `fix_name_attribute.py` |
| 📁 `.mypy_cache` |
| 📄 `.pre-commit-config.yaml` |
| 📄 `uv.lock` |
| 📄 `pyproject.toml` |
| 📁 `_private` |
| 📁 `tests` |
| 📄 `cleanup.py` |
| 📄 `README.md` |
| 📄 `CHANGELOG.md` |
| 📁 `.specstory` |
| 📁 `.venv` |
| 📄 `NEXTENGINES.md` |
| 📄 `CLEANUP.txt` |
| 📄 `twat_search.txt` |
| 📄 `.DS_Store` |
| 📁 `dist` |
| 📄 `TODO.md` |
| 📄 `PROGRESS.md` |
| 📁 `src` |
| 📁 `.benchmarks` |
| 📁 `.ruff_cache` |
| 📁 `.cursor` |
| 📄 `VERSION.txt` |
| 📁 `.pytest_cache` |
| 📁 `.github` |
| 📄 `LICENSE` |
| 📄 `.gitignore` |

</details>

---

_****_



Let's look at the existing TODO.md file to see what's already documented:

---

_****_

Read file: TODO.md

---

_****_



Now let's check the source structure in the src directory:

---

_****_

<details>
            <summary>Listed directory src • **2** results</summary>
        
| Name |
|-------|
| 📁 `twat_search` |
| 📄 `.DS_Store` |

</details>

---

_****_





Let's explore the main package code:

---

_****_

<details>
            <summary>Listed directory src/twat_search • **6** results</summary>
        
| Name |
|-------|
| 📁 `__pycache__` |
| 📄 `__version__.py` |
| 📄 `__init__.py` |
| 📁 `web` |
| 📄 `__main__.py` |
| 📄 `.DS_Store` |

</details>

---

_****_







Let's look at the web subdirectory:

---

_****_

<details>
            <summary>Listed directory src/twat_search/web • **11** results</summary>
        
| Name |
|-------|
| 📁 `__pycache__` |
| 📄 `api.py` |
| 📄 `config.py` |
| 📄 `__init__.py` |
| 📄 `engine_constants.py` |
| 📁 `engines` |
| 📄 `utils.py` |
| 📄 `cli.py` |
| 📄 `.DS_Store` |
| 📄 `models.py` |
| 📄 `exceptions.py` |

</details>

---

_****_





Let's check the main CLI file since that's where the search command is handled:

---

_****_

Read file: src/twat_search/web/cli.py

---

_****_



Now let's look at the API part:

---

_****_

Read file: src/twat_search/web/api.py

---

_****_






Let's check the list of available engines and how they're registered:

---

_****_

<details>
            <summary>Listed directory src/twat_search/web/engines • **16** results</summary>
        
| Name |
|-------|
| 📁 `__pycache__` |
| 📄 `brave.py` |
| 📄 `duckduckgo.py` |
| 📄 `google_scraper.py` |
| 📄 `critique.py` |
| 📄 `searchit.py` |
| 📄 `anywebsearch.py` |
| 📄 `pplx.py` |
| 📄 `serpapi.py` |
| 📄 `tavily.py` |
| 📄 `bing_scraper.py` |
| 📄 `__init__.py` |
| 📄 `you.py` |
| 📄 `hasdata.py` |
| 📄 `base.py` |
| 📄 `.DS_Store` |

</details>

---

_****_







Let's see how engines are registered and initialized by checking the base.py file:

---

_****_

Read file: src/twat_search/web/engines/base.py

---

_****_








Let's look at the config.py file to understand how the configuration works:

---

_****_

Read file: src/twat_search/web/config.py

---

_****_






Let's see the engine_constants module to understand how engine aliases and standardization works:

---

_****_

Read file: src/twat_search/web/engine_constants.py

---

_****_











Let's look at a couple of specific engine implementations to see how they handle the num_results parameter. Let's check the Brave and Tavily engines:

---

_****_

Read file: src/twat_search/web/engines/brave.py

---

_****_









Now let's also check the anywebsearch.py file, which seems to be handling multiple engines:

---

_****_

Read file: src/twat_search/web/engines/anywebsearch.py

---

_****_










Let's look at one more engine implementation - check the searchit engine that also had issues:

---

_****_

Read file: src/twat_search/web/engines/searchit.py

---

_****_










Based on my analysis of the code and the issues in the testing results, I'll create a detailed TODO plan:

---

_****_

```diff
  ## TODO
  
+ ### Critical Issues
+ 
+ 1. **Fix `num_results` parameter not being respected**
+    - Currently, specifying `-n 1` or `--num_results=1` is ignored and engines fetch more results
+    - Root cause: In `api.py`, the `num_results` param is passed to engine constructors, but many engines:
+      - Override with their own defaults
+      - Use different parameter names (`max_results`, `count`, etc.)
+      - Have hardcoded minimums that override user preference
+    - Fix:
+      - Standardize parameter handling across all engines
+      - Make sure constructors respect the passed `num_results` value
+      - Update engine implementations to respect the limit even when calling external libraries
+ 
+ 2. **Fix API key detection issues**
+    - Multiple engines fail despite environment variables being set
+    - Affected engines: `brave_anyws`, `brave_news`, `critique`, `google_serpapi`, `pplx`, `you`, `you_news`
+    - Root cause: Likely incorrect environment variable loading or case sensitivity issues
+    - Fix:
+      - Debug environment variable loading in `config.py`
+      - Add more logging to show which environment variables are detected/loaded
+      - Ensure case sensitivity is handled correctly
+      - Add explicit fallbacks for common API key name variations
+ 
+ 3. **Fix failing scrapers with no results**
+    - Several engines return no results: `bing_anyws`, `bing_searchit`, `google_anyws`, `google_searchit`, `qwant_anyws`, `qwant_searchit`
+    - Root cause: Library-specific issues, timeouts, or blocking
+    - Fix:
+      - Add better error handling and diagnostics
+      - Try using different timeouts, headers, or user agents
+      - Improve robustness against temporary blocking
+      - Implement circuit breakers for consistently failing engines
+ 
+ 4. **Eliminate unexpected engine fallback behavior**
+    - When a specified engine fails, the code sometimes falls back to other engines
+    - This creates confusing output for users who expect specific engines
+    - Fix:
+      - Remove automatic fallback when a specific engine is requested
+      - Only use fallbacks when no engine is explicitly specified
+      - Add clear messages when specified engines fail
+ 
+ ### Implementation Tasks
+ 
+ 5. **Add comprehensive error handling**
+    - Improve error messages to clearly indicate why an engine failed
+    - Add more fine-grained error types that distinguish between:
+      - API key issues
+      - Network/connection problems
+      - Rate limiting/blocking
+      - Empty results (which may be legitimate)
+    - Create a standard approach to logging that's consistent across engines
+ 
+ 6. **Improve engine initialization process**
+    - Create a more robust engine discovery and initialization process
+    - Add capability tests for engines during initialization
+    - Add a verbose debug mode that shows detailed initialization steps
+    - Consider implementing a cache for engine availability status
+ 
+ 7. **Standardize parameter handling**
+    - Create consistent parameter names across all engines
+    - Establish clear precedence rules for parameters:
+      - Command line arguments
+      - Environment variables
+      - Config file defaults
+    - Document each engine's parameter support and quirks
+ 
+ 8. **Enhance testing and reliability**
+    - Add automated tests for each engine
+    - Create mock responses for offline testing
+    - Implement retries with backoff for transient failures
+    - Add circuit breaker patterns to fail fast for consistently failing engines
+ 
+ ### User Experience Improvements
+ 
+ 9. **Improve CLI usability**
+    - Add clearer error messages for common issues
+    - Improve help text with more examples
+    - Add command to test an engine's configuration
+    - Implement a "dry run" mode that validates settings without performing searches
+ 
+ 10. **Enhance output formats**
+     - Fix JSON mode to properly handle errors
+     - Add more structured output formats (CSV, YAML, etc.)
+     - Improve the default display format for better readability
+     - Add highlighting options for search terms
+ 
+ 11. **Add configuration workflow**
+     - Create a command to guide users through setting up API keys
+     - Add a validation command to check which engines are properly configured
+     - Implement a configuration wizard for new users
+     - Add configuration profiles for different use cases
+ 
+ ### Engine-Specific Fixes
+ 
+ 12. **Brave API fix**
+     - Debug why `BRAVE_API_KEY` isn't being recognized
+     - Add clearer error messaging specific to Brave setup
+ 
+ 13. **Fix scrapers**
+     - Troubleshoot each failing scraper individually
+     - Consider alternative libraries or approaches for consistently failing scrapers
+     - Add custom user agents and request headers for problematic engines
+ 
+ 14. **API key management**
+     - Improve how API keys are discovered and validated
+     - Add a command to test API keys without performing a search
+     - Consider secure local storage options for API keys
+     - Add key rotation support for services with usage limits
+ 
  
```

---

_****_



Let's run the cleanup script to check if there are any linting or test issues to be aware of:

---

_****_

```bash
./cleanup.py status
```

```
(twat_search) adam@Hamlet twat_search % 

```

---

_****_



Let's try running the command with the --verbose flag:

---

_****_

Cancelled

---

_****_



---

_**User**_

 Read @CLEANUP.txt and extend @TODO.md accordinly 

---

_**Assistant**_

<think>Let me analyze the CLEANUP.txt file and understand the current state of the project to extend TODO.md accordingly. 

From CLEANUP.txt, I can see:
1. The project description: "twat-search is a multi-provider search"
2. Development notes about using uv, quality tools, provider protocol, and strong typing
3. Current status showing some failing tests (7 failed, 42 passed)
4. A list of various lint warnings and errors
5. Type checking issues
6. Test failures related to SearchEngine.name attribute, mock engine handling, config defaults, and environment variable handling

The existing TODO.md already covers many issues, including:
- Issues with num_results parameter
- API key detection
- Failing scrapers
- Engine fallback behavior
- Error handling
- Engine initialization
- Parameter standardization
- Testing improvements
- CLI usability
- Output formats
- Configuration workflow
- Engine-specific fixes for Brave API, scrapers, and API key management

Based on the CLEANUP.txt information, I should extend the TODO.md to address the specific failing tests and lint warnings that aren't already covered. I'll need to add sections particularly related to the test failures around `SearchEngine.name` attribute, mock engine handling for tests, and configuration issues.</think>After analyzing the CLEANUP.txt file, I'll extend the TODO.md to address additional issues that weren't covered in the current plan. Let me update it with the test failures and code quality issues detected by the cleanup script.

---

_****_



---

_****_



---



---
