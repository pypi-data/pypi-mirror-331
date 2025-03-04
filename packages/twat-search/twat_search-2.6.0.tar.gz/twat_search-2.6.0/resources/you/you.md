Loading...

[You.com API home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/dark.svg)](/)

Search or ask...

  * [Discord](https://discord.com/invite/youdotcom)
  * [Support](mailto:api@you.com)
  * [Support](mailto:api@you.com)

Search...

Navigation

Initial Setup

Quickstart

[Welcome](/welcome)[Quickstart](/docs/quickstart)[API Reference](/api-
reference/smart)[API Guide](/api-modes/smart-api)

##### Initial Setup

  * [Quickstart](/docs/quickstart)

##### More Examples

  * [Open Source Examples](/docs/opensource-examples)

Initial Setup

# Quickstart

##

​

Introduction

Welcome to the Quickstart Guide for integrating comprehensive, high-quality
answers with precise and reliable citations using our [Smart](/api-
modes/smart-api), [Research](/api-modes/research-api), [Search](/api-
modes/search-api) and [News](/api-modes/news-api) APIs. This guide will walk
you through the initial setup and provide you with sample code to perform
searches and retrieve results.

##

​

Step 1: Set Up Your API Key

**Before You Get Started**

To use the You.com Smart, Research, Search and News LLM endpoints, you can get
an API key through the self-serve portal at
[api.you.com](https://api.you.com). For support, please reach out via email at
[api@you.com](mailto:api@you.com).

Replace `X-API-Key` in the code with your actual API key:

API Key

    
    
    YOUR_API_KEY = "your_actual_api_key_here"
    

##

​

Step 2: Write the Search Function

Create a function to interact with the Research API:

  * Smart API
  * Research API
  * Search API
  * News API

Learn more about the [Smart API ](/api-modes/smart-api).

smart_api.py

    
    
    import requests
    
    def get_smart_results(query):
        headers = {"X-API-Key": YOUR_API_KEY}
        params = {"query": query, "instructions": instructions}
        return requests.get(
            "https://chat-api.you.com/smart?query={query}",
            params=params,
            headers=headers,
        ).json()
    

Use the function to search for AI snippets related to a specific topic:

  * Smart API
  * Research API
  * Search API
  * News API

smart_results.py

    
    
    get_smart_results("Who won the Nobel Prize in Physics in 2024?")
    

Answer

answer

    
    
    {
    "answer":"#### The 2024 Nobel Prize in Physics\n\n
    The 2024 Nobel Prize in Physics was awarded jointly to **John J. Hopfield**
    and **Geoffrey E. Hinton** \"for foundational discoveries and inventions that
    enable machine learning with artificial neural networks\".
    [[1]](https://www.nobelprize.org/prizes/physics/2024/summary/) [[2]](https://www.nobelprize.org/prizes/physics/2024/press-release/)\n\n      
    Hopfield and Hinton are pioneers in the field of artificial intelligence and
    machine learning. Their work in the 1980s laid the groundwork for the development of
    modern neural networks and deep learning algorithms, which are now widely used in
    various applications.
    [[3]](https://www.nobelprize.org/prizes/physics/2024/popular-information/) [[4]](https://spectrum.ieee.org/nobel-prize-in-physics)\n\n
    Specifically, Hopfield created a structure that can store and reconstruct information, while Hinton
    invented a method that can autonomously find properties in data, which are key
    innovations that make artificial intelligence work.
    [[5]](https://www.weforum.org/stories/2024/10/nobel-prize-winners-2024/)\n\n        
    The Nobel Prize committee recognized their \"foundational discoveries
    and inventions that enable machine learning with artificial neural networks\",
    highlighting how their work has been instrumental in the rapid progress of AI and machine
    learning in recent years.
    [[1]](https://www.nobelprize.org/prizes/physics/2024/summary/) [[2]](https://www.nobelprize.org/prizes/physics/2024/press-release/)"     
    
    "search_results":[
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/summary/",
    "name":"The Nobel Prize in Physics 2024 - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/press-release/",
    "name":"Press release: The Nobel Prize in Physics 2024 - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/",
    "name":"Nobel Prize in Physics",
    "snippet":"The Nobel Prize medal. ... A slide rule that physics laureate Toshihide Maskawa used as a high school student.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/all-nobel-prizes-2024/",
    "name":"All Nobel Prizes 2024 - NobelPrize.org",
    "snippet":"Ill. Niklas Elmehed © Nobel Prize Outreach · This year’s laureates used tools from physics to construct methods that helped lay the foundation for today’s powerful machine learning. John Hopfield created a structure that can store and reconstruct information.",
    "metadata":"None"
    },
    {
    "url":"https://www.aps.org/about/news/2024/10/nobel-physics-2024-winners",
    "name":"APS congratulates 2024 Nobel Prize winners",
    "snippet":"The latest news and announcements about APS and the global physics community.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/popular-information/",
    "name":"The Nobel Prize in Physics 2024 - Popular science background - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://time.com/7065011/nobel-prize-2024-winners/",
    "name":"These Are the Winners of the 2024 Nobel Prizes",
    "snippet":"Victor Ambros and Gary Ruvkun were on Monday awarded the 2024 Nobel Prize in Physiology or Medicine for their discovery of microRNAs, a class of small molecules essential for gene regulation. Their research has uncovered how these microRNAs influence cellular behavior and contribute to various ...",
    "metadata":"None"
    },
    {
    "url":"https://www.reuters.com/science/hopfield-hinton-win-2024-nobel-prize-physics-2024-10-08/",
    "name":"Nobel physics prize 2024 won by AI pioneers John Hopfield and Geoffrey Hinton | Reuters",
    "snippet":"[1/6]John J Hopfield and Geoffrey E Hinton are awarded this year's Nobel Prize in Physics, announced at a press conference at the Royal Swedish Academy of Sciences in Stockholm, Sweden October 8, 2024.",
    "metadata":"None"
    },
    {
    "url":"https://www.weforum.org/stories/2024/10/nobel-prize-winners-2024/",
    "name":"These are the Nobel Prize winners of 2024 | World Economic Forum",
    "snippet":"AI pioneers John Hopfield and Geoffrey Hinton were both awarded the Physics prize, for using tools to develop methods that are the foundation of today’s machine learning. Widely credited as \"a godfather of AI\", British-Canadian Hinton invented a method that can autonomously find properties ...",
    "metadata":"None"
    },
    {
    "url":"https://new.nsf.gov/news/nsf-congratulates-laureates-2024-nobel-prize-physics",
    "name":"NSF congratulates laureates of the 2024 Nobel Prize in physics | NSF - National Science Foundation",
    "snippet":"Two researchers used fundamental knowledge of the physical properties of materials to create key innovations that make artificial intelligence work ... The U.S. National Science Foundation congratulates John J. Hopfield and Geoffrey E. Hinton for their Nobel Prize in physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-physics/",
    "name":"All Nobel Prizes in Physics - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics has been awarded 118 times to 227 Nobel Prize laureates between 1901 and 2024. John Bardeen is the only laureate who has been awarded the Nobel Prize in Physics twice, in 1956 and 1972. This means that a total of 226 individuals have received the Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics",
    "name":"List of Nobel laureates in Physics - Wikipedia",
    "snippet":"The Nobel Prize in Physics has ... as of 2024. The first prize in physics was awarded in 1901 to Wilhelm Conrad Röntgen, of Germany, who received 150,782 SEK. John Bardeen is the only laureate to win the prize twice—in 1956 and 1972. William Lawrence Bragg was the youngest Nobel laureate in physics; he won the prize ...",
    "metadata":"None"
    },
    {
    "url":"https://www.reddit.com/r/math/comments/1fyzz6t/the_nobel_prize_in_physics_2024_was_awarded_to/",
    "name":"r/math on Reddit: The Nobel Prize in Physics 2024 was awarded to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "snippet":"I think the Boltzmann machine is a really beautiful model, even from the mathematical point of view. I’m still a little bit shocked when I learned that the Nobel Prize in Physics 2024 goes to ML/DL, as much as I also like (theoretical) computer science.",
    "metadata":"None"
    },
    {
    "url":"https://spectrum.ieee.org/nobel-prize-in-physics",
    "name":"Why the Nobel Prize in Physics Went to AI Research",
    "snippet":"The Nobel Prize Committee for Physics caught the academic community off-guard by handing the 2024 award to John J. Hopfield and Geoffrey E. Hinton for their foundational work in neural networks. The pair won the prize for their seminal papers, both published in the 1980s, that described rudimentary ...",
    "metadata":"None"
    },
    {
    "url":"https://www.nytimes.com/2024/10/08/science/nobel-prize-physics.html",
    "name":"Nobel Physics Prize Awarded for Pioneering A.I. Research by 2 Scientists - The New York Times",
    "snippet":"With work on machine learning that uses artificial neural networks, John J. Hopfield and Geoffrey E. Hinton “showed a completely new way for us to use computers,” the committee said.",
    "metadata":"None"
    },
    {
    "url":"https://www.reuters.com/world/nobel-prize-2024-live-physics-award-be-announced-2024-10-08/",
    "name":"Nobel Physics Prize 2024: Winners are machine learning pioneers Hopfield and Hinton - as it happened | Reuters",
    "snippet":"The award-giving body said the pair used tools from physics to develop methods \"that are the foundation of today\\'s powerful machine learning.\"",
    "metadata":"None"
    },
    {
    "url":"https://finshots.in/archive/whats-up-with-ai-and-the-2024-physics-nobel-prize/",
    "name":"What's up with AI and the 2024 Physics Nobel Prize?",
    "snippet":"An explainer of why two pioneers of AI, John Hopfield and Geoffrey Hinton, were awarded the 2024 Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.pbs.org/newshour/science/watch-live-the-winner-of-the-2024-nobel-prize-in-physics-is",
    "name":"WATCH: AI pioneers John Hopfield and Geoffrey Hinton win 2024 Nobel Prize in physics | PBS News",
    "snippet":"Hinton, who is known as the Godfather of artificial intelligence, is a citizen of Canada and Britain who works at the University of Toronto and Hopfield is an American working at Princeton.",
    "metadata":"None"
    },
    {
    "url":"https://en.wikipedia.org/wiki/Nobel_Prize_in_Physics",
    "name":"Nobel Prize in Physics - Wikipedia",
    "snippet":"The first Nobel Prize in Physics was awarded to German physicist Wilhelm Röntgen in recognition of the extraordinary services he rendered by the discovery of X-rays. This award is administered by the Nobel Foundation and is widely regarded as the most prestigious award that a scientist can receive in physics. It is presented in Stockholm at an annual ceremony on the 10th of December, the anniversary of Nobel's death. As of 2024...",
    "metadata":"None"
    },
    {
    "url":"https://www.jagranjosh.com/general-knowledge/list-of-2024-nobel-prize-winners-in-all-categories-1728376617-1",
    "name":"Nobel Prize 2024 Winners List: Recipient Name, Achievement from All Categories",
    "snippet":"Discover the complete list of Nobel Prize 2024 winners. Stay updated on the latest achievements and contributions recognized by the Nobel Committee this year.",
    "metadata":"None"
    },
    {
    "url":"https://www.artsci.utoronto.ca/news/geoffrey-hinton-wins-2024-nobel-prize-physics",
    "name":"Geoffrey Hinton wins 2024 Nobel Prize in Physics | Faculty of Arts & Science",
    "snippet":"Geoffrey Hinton, a University Professor Emeritus of the Department of Computer Science at the University of Toronto, has been awarded the 2024 Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.ap.org/news-highlights/spotlights/2024/pioneers-in-artificial-intelligence-win-the-nobel-prize-in-physics/",
    "name":"Pioneers in artificial intelligence win the Nobel Prize in physics | The Associated Press",
    "snippet":"This photo combo shows the 2024 Nobel Prize winners in Physics, professor John Hopfield, left, of Princeton University, and professor Geoffrey Hinton, of the University of Toronto, Tuesday, Oct. 8, 2024. (Princeton University via AP and Noah Berger/AP Photo) STOCKHOLM (AP) — Two pioneers of artificial intelligence — John Hopfield and Geoffrey Hinton — won ...",
    "metadata":"None"
    },
    {
    "url":"https://twitter.com/NobelPrize",
    "name":"The Nobel Prize (@NobelPrize) · X",
    "snippet":"The latest tweets from The Nobel Prize (@NobelPrize)",
    "metadata":"None"
    },
    {
    "url":"https://www.aljazeera.com/news/2024/10/8/john-hopfield-and-geoffrey-hinton-win-nobel-prize-in-physics-2024",
    "name":"AI scientists John Hopfield, Geoffrey Hinton win 2024 physics Nobel Prize | Science and Technology News | Al Jazeera",
    "snippet":"John Hopfield and Geoffrey Hinton have won the Nobel Prize in physics 2024 for their pioneering work in the field of machine learning.",
    "metadata":"None"
    }
    ]
    }
    
    
    

##

​

Explore our APIs

Unlock new possibilities with our suite of advanced APIs tailored to meet your
needs and explore more use cases.

## [Smart API](/api-modes/smart-api)## [Research API](/api-modes/research-
api)## [News API](/api-modes/news-api)## [Search API](/api-modes/search-api)

[Open Source Examples](/docs/opensource-examples)

[twitter](https://twitter.com/youdotcom)[linkedin](https://www.linkedin.com/company/youdotcom)

[Powered by Mintlify](https://mintlify.com/preview-
request?utm_campaign=poweredBy&utm_medium=docs&utm_source=documentation.you.com)

On this page

  * Introduction
  * Step 1: Set Up Your API Key
  * Step 2: Write the Search Function
  * Explore our APIs

[You.com API home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/light.svg)![dark logo](https://mintlify.s3.us-
west-1.amazonaws.com/you/logo/dark.svg)](/)

Search or ask...

  * [Discord](https://discord.com/invite/youdotcom)
  * [Support](mailto:api@you.com)
  * [Support](mailto:api@you.com)

Search...

Navigation

Initial Setup

Quickstart

[Welcome](/welcome)[Quickstart](/docs/quickstart)[API Reference](/api-
reference/smart)[API Guide](/api-modes/smart-api)

##### Initial Setup

  * [Quickstart](/docs/quickstart)

##### More Examples

  * [Open Source Examples](/docs/opensource-examples)

Initial Setup

# Quickstart

##

​

Introduction

Welcome to the Quickstart Guide for integrating comprehensive, high-quality
answers with precise and reliable citations using our [Smart](/api-
modes/smart-api), [Research](/api-modes/research-api), [Search](/api-
modes/search-api) and [News](/api-modes/news-api) APIs. This guide will walk
you through the initial setup and provide you with sample code to perform
searches and retrieve results.

##

​

Step 1: Set Up Your API Key

**Before You Get Started**

To use the You.com Smart, Research, Search and News LLM endpoints, you can get
an API key through the self-serve portal at
[api.you.com](https://api.you.com). For support, please reach out via email at
[api@you.com](mailto:api@you.com).

Replace `X-API-Key` in the code with your actual API key:

API Key

    
    
    YOUR_API_KEY = "your_actual_api_key_here"
    

##

​

Step 2: Write the Search Function

Create a function to interact with the Research API:

  * Smart API
  * Research API
  * Search API
  * News API

Learn more about the [Smart API ](/api-modes/smart-api).

smart_api.py

    
    
    import requests
    
    def get_smart_results(query):
        headers = {"X-API-Key": YOUR_API_KEY}
        params = {"query": query, "instructions": instructions}
        return requests.get(
            "https://chat-api.you.com/smart?query={query}",
            params=params,
            headers=headers,
        ).json()
    

Use the function to search for AI snippets related to a specific topic:

  * Smart API
  * Research API
  * Search API
  * News API

smart_results.py

    
    
    get_smart_results("Who won the Nobel Prize in Physics in 2024?")
    

Answer

answer

    
    
    {
    "answer":"#### The 2024 Nobel Prize in Physics\n\n
    The 2024 Nobel Prize in Physics was awarded jointly to **John J. Hopfield**
    and **Geoffrey E. Hinton** \"for foundational discoveries and inventions that
    enable machine learning with artificial neural networks\".
    [[1]](https://www.nobelprize.org/prizes/physics/2024/summary/) [[2]](https://www.nobelprize.org/prizes/physics/2024/press-release/)\n\n      
    Hopfield and Hinton are pioneers in the field of artificial intelligence and
    machine learning. Their work in the 1980s laid the groundwork for the development of
    modern neural networks and deep learning algorithms, which are now widely used in
    various applications.
    [[3]](https://www.nobelprize.org/prizes/physics/2024/popular-information/) [[4]](https://spectrum.ieee.org/nobel-prize-in-physics)\n\n
    Specifically, Hopfield created a structure that can store and reconstruct information, while Hinton
    invented a method that can autonomously find properties in data, which are key
    innovations that make artificial intelligence work.
    [[5]](https://www.weforum.org/stories/2024/10/nobel-prize-winners-2024/)\n\n        
    The Nobel Prize committee recognized their \"foundational discoveries
    and inventions that enable machine learning with artificial neural networks\",
    highlighting how their work has been instrumental in the rapid progress of AI and machine
    learning in recent years.
    [[1]](https://www.nobelprize.org/prizes/physics/2024/summary/) [[2]](https://www.nobelprize.org/prizes/physics/2024/press-release/)"     
    
    "search_results":[
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/summary/",
    "name":"The Nobel Prize in Physics 2024 - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/press-release/",
    "name":"Press release: The Nobel Prize in Physics 2024 - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/",
    "name":"Nobel Prize in Physics",
    "snippet":"The Nobel Prize medal. ... A slide rule that physics laureate Toshihide Maskawa used as a high school student.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/all-nobel-prizes-2024/",
    "name":"All Nobel Prizes 2024 - NobelPrize.org",
    "snippet":"Ill. Niklas Elmehed © Nobel Prize Outreach · This year’s laureates used tools from physics to construct methods that helped lay the foundation for today’s powerful machine learning. John Hopfield created a structure that can store and reconstruct information.",
    "metadata":"None"
    },
    {
    "url":"https://www.aps.org/about/news/2024/10/nobel-physics-2024-winners",
    "name":"APS congratulates 2024 Nobel Prize winners",
    "snippet":"The latest news and announcements about APS and the global physics community.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/physics/2024/popular-information/",
    "name":"The Nobel Prize in Physics 2024 - Popular science background - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics 2024 was awarded jointly to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "metadata":"None"
    },
    {
    "url":"https://time.com/7065011/nobel-prize-2024-winners/",
    "name":"These Are the Winners of the 2024 Nobel Prizes",
    "snippet":"Victor Ambros and Gary Ruvkun were on Monday awarded the 2024 Nobel Prize in Physiology or Medicine for their discovery of microRNAs, a class of small molecules essential for gene regulation. Their research has uncovered how these microRNAs influence cellular behavior and contribute to various ...",
    "metadata":"None"
    },
    {
    "url":"https://www.reuters.com/science/hopfield-hinton-win-2024-nobel-prize-physics-2024-10-08/",
    "name":"Nobel physics prize 2024 won by AI pioneers John Hopfield and Geoffrey Hinton | Reuters",
    "snippet":"[1/6]John J Hopfield and Geoffrey E Hinton are awarded this year's Nobel Prize in Physics, announced at a press conference at the Royal Swedish Academy of Sciences in Stockholm, Sweden October 8, 2024.",
    "metadata":"None"
    },
    {
    "url":"https://www.weforum.org/stories/2024/10/nobel-prize-winners-2024/",
    "name":"These are the Nobel Prize winners of 2024 | World Economic Forum",
    "snippet":"AI pioneers John Hopfield and Geoffrey Hinton were both awarded the Physics prize, for using tools to develop methods that are the foundation of today’s machine learning. Widely credited as \"a godfather of AI\", British-Canadian Hinton invented a method that can autonomously find properties ...",
    "metadata":"None"
    },
    {
    "url":"https://new.nsf.gov/news/nsf-congratulates-laureates-2024-nobel-prize-physics",
    "name":"NSF congratulates laureates of the 2024 Nobel Prize in physics | NSF - National Science Foundation",
    "snippet":"Two researchers used fundamental knowledge of the physical properties of materials to create key innovations that make artificial intelligence work ... The U.S. National Science Foundation congratulates John J. Hopfield and Geoffrey E. Hinton for their Nobel Prize in physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-physics/",
    "name":"All Nobel Prizes in Physics - NobelPrize.org",
    "snippet":"The Nobel Prize in Physics has been awarded 118 times to 227 Nobel Prize laureates between 1901 and 2024. John Bardeen is the only laureate who has been awarded the Nobel Prize in Physics twice, in 1956 and 1972. This means that a total of 226 individuals have received the Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics",
    "name":"List of Nobel laureates in Physics - Wikipedia",
    "snippet":"The Nobel Prize in Physics has ... as of 2024. The first prize in physics was awarded in 1901 to Wilhelm Conrad Röntgen, of Germany, who received 150,782 SEK. John Bardeen is the only laureate to win the prize twice—in 1956 and 1972. William Lawrence Bragg was the youngest Nobel laureate in physics; he won the prize ...",
    "metadata":"None"
    },
    {
    "url":"https://www.reddit.com/r/math/comments/1fyzz6t/the_nobel_prize_in_physics_2024_was_awarded_to/",
    "name":"r/math on Reddit: The Nobel Prize in Physics 2024 was awarded to John J. Hopfield and Geoffrey E. Hinton \"for foundational discoveries and inventions that enable machine learning with artificial neural networks\"",
    "snippet":"I think the Boltzmann machine is a really beautiful model, even from the mathematical point of view. I’m still a little bit shocked when I learned that the Nobel Prize in Physics 2024 goes to ML/DL, as much as I also like (theoretical) computer science.",
    "metadata":"None"
    },
    {
    "url":"https://spectrum.ieee.org/nobel-prize-in-physics",
    "name":"Why the Nobel Prize in Physics Went to AI Research",
    "snippet":"The Nobel Prize Committee for Physics caught the academic community off-guard by handing the 2024 award to John J. Hopfield and Geoffrey E. Hinton for their foundational work in neural networks. The pair won the prize for their seminal papers, both published in the 1980s, that described rudimentary ...",
    "metadata":"None"
    },
    {
    "url":"https://www.nytimes.com/2024/10/08/science/nobel-prize-physics.html",
    "name":"Nobel Physics Prize Awarded for Pioneering A.I. Research by 2 Scientists - The New York Times",
    "snippet":"With work on machine learning that uses artificial neural networks, John J. Hopfield and Geoffrey E. Hinton “showed a completely new way for us to use computers,” the committee said.",
    "metadata":"None"
    },
    {
    "url":"https://www.reuters.com/world/nobel-prize-2024-live-physics-award-be-announced-2024-10-08/",
    "name":"Nobel Physics Prize 2024: Winners are machine learning pioneers Hopfield and Hinton - as it happened | Reuters",
    "snippet":"The award-giving body said the pair used tools from physics to develop methods \"that are the foundation of today\\'s powerful machine learning.\"",
    "metadata":"None"
    },
    {
    "url":"https://finshots.in/archive/whats-up-with-ai-and-the-2024-physics-nobel-prize/",
    "name":"What's up with AI and the 2024 Physics Nobel Prize?",
    "snippet":"An explainer of why two pioneers of AI, John Hopfield and Geoffrey Hinton, were awarded the 2024 Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.pbs.org/newshour/science/watch-live-the-winner-of-the-2024-nobel-prize-in-physics-is",
    "name":"WATCH: AI pioneers John Hopfield and Geoffrey Hinton win 2024 Nobel Prize in physics | PBS News",
    "snippet":"Hinton, who is known as the Godfather of artificial intelligence, is a citizen of Canada and Britain who works at the University of Toronto and Hopfield is an American working at Princeton.",
    "metadata":"None"
    },
    {
    "url":"https://en.wikipedia.org/wiki/Nobel_Prize_in_Physics",
    "name":"Nobel Prize in Physics - Wikipedia",
    "snippet":"The first Nobel Prize in Physics was awarded to German physicist Wilhelm Röntgen in recognition of the extraordinary services he rendered by the discovery of X-rays. This award is administered by the Nobel Foundation and is widely regarded as the most prestigious award that a scientist can receive in physics. It is presented in Stockholm at an annual ceremony on the 10th of December, the anniversary of Nobel's death. As of 2024...",
    "metadata":"None"
    },
    {
    "url":"https://www.jagranjosh.com/general-knowledge/list-of-2024-nobel-prize-winners-in-all-categories-1728376617-1",
    "name":"Nobel Prize 2024 Winners List: Recipient Name, Achievement from All Categories",
    "snippet":"Discover the complete list of Nobel Prize 2024 winners. Stay updated on the latest achievements and contributions recognized by the Nobel Committee this year.",
    "metadata":"None"
    },
    {
    "url":"https://www.artsci.utoronto.ca/news/geoffrey-hinton-wins-2024-nobel-prize-physics",
    "name":"Geoffrey Hinton wins 2024 Nobel Prize in Physics | Faculty of Arts & Science",
    "snippet":"Geoffrey Hinton, a University Professor Emeritus of the Department of Computer Science at the University of Toronto, has been awarded the 2024 Nobel Prize in Physics.",
    "metadata":"None"
    },
    {
    "url":"https://www.ap.org/news-highlights/spotlights/2024/pioneers-in-artificial-intelligence-win-the-nobel-prize-in-physics/",
    "name":"Pioneers in artificial intelligence win the Nobel Prize in physics | The Associated Press",
    "snippet":"This photo combo shows the 2024 Nobel Prize winners in Physics, professor John Hopfield, left, of Princeton University, and professor Geoffrey Hinton, of the University of Toronto, Tuesday, Oct. 8, 2024. (Princeton University via AP and Noah Berger/AP Photo) STOCKHOLM (AP) — Two pioneers of artificial intelligence — John Hopfield and Geoffrey Hinton — won ...",
    "metadata":"None"
    },
    {
    "url":"https://twitter.com/NobelPrize",
    "name":"The Nobel Prize (@NobelPrize) · X",
    "snippet":"The latest tweets from The Nobel Prize (@NobelPrize)",
    "metadata":"None"
    },
    {
    "url":"https://www.aljazeera.com/news/2024/10/8/john-hopfield-and-geoffrey-hinton-win-nobel-prize-in-physics-2024",
    "name":"AI scientists John Hopfield, Geoffrey Hinton win 2024 physics Nobel Prize | Science and Technology News | Al Jazeera",
    "snippet":"John Hopfield and Geoffrey Hinton have won the Nobel Prize in physics 2024 for their pioneering work in the field of machine learning.",
    "metadata":"None"
    }
    ]
    }
    
    
    

##

​

Explore our APIs

Unlock new possibilities with our suite of advanced APIs tailored to meet your
needs and explore more use cases.

## [Smart API](/api-modes/smart-api)## [Research API](/api-modes/research-
api)## [News API](/api-modes/news-api)## [Search API](/api-modes/search-api)

[Open Source Examples](/docs/opensource-examples)

[twitter](https://twitter.com/youdotcom)[linkedin](https://www.linkedin.com/company/youdotcom)

[Powered by Mintlify](https://mintlify.com/preview-
request?utm_campaign=poweredBy&utm_medium=docs&utm_source=documentation.you.com)

On this page

  * Introduction
  * Step 1: Set Up Your API Key
  * Step 2: Write the Search Function
  * Explore our APIs

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

Search API

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

# Search API

##

​

Accurate and Real-time Web Data

When trying to build applications that rely on integrating real-time web data,
solutions are very limited. LLMs are generally unable to extract and deliver
only snippets from sources without adding additional AI-generated content.

Our **Search API** provides you with direct snippets and URLs to stay
informed, ensuring an accurate and up-to-date understanding of the world.

## Access to Trusted Data

Our API integrates live web data, providing results from trusted sources
complete with URLs for verification.

## Uniquely Long Snippets

Ensure your responses are trustworthy and contain the information you need.

##

​

Use Cases

## Information from Trusted Sources

  

Scientific Articles

query.py

    
    
    import requests
    
    url = "https://api.ydc-index.io/search"
    
    query = {"query":"Search for Scientific Research Articles on Nanomotors for Cleaning Polluted Water"}
    
    headers = {"X-API-Key": "YOUR_API_KEY"}
    
    response = requests.request("GET", url, headers=headers, params=query)
    
    print(response.text)
    

Response

    
    
    {
    "hits": [
      {
        "description": "Self-propelled nanomotors hold considerable promise for developing innovative environmental applications.Self-propelled nanomotors hold considerable promise for developing innovative environmental applications. This review highlights the recent progress ...",
        "snippets": [
          "In addition, those nanoparticles cannot transport ions and pollutants from one place to another. Catalytically powered micro- and nanomotors have attracted a lot of attention over the last few years in multidisciplinary fields of chemistry and physics.5 Since the pioneering works a decade ago, synthetic nanomotors demonstrated the ability to efficiently convert chemical energy into motion like nature uses biochemistry to power biological motors.6,7 Fundamental research is being conducted in this field and a number of interesting applications are opening up in several different fields, such as",
          "The surface modification of some types of nanomotors allows them to capture oil from contaminated waters. Research by Pumera and co-workers described a sodium dodecyl sulfate (SDS)-loaded polysulfone (PSf) capsule that was used to shepherd several oil droplets and to merge them, cleaning the surface of the water.36 The driving force of self-propulsion is based in the Marangoni effect.",
          "These “self-powered remediation systems” could be seen as a new generation of “smart devices” for cleaning water in small pipes or cavities difficult to reach with traditional methods. With constant improvement and considering the key challenges, we expect that artificial nanomachines could play an important role in environmental applications in the near future. Pollution of water by contaminants and chemical threats is a prevalent topic in scientific, economic, political and, consequently, in the public media.",
          "Researchers and engineers are devoting considerable effort to produce more efficient technological solutions for cleaning environmental pollutants."
        ],
        "title": "Catalytic nanomotors for environmental monitoring and water remediation - PMC",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4080807/"
      },
      {
        "description": "The most critical challenge of the twenty-first century is to provide sufficient clean, cheap water for all. This is made worse by population increase…",
        "snippets": [
          "The most critical challenge of the twenty-first century is to provide sufficient clean, cheap water for all. This is made worse by population increase, climate change, and declining water quality. Technology innovation, such as nanotechnology, is essential for enabling integrated water management to increase treatment effectiveness and expand water supplies using unconventional water sources.",
          "Nanotechnology can improve access to clean, safe drinking water by providing innovative nanomaterials for treating surface water, groundwater, and wastewater contaminated by hazardous metal ions, inorganic and organic solutes, and microorganisms. As a result, the development of nanotechnology provided ground-breaking solutions to issues in engineering, physics, chemistry, and others.",
          "Considering the essential need to examine and handle the developing hazardous wastes with lower costs, less energy, and more efficiency, this review shines a light on the current advancements in nanotechnology. Numerous industries, such as scientific research, the medical field, and the food industry, have paid close attention to the expanding significance of nanotechnology and the unique qualities of nanobubbles."
        ],
        "title": "Smart and innovative nanotechnology applications for water purification - ScienceDirect",
        "url": "https://www.sciencedirect.com/science/article/pii/S2773207X23000271"
      },
      {
        "description": "We describe the use of catalytically self-propelled microjets (dubbed micromotors) for degrading organic pollutants in water via the Fenton oxidation process. The tubular micromotors are composed of rolled-up functional nanomembranes consisting of Fe/Pt ...",
        "snippets": [
          "Great efforts have been made to efficiently propel and accurately control micro- and nanomotors by different mechanisms.29−37 Most self-propelled systems are based on the conversion of chemical energy into mechanical motion.38 Nonetheless, there are also other ways to produce self-motion at the micro- and nanoscale, for instance electromagnetic fields,22,39,40 local electrical fields,41 thermal gradients,42,43 photoinduced motion,44−46 or the Marangoni effect.28 This variety of propulsion mechanisms gave rise to a rich diversity of designs of nanomotors such as nanorods,47,48 spherical particles,34,49 microhelices,22,39,40 polymeric capsules,28,50 and tubular microjets.51−53",
          "Paxton W. F.; Kistler K. C.; Olmeda C. C.; Sen A.; St Angelo S. K.; Cao Y. Y.; Mallouk T. E.; Lammert P. E.; Crespi V. H. Catalytic Nanomotors: Autonomous Movement of Striped Nanorods. J. Am. Chem. Soc. 2004, 126, 13424–13431.",
          "Self-propelled microjets have been fabricated by roll-up nanotechnology of thin films51,52 and later produced in porous templates combined with electrodeposition methods.53 However, in the latter case, parameters such as shape, length, and diameter are limited by the commercially available templates, reducing the versatility in the design of those nanomotors.",
          "Differently, roll-up nanotechnology of functional nanomembranes allows a reproducible mass production method54 of micro/nanomotors with custom-made dimensions, flexible in material composition and design."
        ],
        "title": "Self-Propelled Micromotors for Cleaning Polluted Water - PMC",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3872448/"
      },
      {
        "description": "Nano- and micromotors are machines designed to self-propel and—in the process of propelling themselves—perform specialized tasks like cleaning polluted waters. These motors offer distinct advantages over conventionally static decontamination methods, owing to their ability to move around ...",
        "snippets": [
          "Nano- and micromotors are machines designed to self-propel and—in the process of propelling themselves—perform specialized tasks like cleaning polluted waters. These motors offer distinct advantages over conventionally static decontamination methods, owing to their ability to move around and self-mix—which h Recent Review Articles",
          "In the last decade, considerable research efforts have been expended on exploring various mechanisms by which these motors can self-propel and remove pollutants, proving that the removal of oil droplets, heavy metals, and organic compounds using these synthetic motors is possible.",
          "A fundamental understanding of these removal mechanisms, with their attendant advantages and disadvantages, can help researchers fine-tune motor design in the future so that technical issues can be resolved before they are scaled-up for a wide variety of environmental applications."
        ],
        "title": "Nano- and micromotors for cleaning polluted waters: focused review on pollutant removal mechanisms - Nanoscale (RSC Publishing)",
        "url": "https://pubs.rsc.org/en/content/articlelanding/2017/nr/c7nr05494g"
      },
      {
        "description": "Sustainable nanotechnology has made substantial contributions in providing contaminant-free water to humanity. In this Review, we present the compelling need for providing access to clean water through nanotechnology-enabled solutions and the large disparities in ensuring their implementation.",
        "snippets": [
          "Topics discussed include: introduction; considerations for cellulose nanomaterial-based development for engineering applications (structures and nomenclature inconsistencies, comparisons to carbon nanotubes [CNT], cellulose nanomaterial manufg.); use of cellulose nanomaterials for water treatment technologies (nano-remediation strategies [as pollutant adsorbents, as scaffolds]); cellulose nanomaterials for water purifn.",
          "A review is given. Arsenic groundwater pollution has been reported for the Red River delta of Northern Vietnam and the Mekong delta of Southern Vietnam and Cambodia. Although the health of ∼10 million people is at risk from the drinking tube well water, little information is available on the health effects of As exposure in the residents of these regions.",
          "The countrywide survey on regional distribution of As pollution has not been conducted in these countries. As far as we know, symptoms of chronic As exposure have not yet been reported, probably due to the relative short-term usage of the tube wells in the regions.",
          "However, oxidative DNA damage has been obsd. in the residents of Cambodia and so further continuous usage of the tube well might cause severe damage to the health of the residents. We review literature concerning As pollution of groundwater and its health effects on residents of Vietnam and Cambodia."
        ],
        "title": "Clean Water through Nanotechnology: Needs, Gaps, and Fulfillment | ACS Nano",
        "url": "https://pubs.acs.org/doi/10.1021/acsnano.9b01730"
      },
      {
        "description": "Surface water is extremely susceptible to pollution stemming from human activities, such as the expansion of urban and suburban areas, industries, cit…",
        "snippets": [
          "In fact, sources of surface water have become the most common discharge sites for wastewater, which may contain microorganisms, pharmaceutical waste, heavy metals, and harmful pollutants. As a reference standard for clean water, the water quality standards and index of Malaysia were used.",
          "This prompts the use of nanotechnology applications to control surface water pollution and quality, as surface water is the main source of water consumption for humans, animals, and plants. This paper reviewed the application of nanotechnology for the detection and treatment of surface water pollution to ensure the sustainability of a green environment.",
          "Nanotechnologies for the detection and treatment of surface water pollution."
        ],
        "title": "A review of nanotechnological applications to detect and control surface water pollution - ScienceDirect",
        "url": "https://www.sciencedirect.com/science/article/pii/S2352186421006805"
      },
      {
        "description": "PDF | Nano- and micromotors are machines designed to self-propel and—in the process of propelling themselves—perform specialized tasks like cleaning... | Find, read and cite all the research you need on ResearchGate",
        "snippets": [
          "While offering autonomous propulsion, conventional micro-/nanomachines usually rely on the decomposition of external chemical fuels (e.g., H2 O2 ), which greatly hinders their applications in biologically relevant media. Recent developments have resulted in various micro-/nanomotors that can be powered by biocompatible fuels.",
          "Here, recent developments on fuel-free micro-/nanomotors (powered by various external stimuli such as light, magnetic, electric, or ultrasonic fields) are summarized, ranging from fabrication to propulsion mechanisms. The applications of these fuel-free micro-/nanomotors are also discussed, including nanopatterning, targeted drug/gene delivery, cell manipulation, and precision nanosurgery.",
          "Fuel-free synthetic micro-/nanomotors, which can move without external chemical fuels, represent another attractive solution for practical applications owing to their biocompatibility and sustainability.",
          "micromotor’s surface upon the nanomotor–oil interaction and"
        ],
        "title": "(PDF) Nano- and Micromotors for Cleaning Polluted Waters: Focused Review on Pollutant Removal Mechanisms",
        "url": "https://www.researchgate.net/publication/319642204_Nano-_and_Micromotors_for_Cleaning_Polluted_Waters_Focused_Review_on_Pollutant_Removal_Mechanisms"
      },
      {
        "description": "Important challenges in the global water situation, mainly resulting from worldwide population growth and climate change, require novel innovative water technologies in order to ensure a supply of drinking water and reduce global water pollution. Against ...",
        "snippets": [
          "The use of magnetic nanoparticles (magnetite Fe3O4) for separation of water pollutants has already been established in ground water remediation, in particular for the removal of arsenic.28 The conventionally applied “pump-and-treat” technology for groundwater treatment comprises pumping up the groundwater to the surface and further treatment, usually by activated carbon for final purification. The considerably extended operating hours and higher environmental clean-up costs can be reduced by applying in situ technologies.",
          "Even industrialized countries like the USA, providing highly innovative technologies for saving and purifying water, show the difficulty of exhausted water reservoirs due to the fact that more water is extracted than refilled. In the People’s Republic of China, 550 of the 600 largest cities suffer from a water shortage, since the biggest rivers are immensely polluted and even their use for irrigation has to be omitted, not to mention treatment for potable water.",
          "Photocatalysis is an advanced oxidation process that is employed in the field of water and wastewater treatment, in particular for oxidative elimination of micropollutants and microbial pathogens.48,49 As reported in the literature,50–52 most organic pollutants can be degraded by heterogeneous photocatalysis.",
          "Solids that are used to adsorb gases or dissolved substances are called adsorbents, and the adsorbed molecules are usually referred to collectively as the adsorbate.4 Due to their high specific surface area, nanoadsorbents show a considerably higher rate of adsorption for organic compounds compared with granular or powdered activated carbon. They have great potential for novel, more efficient, and faster decontamination processes aimed at removal of organic and inorganic pollutants like heavy metals and micropollutants."
        ],
        "title": "Innovations in nanotechnology for water treatment - PMC",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4294021/"
      },
      {
        "description": "Nowadays, global water scarcity is becoming a pressing issue, and the discharge of various pollutants leads to the biological pollution of water bodies, which further leads to the poisoning of living organisms. Consequently, traditional water treatment methods are proving inadequate in addressing ...",
        "snippets": [
          "Nowadays, global water scarcity is becoming a pressing issue, and the discharge of various pollutants leads to the biological pollution of water bodies, which further leads to the poisoning of living organisms. Consequently, traditional water treatment methods are proving inadequate in addressing the growing demands of various industries.",
          "Effects of radius and length on the nanomotor rotors in aqueous solution driven by the rotating electric field. J. Phys. Chem. C 123 (50), 30649–30656. doi:10.1021/acs.jpcc.9b07345 ... Fuller, R., Landrigan, P. J., Balakrishnan, K., Bathan, G., Bose-O'Reilly, S., Brauer, M., et al. (2022). Pollution and health: a progress update.",
          "In recent years, micro/nanorobots and micro/nanomotor technologies have shown great advantages such as low cost, high efficiency and environmental friendliness in environmental remediation and water purification applications, which have gained widespread attention and have great potential for development and application.",
          "Micro/nanorobots (MNRs) or micro/nanomotors (MNMs), usually refer to microscopic substances with actuation capability between 1 and 1 mm in size, which can be both organic or inorganic, even artificially edited and modified microorganisms from nature."
        ],
        "title": "Frontiers | Micro/nanorobots for remediation of water resources and aquatic life",
        "url": "https://www.frontiersin.org/articles/10.3389/fbioe.2023.1312074/full"
      },
      {
        "description": "Nano/micromotor technology is evolving as an effective method for water treatment applications in comparison to existing static mechanisms. The dynamic nature of the nano/micromotor particles enable faster mass transport and a uniform mixing ...",
        "snippets": [
          "Other applications include self-powered porous spore@Fe3O4 biohybrid micromotors20 for the removal of toxic lead ions; mesoporous CoNi@Pt nanomotors, T/Fe/Cr micromotors and Fe3O4 nanoparticles are utilized for degradation of organic pollutants26–28; SW-Fe2O3/MnO2 micromotors used for oxidation of anthraquinone dyes/chlorophenols29; and MnFe2O4/oleic acid micromotors and Mg/Ti/Ni/Au Janus micromotors for oil removal22,30.",
          "On the other hand, the fabrication process of these nanomotors is complex and for driving requires a specific wavelength light source, a costly metal catalyst (Pt, Au), and hazardous media (i.e., hydrogen peroxide). They also have weak mechanical properties, such as limited reusability as an absorbent in aqueous media.",
          "There are very few reusable nanomotors that have been reported in past years. For instance, V. Singh et al.59 employed reusable ZrNPs/graphene/Pt hybrid micromotors for the removal of organophosphate compounds; D. Vilela et al.60 reported GOx-microbot-based reusable micromotors for lead-ion decontamination (2-cycle reuse); J.",
          "The extraction and recovery of toxic pollutants were successfully performed for ten cycles. In contrast to typical nanomotors, this design could be utilized to adjust the surface property of the TM nanorobots by changing the type of functional groups (e.g., -OH, -NH2, and -COOH) according to practical needs."
        ],
        "title": "Pick up and dispose of pollutants from water via temperature-responsive micellar copolymers on magnetite nanorobots - PMC",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8888651/"
      }
    ],
    "latency": 0.6449015140533447
    }
    

##

​

Explore further

## [Quickstart](/docs/quickstart)## [API Reference](/api-reference)

[Research API](/api-modes/research-api)[News API](/api-modes/news-api)

[twitter](https://twitter.com/youdotcom)[linkedin](https://www.linkedin.com/company/youdotcom)

[Powered by Mintlify](https://mintlify.com/preview-
request?utm_campaign=poweredBy&utm_medium=docs&utm_source=documentation.you.com)

On this page

  * Accurate and Real-time Web Data
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

Search

[Welcome](/welcome)[Quickstart](/docs/quickstart)[API Reference](/api-
reference/smart)[API Guide](/api-modes/smart-api)

##### API Reference

  * [POSTSmart API](/api-reference/smart)
  * [POSTResearch API](/api-reference/research)
  * [GETSearch](/api-reference/search)
  * [GETNews](/api-reference/news)

API Reference

# Search

GET

/

search

Try it

cURL

Python

JavaScript

PHP

Go

Java

    
    
    curl --request GET \
      --url https://chat-api.you.com/search \
      --header 'X-API-Key: <api-key>'

200

    
    
    {
      "hits": [
        {
          "url": "https://you.com",
          "title": "The World's Greatest Search Engine!",
          "description": "Search on YDC",
          "favicon_url": "https://someurl.com/favicon",
          "thumbnail_url": "https://www.somethumbnailsite.com/thumbnail.jpg",
          "snippets": [
            "I'm an AI assistant that helps you get more done. What can I help you with?"
          ]
        }
      ],
      "latency": 1
    }

**Before You Get Started**

To register for usage of our Search API, please reach out via email at
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

num_web_results

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

safesearch

string

Configures the safesearch filter for content moderation. `off` \- no filtering
applied.`moderate` \- moderate content filtering (default). `strict` \- strict
content filtering.

#### Response

200 - application/json

A JSON object containing array of search hits and request latency

​

hits

object[]

Show child attributes

​

hits.url

string

The URL of the specific search result.

​

hits.title

string

The title or name of the search result.

​

hits.description

string

A brief description of the content of the search result.

​

hits.favicon_url

string

The URL of the favicon of the search result's domain.

​

hits.thumbnail_url

string

URL of the thumbnail.

​

hits.snippets

string[]

An array of text snippets from the search result, providing a preview of the
content.

​

latency

number

Indicates the time (in seconds) taken by the API to generate the response.

[Research API](/api-reference/research)[News](/api-reference/news)

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
      --url https://chat-api.you.com/search \
      --header 'X-API-Key: <api-key>'

200

    
    
    {
      "hits": [
        {
          "url": "https://you.com",
          "title": "The World's Greatest Search Engine!",
          "description": "Search on YDC",
          "favicon_url": "https://someurl.com/favicon",
          "thumbnail_url": "https://www.somethumbnailsite.com/thumbnail.jpg",
          "snippets": [
            "I'm an AI assistant that helps you get more done. What can I help you with?"
          ]
        }
      ],
      "latency": 1
    }

