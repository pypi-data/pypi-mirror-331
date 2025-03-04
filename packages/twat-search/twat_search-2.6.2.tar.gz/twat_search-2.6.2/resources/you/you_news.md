[You.com API home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/dark.svg)](/)

Search or ask...

  * [Discord](https://discord.com/invite/youdotcom)
  * [Support](mailto:api@you.com)
  * [Support](mailto:api@you.com)

Search...

Navigation

API Guide

News API

[Welcome](/welcome)[Quickstart](/docs/quickstart)[API Reference](/api-
reference/smart)[API Guide](/api-modes/smart-api)

##### API Guide

  * [Smart API](/api-modes/smart-api)
  * [Research API](/api-modes/research-api)
  * [Search API](/api-modes/search-api)
  * [News API](/api-modes/news-api)

##### Custom

  * [Custom APIs](/api-modes/custom-api)

API Guide

# News API

##

​

Stay Informed with the Latest Global News

When interacting with news results, LLMs are currently facing challlenges:

## Lack of News-Specific Filtering

LLMs lack the capability to focus exclusively on real-time news updates,
limiting their relevance for time-sensitive information.

## Limited Recency Filtering

Models are generally unable to filter news based on specific timeframes,
preventing users from accessing the most relevant information for them.

With our **News API** , we ensure you have reliable insights into global news
and events, keeping you informed about the latest stories and developments
worldwide

## Access to Live News

Our API integrates live news data, providing long snippets from trusted
sources, complete with URLs for verification.

## Customizable Recency and Region

For news results, users can filter data by timeframes such as the past day,
week, or month, enabling access to the insights you need.

## Uniquely Long Snippets

Ensure your responses are trustworthy and contain the information you need.

##

​

Use Cases

## Stay Up to Date

  

Current Developments in Key Areas of Interest

query.py

    
    
    import requests
    
    url = "https://api.ydc-index.io/news"
    
    query = {"query":"Latest News on Chipmakers"}
    
    headers = {"X-API-Key": "YOUR_API_KEY"}
    
    response = requests.request("GET", url, headers=headers, params=query)
    
    print(response.text)
    

Response

    
    
    {
    "news": {
    "query": {
      "original": "Latest News on Chipmakers",
      "show_strict_warning": false,
      "spellcheck_off": false
    },
    "results": [
      {
        "age": "4 days ago",
        "description": "The country that was once the world’s largest producer of semiconductors has embarked on a quest to return to the top.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› opinion  › articles  › 2024-12-12  › japan-chipmakers-gamble-the-future-of-semiconductors-on-the-past",
          "scheme": "https"
        },
        "page_age": "2024-12-12T22:37:49",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/qlX4Mz061puuwMyZm1FuXEbSGXuCbqjHIypccDoXGqw/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2lYTWNFSDBjMFli/OC92MS8xMjAweDgw/MC5qcGc"
        },
        "title": "Japan Chipmakers Gamble the Future of Semiconductors on the Past - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/opinion/articles/2024-12-12/japan-chipmakers-gamble-the-future-of-semiconductors-on-the-past"
      },
      {
        "age": "2 weeks ago",
        "description": "Chinese companies should buy locally instead, four of the country's top industry associations said.",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› technology  › chinese-firms-should-diversify-chip-sources-internet-society-china-says-2024-12-03",
          "scheme": "https"
        },
        "page_age": "2024-12-04T12:28:42",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/BuXIjhV4mQs66s0tgItvuiy4x3EBC-ZpqgaeQsLvF-Y/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi9S/WlRXVE9YSkNCUDVS/RzM3RURQRERMWTdM/US5qcGc_YXV0aD02/YTI3MDBmMjJhMGJj/Y2I4NzE0OTM4M2Qz/YTZlODkyODg4YWI4/YTk4MTUwMmI2NGQ1/MDNlNDZmZDY0YjVl/MjRkJmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "US chips are 'no longer safe,' Chinese industry bodies say in latest trade salvo | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/technology/chinese-firms-should-diversify-chip-sources-internet-society-china-says-2024-12-03/"
      },
      {
        "age": "2 weeks ago",
        "description": "Microchip Technology Inc. is pausing its application for US semiconductor subsidies, making it the first known company to step back from a program designed to revitalize American chipmaking.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › articles  › 2024-12-03  › microchip-pauses-chips-act-application-after-scaling-back-plans",
          "scheme": "https"
        },
        "page_age": "2024-12-03T22:47:04",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/va8gs8bDTD44dQtxAjHvM8dB9Trdl_puEs2DlPWJlRM/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2llQThZQ3hjNXFp/TS92MC8xMjAweDgw/MC5qcGc"
        },
        "title": "Microchip Pauses Chips Act Application Amid Inventory Woes - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/articles/2024-12-03/microchip-pauses-chips-act-application-after-scaling-back-plans"
      },
      {
        "age": "2 weeks ago",
        "description": "The Chinese government has slammed America’s introduction of fresh export controls on US-made semiconductors that Washington fears Beijing could use to make the next generation of weapons and artificial intelligence (AI) systems.",
        "meta_url": {
          "hostname": "www.cnn.com",
          "netloc": "cnn.com",
          "path": "› 2024  › 12  › 02  › tech  › china-us-chips-new-restrictions-intl-hnk  › index.html",
          "scheme": "https"
        },
        "page_age": "2024-12-03T02:18:13",
        "source_name": "CNN",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/Q7u2YWA5NPRkhPy3LpctiPU11jkmoP6uYjggAeJ4J6s/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5jbm4uY29tL2Fw/aS92MS9pbWFnZXMv/c3RlbGxhci9wcm9k/L2FwMjQyOTE1NDEy/Njk1OTEtY29weS5q/cGc_Yz0xNng5JnE9/d184MDAsY19maWxs"
        },
        "title": "AI and semiconductors: China hits out at latest US effort to block Beijing’s access to chip technology | CNN Business",
        "type": "news_result",
        "url": "https://www.cnn.com/2024/12/02/tech/china-us-chips-new-restrictions-intl-hnk/index.html"
      },
      {
        "age": "2 weeks ago",
        "description": "The US will launch its third crackdown in three years on China's semiconductor industry on Monday, restricting exports to 140 companies.",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› technology  › latest-us-strike-chinas-chips-hits-semiconductor-toolmakers-2024-12-02",
          "scheme": "https"
        },
        "page_age": "2024-12-03T01:14:17",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/UQxYf9pHn51WR53MNkbaa9ieeQZStKI64CetvaW6Tt4/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi9E/VlRNTERBWkRWSkk3/RTdDUzZJUEtEUVRV/RS5qcGc_YXV0aD0x/OGZkYzAxZmNlZmEx/ZDk4MjIxODFhYTY0/YzA2YTBjNWFjMDk4/YWIxMmM2NzBjZmRh/NDlmYmRkY2Y2MDNh/ZjY0JmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "Latest US clampdown on China's chips hits semiconductor toolmakers | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/technology/latest-us-strike-chinas-chips-hits-semiconductor-toolmakers-2024-12-02/"
      },
      {
        "age": "3 weeks ago",
        "description": "There’s been a sea change among tech investors during the past month: Software stocks are hot, while semiconductor makers are not.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › articles  › 2024-11-26  › software-is-in-chips-are-out-as-traders-position-for-trump-era",
          "scheme": "https"
        },
        "page_age": "2024-11-26T12:01:25",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/LxYcJMko0ujutqhct8xx6kD_wc32kwIH0BJJTPle4cM/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2k3aDhSbUZuMjcy/US92MC8xMjAweDgw/MC5qcGc"
        },
        "title": "Software Is In, Chips Are Out as Traders Position for Trump Era - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/articles/2024-11-26/software-is-in-chips-are-out-as-traders-position-for-trump-era"
      },
      {
        "age": "4 weeks ago",
        "description": "Understanding how AI impacts business. The latest news on advancements in artificial intelligence, how to use AI, and how to invest in AI.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› ai",
          "scheme": "https"
        },
        "page_age": "2024-11-21T21:05:04",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/m7Jfen96xPtekEXCptzbwN1D52cE6auJKE9sP5DajpU/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/Ymxvb21iZXJnLmNv/bS9haQ"
        },
        "title": "AI - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/ai"
      },
      {
        "age": "1 month ago",
        "description": "The Biden administration is trying to shore up its CHIPS Act funding agreements before Donald Trump takes office.",
        "meta_url": {
          "hostname": "www.businessinsider.com",
          "netloc": "businessinsider.com",
          "path": "› chips-act-funding-biden-administration-trump-tariffs-repeal-2024-11",
          "scheme": "https"
        },
        "page_age": "2024-11-19T09:15:01",
        "source_name": "Business Insider",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/_16b6eIPhruMXBpV8ovQHxtj5qc_0nTGW5SHlHYseAg/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLmlu/c2lkZXIuY29tLzY3/M2JiM2Y0ZmEwMTQw/Y2RkNTY0Mjk5ZT93/aWR0aD0xMjAwJmZv/cm1hdD1qcGVn"
        },
        "title": "The Biden administration is scrambling to send billions to chipmakers before Trump takes over",
        "type": "news_result",
        "url": "https://www.businessinsider.com/chips-act-funding-biden-administration-trump-tariffs-repeal-2024-11"
      },
      {
        "age": "1 month ago",
        "description": "JONATHAN: NVIDIA IS HUGE SO WE ALL HAVE EXPOSURE TO IT ONE WAY OR ANOTHER. EXPLAIN THE STORY THIS MORNING, REPORTING THE CHIPMAKER IS FACING A DESIGN SNACK FOR THE BLACKWELL CHIPS. WE SEE THAT DROPPING IN AND OUT OF THE NEWS REPEATEDLY, SHAKING UP THE STOCK FROM TIME TO TIME.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › videos  › 2024-11-18  › chipmakers-hope-for-a-boost-from-nvidia-earnigns-video",
          "scheme": "https"
        },
        "page_age": "2024-11-18T14:17:33",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/BzYM6UHOgK9rvTWBxa_JK-buc5-4LfUelVxMrd_tl6A/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2lCejhkVm53dEVo/WS92My8tMXgtMS5q/cGc"
        },
        "title": "Watch Chipmakers Hope for a Boost From Nvidia Earnings - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/videos/2024-11-18/chipmakers-hope-for-a-boost-from-nvidia-earnigns-video"
      },
      {
        "age": "1 month ago",
        "description": "Nov 17 (Reuters) - Nvidia's (NVDA.O), ... reported on Sunday. The Blackwell graphics processing units overheat when connected together in server racks designed to hold up to 72 chips, the report said, citing sources familiar with the issue. The chipmaker has asked its suppliers ...",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› technology  › artificial-intelligence  › new-nvidia-ai-chips-face-issue-with-overheating-servers-information-reports-2024-11-17",
          "scheme": "https"
        },
        "page_age": "2024-11-17T22:36:10",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/16Jgf2p3zxsmMnQUzOrP7EhvynVj9rnuSDEGYINQ-HQ/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi9W/VFhIVkFJM1ZCT1lU/QVFSRzdOQlZMNUVJ/SS5qcGc_YXV0aD1m/ODQxZmExMzY3ODMz/ZGRjMmJhMTQ5MzJi/YTQ5Yzc2ZmY2MTNm/NmI0MWI3ZjM3Y2Yx/ZDU5ZDZiZjA2ZjYw/ZjJhJmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "New Nvidia AI chips overheating in servers, the Information reports | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/technology/artificial-intelligence/new-nvidia-ai-chips-face-issue-with-overheating-servers-information-reports-2024-11-17/"
      },
      {
        "age": "November 8, 2024",
        "description": "China hardliners in Congress are calling on the world's foremost semiconductor equipment makers - KLA , LAM , Applied Materials , Tokyo Electron and ASML - to provide details of their sales to China.",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› technology  › us-lawmakers-press-top-chip-equipment-makers-details-china-sales-2024-11-08",
          "scheme": "https"
        },
        "page_age": "2024-11-08T18:05:21",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/UQxYf9pHn51WR53MNkbaa9ieeQZStKI64CetvaW6Tt4/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi9E/VlRNTERBWkRWSkk3/RTdDUzZJUEtEUVRV/RS5qcGc_YXV0aD0x/OGZkYzAxZmNlZmEx/ZDk4MjIxODFhYTY0/YzA2YTBjNWFjMDk4/YWIxMmM2NzBjZmRh/NDlmYmRkY2Y2MDNh/ZjY0JmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "US lawmakers press top chip equipment makers for details on China sales | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/technology/us-lawmakers-press-top-chip-equipment-makers-details-china-sales-2024-11-08/"
      },
      {
        "age": "November 8, 2024",
        "description": "The Biden administration is racing to complete Chips Act agreements with companies like Intel Corp. and Samsung Electronics Co., aiming to shore up one of its signature initiatives before President-elect Donald Trump enters the White House.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › articles  › 2024-11-08  › trump-s-win-sets-off-race-to-complete-chips-act-subsidy-deals",
          "scheme": "https"
        },
        "page_age": "2024-11-08T01:42:07",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/ei0BLNvbyDZ0k8vGo3QdI7Pm8QtABfzqpfz0ucNHOa0/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2l4T25CbS4zdFhq/Yy92MC8xMjAweDgw/MC5qcGc"
        },
        "title": "Trump’s Win Has Biden Rushing to Finalize Chips Act Deals With Intel, Samsung - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/articles/2024-11-08/trump-s-win-sets-off-race-to-complete-chips-act-subsidy-deals"
      },
      {
        "age": "November 4, 2024",
        "description": "Intel has fallen so far so fast that the chipmaker's stock price is no longer having an impact on the Dow Jones Industrial Average.",
        "meta_url": {
          "hostname": "www.cnbc.com",
          "netloc": "cnbc.com",
          "path": "› 2024  › 11  › 04  › the-dow-needs-nvidia-because-intel-plunge-made-semis-underrepresented.html",
          "scheme": "https"
        },
        "page_age": "2024-11-04T20:59:19",
        "source_name": "CNBC",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/1uMlnbYCbjdLfqxeP9fQOibcd2dVPGJwIDWZ65jYr8k/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWFn/ZS5jbmJjZm0uY29t/L2FwaS92MS9pbWFn/ZS8xMDgwMzI5OTIt/MTcyNjEwNzgwMzAw/NS1nZXR0eWltYWdl/cy0yMTU1MTI3Mzc5/LU5WSURJQV9IVUFO/Ry5qcGVnP3Y9MTcz/MjE5ODI4OCZhbXA7/dz0xOTIwJmFtcDto/PTEwODA"
        },
        "title": "The Dow needs Nvidia to give chipmakers representation in index after Intel's plunge",
        "type": "news_result",
        "url": "https://www.cnbc.com/2024/11/04/the-dow-needs-nvidia-because-intel-plunge-made-semis-underrepresented.html"
      },
      {
        "age": "October 30, 2024",
        "description": "Global stock indexes edged lower on Wednesday as a disappointing forecast from Advanced Micro Devices weighed on chipmakers, while gold prices rose to a record high as uncertainty ahead of next week's U.S. presidential election drove safe-haven demand.",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› markets  › global-markets-wrapup-1-2024-10-30",
          "scheme": "https"
        },
        "page_age": "2024-10-30T21:05:08",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/nzLyG1gwaIEPPDPWvUB6P6_z5aoPvHTWttuhFJ-AZZ4/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi9O/MkJQN0VHM1RGT0dI/REFMSlFGVDNJRTZa/WS5qcGc_YXV0aD0z/YmE1ZmUyZGZkYzkx/MjAzZmU0YzVjZWE2/MWNhNmJiNjUzYTc0/ZjhlMjQxMjEzNDAx/NTUzYTYyMWZiODdm/M2E3JmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "Stocks fall with chipmakers, gold hits record high | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/markets/global-markets-wrapup-1-2024-10-30/"
      },
      {
        "age": "October 30, 2024",
        "description": "OpenAI is working with Broadcom and TSMC to build its first in-house chip designed to support its artificial intelligence systems, while adding AMD chips alongside Nvidia chips to meet its surging infrastructure demands, sources told Reuters.",
        "meta_url": {
          "hostname": "www.reuters.com",
          "netloc": "reuters.com",
          "path": "› technology  › artificial-intelligence  › openai-builds-first-chip-with-broadcom-tsmc-scales-back-foundry-ambition-2024-10-29",
          "scheme": "https"
        },
        "page_age": "2024-10-30T15:30:09",
        "source_name": "reuters.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/JfpxYjJ_YO4fhT-Ejlkn0j1V4oqVpLdCQ7LIqyAlBOM/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/cmV1dGVycy5jb20v/cmVzaXplci92Mi83/M0I1NTRIS0JCTUZI/S0tNTE82RlZFVTNH/US5qcGc_YXV0aD04/NDlhODM1MDIwZGVj/YjBhMjI1ZDM5MGVk/YmE4NzI0YTNkMWYz/YzI2ZmE1YjM4OGMy/ZWU1Y2NkNWVkZmU3/YWYzJmFtcDtoZWln/aHQ9MTAwNSZhbXA7/d2lkdGg9MTkyMCZh/bXA7cXVhbGl0eT04/MCZhbXA7c21hcnQ9/dHJ1ZQ"
        },
        "title": "Exclusive: OpenAI builds first chip with Broadcom and TSMC, scales back foundry ambition | Reuters",
        "type": "news_result",
        "url": "https://www.reuters.com/technology/artificial-intelligence/openai-builds-first-chip-with-broadcom-tsmc-scales-back-foundry-ambition-2024-10-29/"
      },
      {
        "age": "October 16, 2024",
        "description": "A rally in semiconductor names and strong economic data sent stocks higher on Thursday.",
        "meta_url": {
          "hostname": "www.cnbc.com",
          "netloc": "cnbc.com",
          "path": "› 2024  › 10  › 16  › stock-market-today-live-updates.html",
          "scheme": "https"
        },
        "page_age": "2024-10-16T22:02:35",
        "source_name": "CNBC",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/3z4hAEdUIDVi62nmwGTixjpwr8RNndn7RzgS7AzkBpU/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWFn/ZS5jbmJjZm0uY29t/L2FwaS92MS9pbWFn/ZS8xMDgwNDQ3MjUt/MTcyODM5Nzg5MDg1/NC1nZXR0eWltYWdl/cy0yMTc3NDM3MDE5/LW1zMV8xNzQ0X3ln/cXlwem9oLmpwZWc_/dj0xNzI5MTgxMTAz/JmFtcDt3PTE5MjAm/YW1wO2g9MTA4MA"
        },
        "title": "Dow closes at fresh record, Nasdaq ends higher as chipmakers rally: Live updates",
        "type": "news_result",
        "url": "https://www.cnbc.com/2024/10/16/stock-market-today-live-updates.html"
      },
      {
        "age": "October 16, 2024",
        "description": "ASML’s surprise results have implications for the overall chip industry. But first...",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › newsletters  › 2024-10-16  › asml-s-surprise-results-signal-uncertain-future-for-some-chipmakers",
          "scheme": "https"
        },
        "page_age": "2024-10-16T11:05:28",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/CCtgpMYTTo_tqrCUjHj2hE4j33_v3pN_12gPUXztUOk/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2k1QnRoejdlb1Zt/TS92MS8xMjAweDgw/MC5qcGc"
        },
        "title": "ASML’s Surprise Results Signal Uncertain Future for Some Chipmakers - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/newsletters/2024-10-16/asml-s-surprise-results-signal-uncertain-future-for-some-chipmakers"
      },
      {
        "age": "October 16, 2024",
        "description": "ASML Holding NV has lost more than €60 billion ($65.3 billion) in market value since it reported weak orders for its chipmaking machines, forcing investors to reevaluate the health of the industry.",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › articles  › 2024-10-16  › asml-s-tumble-fuels-questions-about-chip-industry-s-prospects",
          "scheme": "https"
        },
        "page_age": "2024-10-16T10:36:26",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/FRs8PrWQma_nu8Z4wCUNX20wYoNYhRPA5K8oYZWYcL0/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2k2dUkwNDdXTWpC/OC92MC8xMjAweDgw/MC5qcGc"
        },
        "title": "ASML’s Plunge Shows the Diverging Fortunes of Chipmakers From AI - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/articles/2024-10-16/asml-s-tumble-fuels-questions-about-chip-industry-s-prospects"
      },
      {
        "age": "October 16, 2024",
        "description": "Chip stocks fell Tuesday. ASML slashed its guidance for 2025, and the sector mulled reports of more potential restrictions on chip exports from some US firms.",
        "meta_url": {
          "hostname": "ca.finance.yahoo.com",
          "netloc": "ca.finance.yahoo.com",
          "path": "› news  › chipmakers-tumble-asml-forecast-cut-030444530.html",
          "scheme": "https"
        },
        "page_age": "2024-10-16T03:04:44",
        "source_name": "ca.finance.yahoo.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/a2VYr800beR71JP283brHdStO-voqPux2jfJuPjnnuw/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9zLnlp/bWcuY29tL255L2Fw/aS9yZXMvMS4yL1ho/OU5CUEk1WEFLR2Np/S3puREk1TmctLS9Z/WEJ3YVdROWFHbG5h/R3hoYm1SbGNqdDNQ/VEV5TURBN2FEMDVN/REEtL2h0dHBzOi8v/bWVkaWEuemVuZnMu/Y29tL2VuL2J1c2lu/ZXNzX2luc2lkZXJf/YXJ0aWNsZXNfODg4/LzEzMjI5YmQ0OWEz/NjhmYzQ4YmViZWZl/ZjUwZTcwMjU4"
        },
        "title": "Chipmakers tumble as ASML forecast cut issues a growth warning to the sector",
        "type": "news_result",
        "url": "https://ca.finance.yahoo.com/news/chipmakers-tumble-asml-forecast-cut-030444530.html"
      },
      {
        "age": "October 15, 2024",
        "description": "Manage your newsletter preferences anytime here. ASML Holding’s shares plunged the most in 26 years after it booked only about half the orders analysts expected, a startling slowdown for the Dutch company, maker of the world’s most advanced chip-making machines and one of the bellwethers ...",
        "meta_url": {
          "hostname": "www.bloomberg.com",
          "netloc": "bloomberg.com",
          "path": "› news  › newsletters  › 2024-10-15  › asml-shares-plunge-amid-strange-times-for-chipmakers-like-intel-samsung",
          "scheme": "https"
        },
        "page_age": "2024-10-15T22:14:46",
        "source_name": "Bloomberg L.P.",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/iQL7-057RrQw0oDsHMrzhHX5ksoVJeP0D_tecxHpO1E/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuYndieC5pby9p/bWFnZXMvdXNlcnMv/aXFqV0hCRmRmeElV/L2lhaWNjSmhPMTc4/US92MC8xMjAweDgw/MC5qcGc"
        },
        "title": "ASML Shares Plunge Amid Strange Times for Chipmakers Like Intel, Samsung - Bloomberg",
        "type": "news_result",
        "url": "https://www.bloomberg.com/news/newsletters/2024-10-15/asml-shares-plunge-amid-strange-times-for-chipmakers-like-intel-samsung"
      }
    ],
    "type": "news"
    }
    }
    

