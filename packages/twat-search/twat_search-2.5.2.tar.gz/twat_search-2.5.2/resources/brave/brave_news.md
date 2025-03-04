[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

# Brave News Search API

Brave Search API is a REST API to query Brave Search and get back search
results from the web. The following sections describe how to curate requests,
including parameters and headers, to Brave Search API and get a JSON response
back.

> To try the API on a Free plan, you’ll still need to subscribe — you simply
> won’t be charged. Once subscribed, you can get an API key in the [API Keys
> section](/app/keys).

## Endpoints

Brave Search API exposes multiple endpoints for specific types of data, based
on the level of your subscription. If you don’t see the endpoint you’re
interested in, you may need to change your subscription.

Brave News Search API is currently available at the following endpoint and
exposes an API to get news from the web relevant to the query.

    
    
    https://api.search.brave.com/res/v1/news/search
    

## Example

Get started immediately with CURL. An example request will look something like
this:

    
    
    
    curl -s --compressed "https://api.search.brave.com/res/v1/news/search?q=munich&count=10&country=us&search_lang=en&spellcheck=1" \
      -H "Accept: application/json" \
      -H "Accept-Encoding: gzip" \
      -H "X-Subscription-Token: <YOUR_API_KEY>"
    

## Next Steps

To learn what parameters are available and what responses can be expected
while querying Brave Search, please review the following pages:

  * [Query Parameters](/app/documentation/news-search/query)
  * [Request Headers](/app/documentation/news-search/request-headers)
  * [Response Headers](/app/documentation/news-search/response-headers)
  * [Response Objects](/app/documentation/news-search/responses)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave News Search API

## Query Parameters

#### # News Search API

This table lists the query parameters supported by the News Search API. Some
are required, but most are optional.

Parameter| Required| Type| Default| Description  
---|---|---|---|---  
q| true| string| |  The user’s search query term. Query can not be empty. Maximum of 400 characters and 50 words in the query.  
country| false| string| US|  The search query country, where the results come
from. The country string is limited to 2 character country codes of supported
countries. For a list of supported values, see [Country
Codes](/app/documentation/news-search/codes#country-codes).  
search_lang| false| string| en|  The search language preference. The 2 or more
character language code for which the search results are provided. For a list
of possible values, see [Language Codes](/app/documentation/news-
search/codes#language-codes).  
ui_lang| false| string| en-US|  User interface language preferred in response.
Usually of the format ‘<language_code>-<country_code>’. For more, see [RFC
9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-language). For a
list of supported values, see [UI Language Codes](/app/documentation/news-
search/codes#market-codes).  
count| false| number| 20|  The number of search results returned in response.
The maximum is `50`. The actual number delivered may be less than requested.
Combine this parameter with `offset` to paginate search results.  
offset| false| number| 0|  The zero based offset that indicates number of
search results per page (count) to skip before returning the result. The
maximum is `9`. The actual number delivered may be less than requested based
on the query. In order to paginate results use this parameter together with
`count`. For example, if your user interface displays 20 search results per
page, set `count` to `20` and offset to `0` to show the first page of results.
To get subsequent pages, increment `offset` by 1 (e.g. 0, 1, 2). The results
may overlap across multiple pages.  
spellcheck| false| bool| 1|  Whether to spellcheck provided query. If the
spellchecker is enabled, the modified query is always used for search. The
modified query can be found in `altered` key from the
[query](/app/documentation/news-search/responses#Query) response model.  
safesearch| false| string| moderate|  Filters search results for adult
content. The following values are supported:

  * `off` \- No filtering.
  * `moderate` \- Filter out explicit content.
  * `strict` \- Filter out explicit and suggestive content.

  
freshness| false| string| |  Filters search results by when they were discovered. The following values are supported: \- `pd`: Discovered within the last 24 hours. \- `pw`: Discovered within the last 7 Days. \- `pm`: Discovered within the last 31 Days. \- `py`: Discovered within the last 365 Days… \- `YYYY-MM-DDtoYYYY-MM-DD`: timeframe is also supported by specifying the date range e.g. `2022-04-01to2022-07-30`.  
extra_snippets| false| bool| |  A snippet is an excerpt from a page you get as a result of the query, and extra_snippets allow you to get up to 5 additional, alternative excerpts. Only available under `Free AI`, `Base AI`, `Pro AI`, `Base Data`, `Pro Data` and `Custom plans`.

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave News Search API

## Request Headers

#### News Search API Request Headers

This table lists the request headers supported by the News Search API, most of
which are optional.

Header| Required| Name| Description  
---|---|---|---  
Accept| false| Accept|  The default supported media type is `application/json`  
Accept-Encoding| false| Accept Encoding|  The supported compression type is
`gzip`.  
Api-Version| false| Web Search API Version|  The Brave Web Search API version
to use. This is denoted by the format `YYYY-MM-DD`. The latest version is used
by default, and the previous ones can be found in the [API Changelog](./api-
changelog).  
Cache-Control| false| Cache Control|  Search will return cached web search
results by default. To prevent caching set the Cache-Control header to `no-
cache`. This is currently done as best effort.  
User-Agent| false| User Agent|  The user agent of the client sending the
request. Search can utilize the user agent to provide a different experience
depending on the client sending the request. The user agent should follow the
commonly used browser agent strings on each platform. For more information on
curating user agents, see [RFC 9110](https://www.rfc-
editor.org/rfc/rfc9110.html#name-user-agent). User agent string examples by
platform:

  * **Android** : Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36
  * **iOS** : Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1
  * **macOS** : Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/
  * **Windows** : Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/

  
X-Subscription-Token| true| Authentication token|  The secret token for the
subscribed plan to authenticate the request. Can be obtained from [API
Keys](/app/keys).

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave News Search API

## Response Headers

#### Global

This table lists the response headers supported by the News Search API.

Header| Name| Description  
---|---|---  
X-RateLimit-Limit| Rate Limit|  Rate limits associated with the requested
plan. An example rate limit `X-RateLimit-Limit: 1, 15000` means 1 request per
second and 15000 requests per month.  
X-RateLimit-Policy| Rate Limit Policy|  Rate limit policies currently
associated with the requested plan. An example policy `X-RateLimit-Policy:
1;w=1, 15000;w=2592000` means a limit of 1 request over a 1 second window and
15000 requests over a month window. The windows are always given in seconds.  
X-RateLimit-Remaining| Rate Limit Remaining|  Remaining quota units associated
with the expiring limits. An example remaining limit `X-RateLimit-Remaining:
1, 1000` indicates the API is able to be accessed once during the current
second, and 1000 times over the current month. **Note** : Only successful
requests are counted and billed.  
X-RateLimit-Reset| Rate Limit Reset|  The number of seconds until the quota
associated with the expiring limits resets. An example reset limit
`X-RateLimit-Reset: 1, 1419704` means a single request can be done again in a
second and in 1419704 seconds the full monthly quota associated with the plan
will be available again.

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave News Search API

## Response Objects

#### # NewsSearchApiResponse

Top level response model for successful News Search API requests. The API can
also respond back with an error response based on invalid subscription keys
and rate limit events.

Field| Type| Description  
---|---|---  
type| "news"| The type of search API result. The value is always news.  
query| Query| News search query string.  
results| list [ NewsResult ]| The list of news results for the given query.  
  
#### # Query

A model representing information gathered around the requested query.

Field| Type| Description  
---|---|---  
original| string| The original query that was requested.  
altered| string| The altered query by the spellchecker. This is the query that
is used to search if any.  
cleaned| string| The cleaned noramlized query by the spellchecker. This is the
query that is used to search if any.  
spellcheck_off| bool| Whether the spell checker is enabled or disabled.  
show_strict_warning| bool| The value is True if the lack of results is due to
a 'strict' safesearch setting. Adult content relevant to the query was found,
but was blocked by safesearch.  
  
#### # NewsResult

A model representing a news result for the requested query.

Field| Type| Description  
---|---|---  
type| news_result| The type of news search API result. The value is always
news_result.  
url| string| The source url of the news article.  
title| string| The title of the news article.  
description| string| The description for the news article.  
age| string| A human readable representation of the page age.  
page_age| string| The page age found from the source web page.  
page_fetched| string| The iso date time when the page was last fetched. The
format is YYYY-MM-DDTHH:MM:SSZ  
breaking| bool| Whether the result includes breaking news.  
thumbnail| Thumbnail| The thumbnail for the news article.  
meta_url| MetaUrl| Aggregated information on the url associated with the news
search result.  
extra_snippets| list [ string ]| A list of extra alternate snippets for the
news search result.  
  
#### # Thumbnail

Aggregated details representing the news thumbnail

Field| Type| Description  
---|---|---  
src| string| The served url of the thumbnail associated with the news article.  
original| string| The original url of the thumbnail associated with the news
article.  
  
#### # MetaUrl

Aggregated information about a url.

Field| Type| Description  
---|---|---  
scheme| string| The protocol scheme extracted from the url.  
netloc| string| The network location part extracted from the url.  
hostname| string| The lowercased domain name extracted from the url.  
favicon| string| The favicon used for the url.  
path| string| The hierarchical path of the url useful as a display string.

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave News Search API

## Codes

#### [#](/app/documentation/news-search/query#country) Country Codes

This table lists the country codes supported by the `country` parameter.

Country| Code  
---|---  
All Regions| ALL  
Argentina| AR  
Australia| AU  
Austria| AT  
Belgium| BE  
Brazil| BR  
Canada| CA  
Chile| CL  
Denmark| DK  
Finland| FI  
France| FR  
Germany| DE  
Hong Kong| HK  
India| IN  
Indonesia| ID  
Italy| IT  
Japan| JP  
Korea| KR  
Malaysia| MY  
Mexico| MX  
Netherlands| NL  
New Zealand| NZ  
Norway| NO  
Peoples Republic of China| CN  
Poland| PL  
Portugal| PT  
Republic of the Philippines| PH  
Russia| RU  
Saudi Arabia| SA  
South Africa| ZA  
Spain| ES  
Sweden| SE  
Switzerland| CH  
Taiwan| TW  
Turkey| TR  
United Kingdom| GB  
United States| US  
  
#### [#](/app/documentation/news-search/query#language) Language Codes

This table lists the language codes supported by the `search_lang` parameter.

Language| Code  
---|---  
Arabic| ar  
Basque| eu  
Bengali| bn  
Bulgarian| bg  
Catalan| ca  
Chinese Simplified| zh-hans  
Chinese Traditional| zh-hant  
Croatian| hr  
Czech| cs  
Danish| da  
Dutch| nl  
English| en  
English United Kingdom| en-gb  
Estonian| et  
Finnish| fi  
French| fr  
Galician| gl  
German| de  
Gujarati| gu  
Hebrew| he  
Hindi| hi  
Hungarian| hu  
Icelandic| is  
Italian| it  
Japanese| jp  
Kannada| kn  
Korean| ko  
Latvian| lv  
Lithuanian| lt  
Malay| ms  
Malayalam| ml  
Marathi| mr  
Norwegian Bokmål| nb  
Polish| pl  
Portuguese Brazil| pt-br  
Portuguese Portugal| pt-pt  
Punjabi| pa  
Romanian| ro  
Russian| ru  
Serbian Cyrylic| sr  
Slovak| sk  
Slovenian| sl  
Spanish| es  
Swedish| sv  
Tamil| ta  
Telugu| te  
Thai| th  
Turkish| tr  
Ukrainian| uk  
Vietnamese| vi  
  
#### [#](/app/documentation/news-search/query#market-code) Market Codes

This table lists the country language codes supported by the `ui_lang`
parameter.

Country| Language| Code  
---|---|---  
Argentina| Spanish| es-AR  
Australia| English| en-AU  
Austria| German| de-AT  
Belgium| Dutch| nl-BE  
Belgium| French| fr-BE  
Brazil| Portuguese| pt-BR  
Canada| English| en-CA  
Canada| French| fr-CA  
Chile| Spanish| es-CL  
Denmark| Danish| da-DK  
Finland| Finnish| fi-FI  
France| French| fr-FR  
Germany| German| de-DE  
Hong Kong SAR| Traditional Chinese| zh-HK  
India| English| en-IN  
Indonesia| English| en-ID  
Italy| Italian| it-IT  
Japan| Japanese| ja-JP  
Korea| Korean| ko-KR  
Malaysia| English| en-MY  
Mexico| Spanish| es-MX  
Netherlands| Dutch| nl-NL  
New Zealand| English| en-NZ  
Norway| Norwegian| no-NO  
People's republic of China| Chinese| zh-CN  
Poland| Polish| pl-PL  
Republic of the Philippines| English| en-PH  
Russia| Russian| ru-RU  
South Africa| English| en-ZA  
Spain| Spanish| es-ES  
Sweden| Swedish| sv-SE  
Switzerland| French| fr-CH  
Switzerland| German| de-CH  
Taiwan| Traditional Chinese| zh-TW  
Turkey| Turkish| tr-TR  
United Kingdom| English| en-GB  
United States| English| en-US  
United States| Spanish| es-US

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search) [ Video
Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search)

[ Get Started](/app/documentation/news-search/get-started)[ Query
Parameters](/app/documentation/news-search/query)[ Request
Headers](/app/documentation/news-search/request-headers)[ Response
Headers](/app/documentation/news-search/response-headers)[ Response
Objects](/app/documentation/news-search/responses)[
Codes](/app/documentation/news-search/codes)[ API
Changelog](/app/documentation/news-search/api-changelog)

[ Suggest](/app/documentation/suggest) [
Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

# Brave Search API Changelog - News

This changelog lists all updates to the Brave News Search API in chronological
order.

### 2023-08-15

  * Add news search.

