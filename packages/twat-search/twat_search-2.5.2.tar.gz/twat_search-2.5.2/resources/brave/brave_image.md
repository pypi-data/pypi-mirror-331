[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

# Brave Search Image Search API

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

Brave Image Search API is currently available at the following endpoint and
exposes an API to get images from the web relevant to the query.

    
    
    https://api.search.brave.com/res/v1/images/search
    
    

## Example

Get started immediately with CURL. An example request will look something like
this:

    
    
    
    curl -s --compressed "https://api.search.brave.com/res/v1/images/search?q=munich&safesearch=strict&count=20&search_lang=en&country=us&spellcheck=1" \
      -H "Accept: application/json" \
      -H "Accept-Encoding: gzip" \
      -H "X-Subscription-Token: <YOUR_API_KEY>"
    

## Next Steps

To learn what parameters are available and what responses can be expected
while querying Brave Search, please review the following pages:

  * [Query Parameters](/app/documentation/image-search/query)
  * [Request Headers](/app/documentation/image-search/request-headers)
  * [Response Headers](/app/documentation/image-search/response-headers)
  * [Response Objects](/app/documentation/image-search/responses)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave Image Search API

## Query Parameters

#### # Image Search API

This table lists the query parameters supported by the Image Search API. Some
are required, but most are optional.

Parameter| Required| Type| Default| Description  
---|---|---|---|---  
q| true| string| |  The user’s search query term. Query can not be empty. Maximum of 400 characters and 50 words in the query.  
country| false| string| US|  The search query country, where the results come
from. The country string is limited to 2 character country codes of supported
countries. For a list of supported values, see [Country
Codes](/app/documentation/image-search/codes#country-codes).  
search_lang| false| string| en|  The search language preference. The 2 or more
character language code for which the search results are provided. For a list
of possible values, see [Language Codes](/app/documentation/image-
search/codes#language-codes).  
count| false| number| 50|  The number of search results returned in response.
The maximum is `100`. The actual number delivered may be less than requested.  
safesearch| false| string| strict|  Filters search results for adult content.
The following values are supported:

  * `off`: No filtering is done.
  * `strict`: Drops all adult content from search results.

  
spellcheck| false| bool| 1|  Whether to spellcheck provided query. If the
spellchecker is enabled, the modified query is always used for search. The
modified query can be found in `altered` key from the
[query](/app/documentation/image-search/responses#Query) response model.

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave Image Search API

## Request Headers

#### Image Search API Request Headers

This table lists the request headers supported by the Image Search API, most
of which are optional.

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
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave Image Search API

## Response Headers

#### Global

This table lists the response headers supported by the Image Search API.

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
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

###### Brave Image Search API

## Response Objects

#### # ImageSearchApiResponse

Top level response model for successful Image Search API requests. The API can
also respond back with an error response based on invalid subscription keys
and rate limit events.

Field| Type| Description  
---|---|---  
type| "images"| The type of search API result. The value is always images.  
query| Query| Image search query string.  
results| list [ ImageResult ]| The list of image results for the given query.  
  
#### # Query

A model representing information gathered around the requested query.

Field| Type| Description  
---|---|---  
original| string| The original query that was requested.  
altered| string| The altered query by the spellchecker. This is the query that
is used to search.  
spellcheck_off| bool| Whether the spell checker is enabled or disabled.  
show_strict_warning| string| The value is True if the lack of results is due
to a 'strict' safesearch setting. Adult content relevant to the query was
found, but was blocked by safesearch.  
  
#### # ImageResult

A model representing an image result for the requested query.

Field| Type| Description  
---|---|---  
type| image_result| The type of image search API result. The value is always
image_result.  
title| string| The title of the image.  
url| string| The original page url where the image was found.  
source| string| The source domain where the image was found.  
page_fetched| string| The iso date time when the page was last fetched. The
format is YYYY-MM-DDTHH:MM:SSZ  
thumbnail| Thumbnail| The thumbnail for the image.  
properties| Properties| Metadata for the image.  
meta_url| MetaUrl| Aggregated information on the url associated with the image
search result.  
  
#### # Thumbnail

Aggregated details representing the image thumbnail

Field| Type| Description  
---|---|---  
src| string| The served url of the image.  
  
#### # Properties

Metadata on an image.

Field| Type| Description  
---|---|---  
url| string| The image URL.  
placeholder| string| The lower resolution placeholder image url.  
  
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
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

## Codes

#### [#](/app/documentation/image-search/query#country) Country Codes

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
  
#### [#](/app/documentation/image-search/query#language) Language Codes

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

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

# Brave Search API Changelog - Images

This changelog lists all updates to the Brave Image Search API in
chronological order.

### 2023-08-09

  * Initial release of the Image Search API.

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard)

[![Brave](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/brave-
logo.BytqdRrN.svg)](/app/dashboard) [ Documentation](/app/documentation)

[ Web Search](/app/documentation/web-search) [ Summarizer
Search](/app/documentation/summarizer-search) [ Image
Search](/app/documentation/image-search)

[ Get Started](/app/documentation/image-search/get-started)[ Query
Parameters](/app/documentation/image-search/query)[ Request
Headers](/app/documentation/image-search/request-headers)[ Response
Headers](/app/documentation/image-search/response-headers)[ Response
Objects](/app/documentation/image-search/responses)[
Codes](/app/documentation/image-search/codes)[ API
Changelog](/app/documentation/image-search/api-changelog)[ How to
Guides](/app/documentation/image-search/guides)

[ Video Search](/app/documentation/video-search) [ News
Search](/app/documentation/news-search) [ Suggest](/app/documentation/suggest)
[ Spellcheck](/app/documentation/spellcheck) [
General](/app/documentation/general)

[Login](/login) [Register](/register)

# A simple guide to handle missing and small image results

##### Brave Search Image API

There are two limitations of the Brave Search Image API:

  * the image results could be pointing to urls that cannot be resolved (404)
  * the image dimensions `width` and `height` are not provided ahead of time.

We’ve worked around the very same limitations to build our image search
vertical at [search.brave.com/images](https://search.brave.com/images?q=cats).
This guide is a simpler version of the same approach.

Our project structure will be this:

    
    
    index.js
    public/
        images.html
        styles.css
    

To get started, let’s create a folder for our image search page as well as
create the files we will need later on:

    
    
    mkdir img-search && cd img-search
    mkdir public
    touch public/images.html
    touch public/styles.css
    

We’ll use a simple [node.js express server](https://expressjs.com/) to call
the API. So let’s go ahead and install it as a dependency (our only one).

    
    
    npm install express --save
    

The following `index.js` is our server, and will be handling the API calls. It
has to be done through a server environment so that there are no Cross-Origin
Resource Sharing ([CORS](https://developer.mozilla.org/en-
US/docs/Web/HTTP/CORS)) issues.

#### index.js

    
    
    const express = require('express');
    const app = express();
    const port = 4000;
    
    app.use(express.static('public'));
    
    const API_KEY = '<YOUR_API_KEY>';
    const API_PATH = 'https://api.search.brave.com/res/v1/images/search';
    
    app.get('/api/images', async (req, res) => {
      try {
        const params = new URLSearchParams({
          q: req.query.q,
          count: 20,
          search_lang: 'en',
          country: 'us',
          spellcheck: 1,
        });
        const response = await fetch(`${API_PATH}?${params}`, {
          headers: {
            'x-subscription-token': API_KEY,
            accept: 'application/json',
          },
        });
        const data = await response.json();
        res.json(data);
        return;
      } catch (err) {
        console.log(err);
      }
      res.status(500).send('Internal Server Error');
    });
    
    app.listen(port, () => {
      console.log(`Example app listening on port ${port}`);
    });
    

Now that we have our server, let’s focus on the client side scripts needed to
load image outside of the DOM, to learn if they exist, and what the `width`
and `height` is.

#### public/images.html

    
    
    <html>
      <head>
        <title>Image Search</title>
        <link rel="stylesheet" href="/styles.css" />
      </head>
      <body>
        <script lang="javascript">
          async function fetchImages(query) {
            const params = new URLSearchParams({ q: query });
            const response = await fetch(`/api/images?${params}`);
            return await response.json();
            return data;
          }
    
          function renderImages(images) {
            const imagesContainer = document.getElementById('images');
            imagesContainer.innerHTML = '';
            images.forEach(({ image }) => {
              const figElement = document.createElement('figure');
    
              const imgElement = document.createElement('img');
              imgElement.src = image.thumbnail.src;
              imgElement.alt = image.title;
              imgElement.width = image.thumbnail.width;
              imgElement.height = image.thumbnail.height;
    
              const figCaptionElement = document.createElement('figcaption');
              figCaptionElement.innerHTML =
                `<div class="dimensions">${image.thumbnail.width} x ${image.thumbnail.height}</div>` +
                image.title;
    
              figElement.appendChild(imgElement);
              figElement.appendChild(figCaptionElement);
    
              imagesContainer.appendChild(figElement);
            });
          }
    
          function loadImage(result) {
            return new Promise((resolve, reject) => {
              const img = new Image();
              img.crossOrigin = 'anonymous';
              img.onload = (e) => {
                if (e.target) {
                  const image = e.target;
                  const width = image.naturalWidth;
                  const height = image.naturalHeight;
    
                  // Filter images that are too small
                  if (width < 275 || height < 275) {
                    console.error('[Img] Image too small', result);
                    reject(result);
                    return;
                  }
    
                  // Fill missing info; use the size the image will be scaled into instead of actual size
                  result.thumbnail.width = width;
                  result.thumbnail.height = height;
    
                  resolve(result);
                } else {
                  console.error('[Img] onLoad returned no image', result);
                  reject(result);
                }
              };
              img.onerror = (e) => {
                console.error('[Img] onError loading img', e);
                reject(result);
              };
              img.onabort = (e) => {
                console.error('[Img] onAbort loading img', e);
                reject(result);
              };
              img.src = result.thumbnail.src;
            });
          }
    
          async function load(query) {
            // Load images from API
            const response = await fetchImages(query);
            const loadedImages = [];
            let i = 0;
            const count = 5;
            const initialPromises = [];
    
            // Load the first 5 images in parallel
            for (let i = 0; i < count; i++) {
              initialPromises.push(async () => {
                const result = response.results[i];
                try {
                  const image = await loadImage(result);
                  loadedImages.push({
                    image,
                  });
                } catch (err) {
                  // pass
                }
              });
            }
    
            // Wait for the first 5 images to resolve
            await Promise.all(initialPromises);
    
            // Load images sequentially until there is 5 results, then show them.
            while (loadedImages.length < 5 || i >= response.results.length) {
              const result = response.results[i];
              try {
                const image = await loadImage(result);
                loadedImages.push({
                  image,
                });
              } catch (err) {
                // pass
              }
              i++;
            }
    
            renderImages(loadedImages);
          }
        </script>
        <div id="search">
          <input type="text" id="query" value="" onchan />
          <button onclick="load(document.getElementById('query').value)">Search</button>
        </div>
        <div id="images"></div>
      </body>
    </html>
    

The approach here, is to load images outside of the DOM, 5 at a time (which
you can configure), and images that we manage successfully, and are larger
than a given size (`width > 275 || height > 275` in the example), we show in
the DOM.

Lastly, we need some styles to make sure what we see does not look too bad:

### styles.css

    
    
    #images {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      max-width: 1000px;
      margin: 2rem auto;
      justify-content: center;
    }
    #search {
      display: flex;
      gap: 1rem;
      align-items: center;
      width: 600px;
      margin: auto;
    }
    #search input {
      width: 100%;
      padding: 10px 20px;
      border-radius: 12px;
      outline: none;
      border: solid 1px #d3d3d3;
      background: #f3f3f3;
    }
    button {
      cursor: pointer;
      padding: 10px 20px;
      border-radius: 12px;
      outline: none;
      border: solid 1px #d3d3d3;
      background: #f3f3f3;
    }
    button:hover {
      background: #111;
      color: #fff;
    }
    figure {
      border: solid 1px #d3d3d3;
      display: flex;
      flex-flow: column;
      padding: 5px 5px 10px 5px;
      max-width: 220px;
      gap: 1rem;
      border-radius: 12px;
      margin: 0;
    }
    
    img {
      max-width: 220px;
      max-height: 150px;
      object-fit: contain;
      border-radius: 12px;
    }
    
    figcaption {
      display: flex;
      text-align: center;
      font-family: sans-serif;
      font-size: 14px;
      flex-direction: column;
      gap: 5px;
      align-items: center;
    }
    figcaption .dimensions {
      font-size: 12px;
      color: blue;
      background: #e7e7fc;
      padding: 5px 10px;
      border-radius: 12px;
      width: fit-content;
    }
    

And we’re ready to go. You can now run the project:

    
    
    node index.js
    

Open `localhost:4000/images.html` in the browser, and start searching.

![Image Search Client](https://cdn.search.brave.com/search-
api/web/v1/client/_app/immutable/assets/img-search-client.Yjc8cU7X.png)