Country-specific Industry Overviews

query.py

    
    
    import requests
    
    url = "https://api.ydc-index.io/news"
    
    querystring = {"query":"News on the Chemical Industry", "country":"IN"}
    
    headers = {"X-API-Key": "YOUR_API_KEY"}
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    print(response.text)
    

reponse

    
    
    {
    "news": {
    "query": {
      "original": "Chemical Industry",
      "show_strict_warning": false,
      "spellcheck_off": false
    },
    "results": [
      {
        "age": "2 weeks ago",
        "description": "On December 3 2024 Sudarshan Chemical Industries a midcap company in the dyes and pigments industry saw a 5 02 increase in its stock outperforming the sector by 2 7 This marks the fourth consecutive day of gains with a total increase of 11 34 in the past four days The stock is currently trading ...",
        "meta_url": {
          "hostname": "www.marketsmojo.com",
          "netloc": "marketsmojo.com",
          "path": "› news  › stocks-in-action  › sudarshan-chemical-industries-stock-sees-positive-trend-outperforms-sector-and-market-308679",
          "scheme": "https"
        },
        "page_age": "2024-12-03T05:30:02",
        "source_name": "marketsmojo.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/YiUpk2EMKEHCCGwC57406-c57F3JKfEZr6r3jUKE_jk/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLm1h/cmtldHNtb2pvLmNv/bS9uZXdzaW1nLzIw/MjQvMTIvU3VkYXJz/aGFuQ2hlbWljX3By/aWNlUmVsYXRlZGZh/Y3RvcnNfMjMxNjI5/LnBuZw"
        },
        "title": "Sudarshan Chemical Industries' Stock Sees Positive Trend, Outperforms Sector and Market",
        "type": "news_result",
        "url": "https://www.marketsmojo.com/news/stocks-in-action/sudarshan-chemical-industries-stock-sees-positive-trend-outperforms-sector-and-market-308679"
      },
      {
        "age": "2 weeks ago",
        "description": "Chemical industry in Tamil Nadu faces challenges, seeks government support for cracker project, growth projections shared at Chemvision 2024.",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› news  › national  › tamil-nadu  › chemical-industry-calls-for-cracker-project-to-boost-growth-in-tamil-nadu  › article68927363.ece",
          "scheme": "https"
        },
        "page_age": "2024-12-02T15:30:31",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/MbaLnkSns7korT9MlnYjmNHGa1WUAhQ3UWPKsATH8sw/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly90aC1p/LnRoZ2ltLmNvbS9w/dWJsaWMvaW5jb21p/bmcvNnppYXh2L2Fy/dGljbGU2ODkzOTQ1/Ni5lY2UvYWx0ZXJu/YXRlcy9MQU5EU0NB/UEVfMTIwMC9CVlJf/NDQ1NS5KUEc"
        },
        "title": "Chemical industry calls for cracker project to boost growth in Tamil Nadu - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/chemical-industry-calls-for-cracker-project-to-boost-growth-in-tamil-nadu/article68927363.ece"
      },
      {
        "age": "2 weeks ago",
        "description": "Paradeep Phosphates Limited has taken the planned shutdown of the ammonia and urea plants at Goa",
        "meta_url": {
          "hostname": "www.indianchemicalnews.com",
          "netloc": "indianchemicalnews.com",
          "path": "› general  › briefs-paradeep-phosphates-and-upl-24269",
          "scheme": "https"
        },
        "page_age": "2024-12-02T14:35:03",
        "source_name": "indianchemicalnews.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/Vl4q-rbHKGG5hwNVyuoaLx_Igp-MdbrerzkvrrHSwGQ/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/aW5kaWFuY2hlbWlj/YWxuZXdzLmNvbS9w/dWJsaWMvdXBsb2Fk/cy9uZXdzLzIwMjQv/MTIvMjQyNjkvVVBM/X2xvZ29fb3JpZ2lu/YWwuanBn"
        },
        "title": "Briefs: Paradeep Phosphates and UPL",
        "type": "news_result",
        "url": "https://www.indianchemicalnews.com/general/briefs-paradeep-phosphates-and-upl-24269"
      },
      {
        "age": "2 weeks ago",
        "description": "Press release - Exactitude Consultancy - Crop Protection Chemicals Market Detailed Industry Report Analysis 2024-2032 | BASF, Syngenta, Bayer Crop Science - published on openPR.com",
        "meta_url": {
          "hostname": "www.openpr.com",
          "netloc": "openpr.com",
          "path": "› news  › 3766044  › crop-protection-chemicals-market-detailed-industry-report",
          "scheme": "https"
        },
        "page_age": "2024-12-02T10:46:15",
        "source_name": "openpr.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/pAlDpCwJjcEf6Ypm-K1Tl8JBCNjyRa73ZfUkRYZwVXU/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9jZG4u/b3Blbi1wci5jb20v/TC9jL0xjMDIxNTQ3/NjdfZy5qcGc"
        },
        "title": "Crop Protection Chemicals Market Detailed Industry Report Analysis 2024-2032 | BASF, Syngenta, Bayer Crop Science",
        "type": "news_result",
        "url": "https://www.openpr.com/news/3766044/crop-protection-chemicals-market-detailed-industry-report"
      },
      {
        "age": "5 days ago",
        "description": "CII Visakhapatnam to organise conference on Industrial & Chemical Safety from December 12",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› news  › cities  › Visakhapatnam  › cii-visakhapatnam-to-organise-conference-on-industrial-chemical-safety-from-december-12  › article68973107.ece",
          "scheme": "https"
        },
        "page_age": "2024-12-11T12:18:13",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/llajowBpmgWaVpuUx0Kw-DZmR0pl3GHEUnH8UFCou-g/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/dGhlaGluZHUuY29t/L3RoZW1lL2ltYWdl/cy9vZy1pbWFnZS5w/bmc"
        },
        "title": "CII Visakhapatnam to organise conference on Industrial & Chemical Safety from December 12 - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/news/cities/Visakhapatnam/cii-visakhapatnam-to-organise-conference-on-industrial-chemical-safety-from-december-12/article68973107.ece"
      },
      {
        "age": "3 weeks ago",
        "description": "CII Tamil Nadu Chemvision 2024 highlights sustainability, safety, investment opportunities, and capability building in the chemical industry.",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› news  › national  › tamil-nadu  › cii-tamil-nadu-chemvision-2024-to-be-held-on-november-29  › article68923289.ece",
          "scheme": "https"
        },
        "page_age": "2024-11-28T17:55:13",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/llajowBpmgWaVpuUx0Kw-DZmR0pl3GHEUnH8UFCou-g/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/dGhlaGluZHUuY29t/L3RoZW1lL2ltYWdl/cy9vZy1pbWFnZS5w/bmc"
        },
        "title": "CII Tamil Nadu Chemvision 2024 to be held on November 29 - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/cii-tamil-nadu-chemvision-2024-to-be-held-on-november-29/article68923289.ece"
      },
      {
        "age": "1 month ago",
        "description": "Fire officials said the incident occurred when chemical sludge, which was awaiting transport to a cement factory, caught fire. Firefighters doused the flames before fire could spread to the main unit. The reactor and boilers, which are key components of the chemical industry, were not damaged ...",
        "meta_url": {
          "hostname": "timesofindia.indiatimes.com",
          "netloc": "timesofindia.indiatimes.com",
          "path": "› city  › hyderabad  › massive-fire-erupts-at-chemical-facility-near-hyderabad-no-casualties-reported  › articleshow  › 115369330.cms",
          "scheme": "https"
        },
        "page_age": "2024-11-16T19:01:00",
        "source_name": "timesofindia.indiatimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/2lwy_RjV_cNso39qFr6pfrjPykcR3cRKhHnm_Z6LzJI/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudG9paW1nLmNv/bS90aHVtYi9tc2lk/LTExNTM2OTMyNyx3/aWR0aC0xMDcwLGhl/aWdodC01ODAsaW1n/c2l6ZS01NjQ2MCxy/ZXNpemVtb2RlLTc1/LG92ZXJsYXktdG9p/X3N3LHB0LTMyLHlf/cGFkLTQwL3Bob3Rv/LmpwZw"
        },
        "title": "Massive Fire Erupts at Chemical Facility Near Hyderabad, No Casualties Reported | - Times of India",
        "type": "news_result",
        "url": "https://timesofindia.indiatimes.com/city/hyderabad/massive-fire-erupts-at-chemical-facility-near-hyderabad-no-casualties-reported/articleshow/115369330.cms"
      },
      {
        "age": "October 24, 2024",
        "description": "সম্প্রতি যে সংস্থা দেশের সেরা কোম্পানির পুরস্কার (তালিকাভুক্ত কোম্পানির মধ্যে) পেয়েছে, সেটিই সিঙ্গুরে ২২০ কোটি ...",
        "meta_url": {
          "hostname": "bangla.hindustantimes.com",
          "netloc": "bangla.hindustantimes.com",
          "path": "› pictures  › big-investment-for-singur-himadri-speciality-chemical-limited-to-invest-rs-220-crore-for-31729757880342.html",
          "scheme": "https"
        },
        "page_age": "2024-10-24T08:29:45",
        "source_name": "bangla.hindustantimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/P2qC9UIGEGMbr_jLcGcbrqITQpUIY6NaltTu8DBiEB8/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWFn/ZXMuaGluZHVzdGFu/dGltZXMuY29tL2Jh/bmdsYS9pbWcvMjAy/NC8xMC8yNC82MDB4/MzM4L0lORElBLVNU/RUVMLTBfMTcyOTc1/Nzg3MTk5NF8xNzI5/NzU4NTg1MDQ4LkpQ/Rw"
        },
        "title": "₹220 cr investment at Singur: সিঙ্গুরে ২২০ কোটি টাকার বিনিয়োগ আসছে! লগ্নি করছে দেশের সেরা হওয়া সংস্থা, কী হবে? - Big investment for Singur, Himadri Speciality Chemical limited to invest ₹220 crore for - ছবিঘর নিউজ",
        "type": "news_result",
        "url": "https://bangla.hindustantimes.com/pictures/big-investment-for-singur-himadri-speciality-chemical-limited-to-invest-rs-220-crore-for-31729757880342.html"
      },
      {
        "age": "September 16, 2024",
        "description": "Texas chemical plant explosion: Firefighters were battling a pipeline fire in suburban Houston that sparked grass fires and burned power poles on Monday",
        "meta_url": {
          "hostname": "www.hindustantimes.com",
          "netloc": "hindustantimes.com",
          "path": "› world-news  › us-news  › texas-chemical-plant-explosion-evacuations-ordered-in-la-porte-amid-roaring-pipeline-fire-101726503834727.html",
          "scheme": "https"
        },
        "page_age": "2024-09-16T16:28:49",
        "source_name": "Hindustan Times",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/faaxK__lNPrgy_h2x4S1uacJIB8EVkgmD37qsgKPHl8/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/aGluZHVzdGFudGlt/ZXMuY29tL2h0LWlt/Zy9pbWcvMjAyNC8w/OS8xNi8xNjAweDkw/MC9URVhBUy1DQVRU/TEUtLTFfMTY4MTQ1/MTc1NjI3MF8xNjgx/NDUxNzU2MjcwXzE3/MjY1MDM5MTIyNDUu/SlBH"
        },
        "title": "Texas chemical plant explosion: Evacuations ordered in La Porte amid roaring pipeline fire - Hindustan Times",
        "type": "news_result",
        "url": "https://www.hindustantimes.com/world-news/us-news/texas-chemical-plant-explosion-evacuations-ordered-in-la-porte-amid-roaring-pipeline-fire-101726503834727.html"
      },
      {
        "age": "September 13, 2024",
        "description": "Gas leak reported at chemical company in Ambernath, Thane district; fire brigade officials on scene, awaiting further details.",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› news  › national  › maharashtra  › gas-leak-at-chemical-factory-in-thanes-ambernath  › article68637090.ece",
          "scheme": "https"
        },
        "page_age": "2024-09-13T01:43:07",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/llajowBpmgWaVpuUx0Kw-DZmR0pl3GHEUnH8UFCou-g/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/dGhlaGluZHUuY29t/L3RoZW1lL2ltYWdl/cy9vZy1pbWFnZS5w/bmc"
        },
        "title": "Gas leak at chemical factory in Thane’s Ambernath - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/news/national/maharashtra/gas-leak-at-chemical-factory-in-thanes-ambernath/article68637090.ece"
      },
      {
        "age": "August 31, 2024",
        "description": "Discover the vast chemical armory of plants like garlic, used for centuries in diets and medicine for human health.",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› sci-tech  › the-chemical-treasury-in-garlic  › article68559174.ece",
          "scheme": "https"
        },
        "page_age": "2024-08-31T15:40:00",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/llajowBpmgWaVpuUx0Kw-DZmR0pl3GHEUnH8UFCou-g/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly93d3cu/dGhlaGluZHUuY29t/L3RoZW1lL2ltYWdl/cy9vZy1pbWFnZS5w/bmc"
        },
        "title": "The chemical treasury in garlic - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/sci-tech/the-chemical-treasury-in-garlic/article68559174.ece"
      },
      {
        "age": "August 26, 2024",
        "description": "And are there such more requests from the industry pending for the ministry to look at? Ajay Joshi: We will see a lot more anti-dumping duties, as well as a lot more minimum import support price initiatives that will be rendered from the Indian government to Indian chemical players.",
        "meta_url": {
          "hostname": "m.economictimes.com",
          "netloc": "m.economictimes.com",
          "path": "› markets  › expert-view  › more-anti-dumping-duties-to-support-local-indian-chemical-companies-ajay-joshi  › articleshow  › 112801519.cms",
          "scheme": "https"
        },
        "page_age": "2024-08-26T10:40:02",
        "source_name": "m.economictimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/36FKJ7dAKQRbme3CqO47lQcFO4VHz03KPSoqn-Eqxi0/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWcu/ZXRpbWcuY29tL3Ro/dW1iL21zaWQtMTEy/ODAxNTI4LHdpZHRo/LTEyMDAsaGVpZ2h0/LTYzMCxpbWdzaXpl/LTQwNTQsb3Zlcmxh/eS1ldG1hcmtldHMv/YXJ0aWNsZXNob3cu/anBn"
        },
        "title": "chemical companies: More anti-dumping duties to support local Indian chemical companies: Ajay Joshi - The Economic Times",
        "type": "news_result",
        "url": "https://m.economictimes.com/markets/expert-view/more-anti-dumping-duties-to-support-local-indian-chemical-companies-ajay-joshi/articleshow/112801519.cms"
      },
      {
        "age": "August 24, 2024",
        "description": "Producers of PFAS chemicals and semiconductors, a key part of most electronics, have formed a group that develops industry-friendly science aimed at heading off regulation as facilities release high levels of toxic waste, documents seen by the Guardian show.",
        "meta_url": {
          "hostname": "www.theguardian.com",
          "netloc": "theguardian.com",
          "path": "› environment  › article  › 2024  › aug  › 24  › pfas-toxic-waste-pollution-regulation-lobbying",
          "scheme": "https"
        },
        "page_age": "2024-08-24T13:00:33",
        "source_name": "The Guardian",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/0W30teYhY65K0E8fmkhQaOgOuJ6qSCa1DspIcofMITQ/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLmd1/aW0uY28udWsvaW1n/L21lZGlhL2QwMzc3/ODczZjBjM2VlNjcw/YzljODNhNDgzMjU2/YzQ1MjljMzZjY2Qv/MF8yMzJfNjk2MF80/MTc2L21hc3Rlci82/OTYwLmpwZz93aWR0/aD0xMjAwJmhlaWdo/dD02MzAmcXVhbGl0/eT04NSZhdXRvPWZv/cm1hdCZmaXQ9Y3Jv/cCZvdmVybGF5LWFs/aWduPWJvdHRvbSUy/Q2xlZnQmb3Zlcmxh/eS13aWR0aD0xMDBw/Jm92ZXJsYXktYmFz/ZTY0PUwybHRaeTl6/ZEdGMGFXTXZiM1ps/Y214aGVYTXZkR2N0/WkdWbVlYVnNkQzV3/Ym1jJmVuYWJsZT11/cHNjYWxlJnM9NTRl/M2VkMjAzNzNmNjJh/Njg0ZTNhYzM0NTA5/ODgxOTI"
        },
        "title": "Industry acts to head off regulation on PFAS pollution from semiconductors | PFAS | The Guardian",
        "type": "news_result",
        "url": "https://www.theguardian.com/environment/article/2024/aug/24/pfas-toxic-waste-pollution-regulation-lobbying"
      },
      {
        "age": "August 6, 2024",
        "description": "Imported chemicals, reagents, and ... chemicals and are vital to experimental research across nearly every domain of scientific research. They comprise oxidisers, corrosive acids, and compressed gas, that are used by researchers to conduct experiments and even make new products. Outside of research settings, the medical diagnostics industry is run on ...",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› news  › national  › why-was-customs-duty-hike-imposed-for-lab-chemicals-explained  › article68489881.ece",
          "scheme": "https"
        },
        "page_age": "2024-08-06T03:00:00",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/XnRTEq-045V-3-yqQmZzNL2CXz7nfE9uB3A4EvvK_ek/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly90aC1p/LnRoZ2ltLmNvbS9w/dWJsaWMvaW5jb21p/bmcvM2QycmNkL2Fy/dGljbGU2ODQ4OTg5/NC5lY2UvYWx0ZXJu/YXRlcy9MQU5EU0NB/UEVfMTIwMC9JTUdf/UE8yMl9MYWJfMl8x/X0xVQlRLVkxOLmpw/Zw"
        },
        "title": "Why was a customs duty hike imposed for lab chemicals? | Explained - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/news/national/why-was-customs-duty-hike-imposed-for-lab-chemicals-explained/article68489881.ece"
      },
      {
        "age": "July 30, 2024",
        "description": "Scientists alarmed by 150% hike in customs duty on laboratory chemicals, sparking concerns over research funding and accessibility.",
        "meta_url": {
          "hostname": "www.thehindu.com",
          "netloc": "thehindu.com",
          "path": "› sci-tech  › science  › 150-customs-duty-on-lab-chemicals-alarms-scientists  › article68465158.ece",
          "scheme": "https"
        },
        "page_age": "2024-07-30T23:18:00",
        "source_name": "The Hindu",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/efUVKzr_CvwMR3CIlcnSh_yOGKOwJkoPdM38OGSPIlg/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly90aC1p/LnRoZ2ltLmNvbS9w/dWJsaWMvaW5jb21p/bmcvNHUzdWs1L2Fy/dGljbGU2ODQ2NjE4/NS5lY2UvYWx0ZXJu/YXRlcy9MQU5EU0NB/UEVfMTIwMC9QTzE5/X0xhYl9zYW1wbGVz/LmpwZw"
        },
        "title": "150% customs duty on lab chemicals alarms scientists - The Hindu",
        "type": "news_result",
        "url": "https://www.thehindu.com/sci-tech/science/150-customs-duty-on-lab-chemicals-alarms-scientists/article68465158.ece"
      },
      {
        "age": "July 15, 2024",
        "description": "Union Budget 2024: The agrochemical sector in India is pushing for an increase in import duties to combat the influx of chemicals from China. Industry experts are advocating for tariffs to level the playing field for domestic players and address the trade deficit.",
        "meta_url": {
          "hostname": "m.economictimes.com",
          "netloc": "m.economictimes.com",
          "path": "› news  › economy  › policy  › budget-2024-agro-chemical-sector-seeks-hike-in-import-duties  › articleshow  › 111736462.cms",
          "scheme": "https"
        },
        "page_age": "2024-07-15T18:35:05",
        "source_name": "m.economictimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/D0Ec-qSM1b3xUV5kKHPGOuFehxSUBw2KwKBFAyJ6zC8/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWcu/ZXRpbWcuY29tL3Ro/dW1iL21zaWQtMTEx/NzM2NDg4LHdpZHRo/LTEyMDAsaGVpZ2h0/LTYzMCxpbWdzaXpl/LTEwMTEwNCxvdmVy/bGF5LWVjb25vbWlj/dGltZXMvcGhvdG8u/anBn"
        },
        "title": "Budget 2024: Agro-chemical sector seeks hike in import duties - The Economic Times",
        "type": "news_result",
        "url": "https://m.economictimes.com/news/economy/policy/budget-2024-agro-chemical-sector-seeks-hike-in-import-duties/articleshow/111736462.cms"
      },
      {
        "age": "June 26, 2024",
        "description": "“These stocks have either reversed from a long-term support or made a multiyear breakout retest which make them quite safe as compared to the stocks which are witnessing a breakout which can fail if the markets correct,” said InCreds VP, Gaurav Bissa, in a client note.",
        "meta_url": {
          "hostname": "m.economictimes.com",
          "netloc": "m.economictimes.com",
          "path": "› markets  › stocks  › news  › brokerage-view-chemical-stocks-ripe-for-fresh-up-cycle  › articleshow  › 111270903.cms",
          "scheme": "https"
        },
        "page_age": "2024-06-26T09:05:03",
        "source_name": "m.economictimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/GqRtEiyviXDP6MguofYwO3jl4EWYZYJl6Wyj_EaGV30/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWcu/ZXRpbWcuY29tL3Ro/dW1iL21zaWQtMTEx/MjcwODg2LHdpZHRo/LTEyMDAsaGVpZ2h0/LTYzMCxpbWdzaXpl/LTQ4NjQwLG92ZXJs/YXktZXRtYXJrZXRz/L3Bob3RvLmpwZw"
        },
        "title": "chemical stocks: Brokerage View: Chemical stocks ripe for fresh up-cycle - The Economic Times",
        "type": "news_result",
        "url": "https://m.economictimes.com/markets/stocks/news/brokerage-view-chemical-stocks-ripe-for-fresh-up-cycle/articleshow/111270903.cms"
      },
      {
        "age": "June 3, 2024",
        "description": "Regulating chemicals one-by-one has allowed the tobacco industry to skirt menthol bans by creating new additives with similar effects but unclear safety profiles",
        "meta_url": {
          "hostname": "www.scientificamerican.com",
          "netloc": "scientificamerican.com",
          "path": "› article  › how-tobacco-companies-use-chemistry-to-get-around-menthol-bans",
          "scheme": "https"
        },
        "page_age": "2024-06-03T13:00:00",
        "source_name": "Scientific American",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/72rWK2FjUyLGTVKABZyKNSK-9aPPMcc4KVbkuSR30xw/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9zdGF0/aWMuc2NpZW50aWZp/Y2FtZXJpY2FuLmNv/bS9kYW0vbS8xNGEw/NDEyODM4ZGRkMTMv/b3JpZ2luYWwvMlJF/NDBLNl9XRUIuanBn/P3c9MTIwMA"
        },
        "title": "How Tobacco Companies Use Chemistry to Get around Menthol Bans | Scientific American",
        "type": "news_result",
        "url": "https://www.scientificamerican.com/article/how-tobacco-companies-use-chemistry-to-get-around-menthol-bans/"
      },
      {
        "age": "May 30, 2024",
        "description": "The plastic industry is pitching chemical recycling as a great new hope in the battle against the plastic pollution crisis. Experts say not so fast",
        "meta_url": {
          "hostname": "www.cnn.com",
          "netloc": "cnn.com",
          "path": "› 2024  › 05  › 30  › climate  › chemical-recycling-plastic-pollution-climate  › index.html",
          "scheme": "https"
        },
        "page_age": "2024-05-30T08:00:15",
        "source_name": "CNN",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/JKOPReSeEiqJBpPyB9W_qKvTxxtYi24wM8W2UP76JII/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5jbm4uY29tL2Fw/aS92MS9pbWFnZXMv/c3RlbGxhci9wcm9k/L2dldHR5aW1hZ2Vz/LTEyNTg1MTE4NDUu/anBnP2M9MTZ4OSZx/PXdfODAwLGNfZmls/bA"
        },
        "title": "The plastics industry says chemical recycling could help banish pollution. It’s ‘an illusion,’ critics say | CNN",
        "type": "news_result",
        "url": "https://www.cnn.com/2024/05/30/climate/chemical-recycling-plastic-pollution-climate/index.html"
      },
      {
        "age": "May 25, 2024",
        "description": "India's Petroleum, Chemical, and Petrochemical Investment Regions (PCPIRs) are expected to attract investments worth USD 420 billion, reflecting the sector's robust potential. Additionally, the establishment of seven Central Institutes of Petrochemicals Engineering & Technology (CIPET) and the Institute of Pesticide Formulation Technology (IPFT) will drive skill development, ensuring a skilled workforce to support the industry...",
        "meta_url": {
          "hostname": "m.economictimes.com",
          "netloc": "m.economictimes.com",
          "path": "› industry  › indl-goods  › svs  › chem-  › -fertilisers  › indias-chemicals-market-to-hit-29-7-bn-in-2024-set-for-steady-growth-with-3-26-cagr-through-2029  › articleshow  › 110418837.cms",
          "scheme": "https"
        },
        "page_age": "2024-05-25T07:30:02",
        "source_name": "m.economictimes.com",
        "thumbnail": {
          "src": "https://you.com/proxy?url=https://imgs.news.you.com/KNb5Pm02ITThd3icECdte7bUxKtEz53cELFDWN7YRh8/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pbWcu/ZXRpbWcuY29tL3Ro/dW1iL21zaWQtMTEw/NDE4ODU2LHdpZHRo/LTEyMDAsaGVpZ2h0/LTYzMCxpbWdzaXpl/LTI0MDc0LG92ZXJs/YXktZWNvbm9taWN0/aW1lcy9hcnRpY2xl/c2hvdy5qcGc"
        },
        "title": "chemicals market: India's chemicals market to hit $29.7 bn in 2024, set for steady growth with 3.26% CAGR through 2029 - The Economic Times",
        "type": "news_result",
        "url": "https://m.economictimes.com/industry/indl-goods/svs/chem-/-fertilisers/indias-chemicals-market-to-hit-29-7-bn-in-2024-set-for-steady-growth-with-3-26-cagr-through-2029/articleshow/110418837.cms"
      }
    ],
    "type": "news"
    }
    }
    

##

​

Explore further

## [Quickstart](/docs/quickstart)## [API Reference](/api-reference)

[Search API](/api-modes/search-api)[Custom APIs](/api-modes/custom-api)

[twitter](https://twitter.com/youdotcom)[linkedin](https://www.linkedin.com/company/youdotcom)

[Powered by Mintlify](https://mintlify.com/preview-
request?utm_campaign=poweredBy&utm_medium=docs&utm_source=documentation.you.com)

On this page

  * Stay Informed with the Latest Global News
  * Use Cases
  * Explore further

[You.com API home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/dark.svg)](/)

Search or ask...

  * [Discord](https://discord.com/invite/youdotcom)
  * [Support](mailto:api@you.com)
  * [Support](mailto:api@you.com)

Search...

Navigation

API Reference

News

[Welcome](/welcome)[Quickstart](/docs/quickstart)[API Reference](/api-
reference/smart)[API Guide](/api-modes/smart-api)

##### API Reference

  * [POSTSmart API](/api-reference/smart)
  * [POSTResearch API](/api-reference/research)
  * [GETSearch](/api-reference/search)
  * [GETNews](/api-reference/news)

API Reference

# News

GET

/

news

Try it

cURL

Python

JavaScript

PHP

Go

Java

    
    
    curl --request GET \
      --url https://chat-api.you.com/news \
      --header 'X-API-Key: <api-key>'

200

    
    
    {
      "news": {
        "results": [
          {
            "url": "https://news.you.com",
            "title": "Breaking News about the World's Greatest Search Engine!",
            "description": "Search on YDC for the news",
            "type": "news",
            "age": "18 hours ago",
            "page_age": "2 days",
            "breaking": false,
            "page_fetched": "2023-10-12T23:00:00Z",
            "thumbnail": {
              "original": "https://reuters.com/news.jpg"
            },
            "meta_url": {
              "scheme": "https",
              "netloc": "reuters.com",
              "hostname": "www.reuters.com",
              "path": "› 2023  › 10  › 18  › politics  › inflation  › index.html"
            }
          }
        ]
      }
    }

**Before You Get Started**

To register for usage of our News API, please reach out via email at
[api@you.com](mailto:api@you.com).

#### Authorizations

​

X-API-Key

string

header

required

#### Query Parameters

​

query

string

required

Search query used to retrieve relevant results from index

​

count

integer

Specifies the maximum number of web results to return. Range `1 ≤
num_web_results ≤ 20`.

​

offset

integer

Indicates the `offset` for pagination. The `offset` is calculated in multiples
of `num_web_results`. For example, if `num_web_results = 5` and `offset = 1`,
results 5–10 will be returned. Range `0 ≤ offset ≤ 9`.

​

country

string

Country Code, one of `['AR', 'AU', 'AT', 'BE', 'BR', 'CA', 'CL', 'DK', 'FI',
'FR', 'DE', 'HK', 'IN', 'ID', 'IT', 'JP', 'KR', 'MY', 'MX', 'NL', 'NZ', 'NO',
'CN', 'PL', 'PT', 'PH', 'RU', 'SA', 'ZA', 'ES', 'SE', 'CH', 'TW', 'TR', 'GB',
'US']`.

​

search_lang

string

Language codes, one of `['ar', 'eu', 'bn', 'bg', 'ca', 'Simplified',
'Traditional', 'hr', 'cs', 'da', 'nl', 'en', 'United', 'et', 'fi', 'fr', 'gl',
'de', 'gu', 'he', 'hi', 'hu', 'is', 'it', 'jp', 'kn', 'ko', 'lv', 'lt', 'ms',
'ml', 'mr', 'Bokmål', 'pl', 'Brazil', 'Portugal', 'pa', 'ro', 'ru', 'Cyrylic',
'sk', 'sl', 'es', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'vi']`.

​

ui_lang

string

User interface language for the response, one of `['es-AR', 'en-AU', 'de-AT',
'nl-BE', 'fr-BE', 'pt-BR', 'en-CA', 'fr-CA', 'es-CL', 'da-DK', 'fi-FI', 'fr-
FR', 'de-DE', 'SAR', 'en-IN', 'en-ID', 'it-IT', 'ja-JP', 'ko-KR', 'en-MY',
'es-MX', 'nl-NL', 'English', 'no-NO', 'of', 'pl-PL', 'the', 'ru-RU',
'English', 'es-ES', 'sv-SE', 'fr-CH', 'de-CH', 'Chinese', 'tr-TR', 'English',
'English', 'Spanish']`.

​

safesearch

string

Configures the safesearch filter for content moderation. `off` \- no filtering
applied.`moderate` \- moderate content filtering (default). `strict` \- strict
content filtering.

​

spellcheck

boolean

Determine whether the `query` requires spell-checking. default is `true`.

​

recency

enum<string>

Specify the desired recency for the requested articles.

Available options:

`day`,

`week`,

`month`,

`year`

#### Response

200 - application/json

A JSON object containing array of news results

​

news

object

Show child attributes

​

news.results

object[]

Show child attributes

​

news.results.url

string

​

news.results.title

string

​

news.results.description

string

​

news.results.type

string

​

news.results.age

string

​

news.results.page_age

string

​

news.results.breaking

boolean

​

news.results.page_fetched

string

​

news.results.thumbnail

object

Show child attributes

​

news.results.thumbnail.original

string

​

news.results.meta_url

object

Show child attributes

​

news.results.meta_url.scheme

string

​

news.results.meta_url.netloc

string

​

news.results.meta_url.hostname

string

​

news.results.meta_url.path

string

[Search](/api-reference/search)

[twitter](https://twitter.com/youdotcom)[linkedin](https://www.linkedin.com/company/youdotcom)

[Powered by Mintlify](https://mintlify.com/preview-
request?utm_campaign=poweredBy&utm_medium=docs&utm_source=documentation.you.com)

cURL

Python

JavaScript

PHP

Go

Java

    
    
    curl --request GET \
      --url https://chat-api.you.com/news \
      --header 'X-API-Key: <api-key>'

200

    
    
    {
      "news": {
        "results": [
          {
            "url": "https://news.you.com",
            "title": "Breaking News about the World's Greatest Search Engine!",
            "description": "Search on YDC for the news",
            "type": "news",
            "age": "18 hours ago",
            "page_age": "2 days",
            "breaking": false,
            "page_fetched": "2023-10-12T23:00:00Z",
            "thumbnail": {
              "original": "https://reuters.com/news.jpg"
            },
            "meta_url": {
              "scheme": "https",
              "netloc": "reuters.com",
              "hostname": "www.reuters.com",
              "path": "› 2023  › 10  › 18  › politics  › inflation  › index.html"
            }
          }
        ]
      }
    }

