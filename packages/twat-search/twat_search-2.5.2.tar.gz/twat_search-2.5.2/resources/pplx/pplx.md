[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Initial Setup

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Initial Setup

Register and make a successful API request

##

​

Registration

  * Start by visiting the [API Settings page](https://www.perplexity.ai/pplx-api)

  * Register your credit card to get started

This step will not charge your credit card. It just stores payment information
for later API usage.

##

​

Generate an API key

  * Every API call needs a valid API key

The API key is a long-lived access token that can be used until it is manually
refreshed or deleted.

Send the API key as a bearer token in the Authorization header with each API
request.

When you run out of credits, your API keys will be blocked until you add to
your credit balance. You can avoid this by configuring “Automatic Top Up”,
which refreshes your balance whenever you drop below $2.

##

​

Make your API call

  * The API is conveniently OpenAI client-compatible for easy integration with existing applications.

cURL

    
    
    curl --location 'https://api.perplexity.ai/chat/completions' \
    --header 'accept: application/json' \
    --header 'content-type: application/json' \
    --header 'Authorization: Bearer {API_KEY}' \
    --data '{
      "model": "sonar-pro ",
      "messages": [
        {
          "role": "system",
          "content": "Be precise and concise."
        },
        {
          "role": "user",
          "content": "How many stars are there in our galaxy?"
        }
      ]
    }'
    

python

    
    
    from openai import OpenAI
    
    YOUR_API_KEY = "INSERT API KEY HERE"
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {   
            "role": "user",
            "content": (
                "How many stars are in the universe?"
            ),
        },
    ]
    
    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")
    
    # chat completion without streaming
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    print(response)
    
    # chat completion with streaming
    response_stream = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
        stream=True,
    )
    for response in response_stream:
        print(response)
    

[Supported Models](/guides/model-cards)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

On this page

  * Registration
  * Generate an API key
  * Make your API call

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Supported Models

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Supported Models

Model| Context Length| Model Type  
---|---|---  
`sonar-deep-research`| 128k| Chat Completion  
`sonar-reasoning-pro`| 128k| Chat Completion  
`sonar-reasoning`| 128k| Chat Completion  
`sonar-pro`| 200k| Chat Completion  
`sonar`| 128k| Chat Completion  
`r1-1776`| 128k| Chat Completion  
  
  1. `sonar-reasoning-pro` and `sonar-pro` have a max output token limit of 8k
  2. The reasoning models output CoTs in their responses as well
  3. `r1-1776` is an offline chat model that does not use our search subsystem

[Initial Setup](/guides/getting-started)[Pricing](/guides/pricing)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Pricing

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Pricing

Model| Input Tokens (Per Million Tokens)| Reasoning Tokens (Per Million
Tokens)| Output Tokens (Per Million Tokens)| Price per 1000 searches  
---|---|---|---|---  
`sonar-deep-research`| $2| $3| $8| $5  
`sonar-reasoning-pro`| $2| -| $8| $5  
`sonar-reasoning`| $1| -| $5| $5  
`sonar-pro`| $3| -| $15| $5  
`sonar`| $1| -| $1| $5  
`r1-1776`| $2| -| $8| -  
  
`r1-1776` is an offline chat model that does not use our search subsystem

##

​

Pricing Breakdown

Detailed Pricing Breakdown for Sonar Deep Research

**Input Tokens**

  1. Input tokens are priced at $2/1M tokens

  2. Input tokens comprise of Prompt tokens (user prompt) + Citation tokens (these are processed tokens from running searches)

**Search Queries**

  1. Deep Research runs multiple searches to conduct exhaustive research

  2. Searches are priced at $5/1000 searches

  3. A request that does 30 searches will cost $0.15 in this step.

**Reasoning Tokens**

  1. Reasoning is a distinct step in Deep Research since it does extensive automated reasoning through all the material it gathers during its research phase

  2. Reasoning tokens here are a bit different than the CoTs in the answer - these are tokens that we use to reason through the research material prior to generating the outputs via the CoTs.

  3. Reasoning tokens are priced at $3/1M tokens

**Output Tokens**

  1. Output tokens (Completion tokens) are priced at $8/1M tokens

**Total Price**

Your total price per request finally is a sum of the above 4 components

Detailed Pricing Breakdown for Sonar Reasoning Pro and Sonar Pro

**Input Tokens**

  1. Input tokens are priced at $2/1M tokens and $3/1M tokens respectively

  2. Input tokens comprise of Prompt tokens (user prompt) + Citation tokens (these are processed tokens from running searches)

**Search Queries**

  1. To give detailed answers, both the Pro APIs also run multiple searches on top of the user prompt where necessary for more exhaustive information retrieval

  2. Searches are priced at $5/1000 searches

  3. A request that does 3 searches will cost $0.015 in this step

**Output Tokens**

  1. Output tokens (Completion tokens) are priced at $8/1M tokens and $15/1M tokens respectively

**Total Price**

Your total price per request finally is a sum of the above 3 components

Detailed Pricing Breakdown for Sonar Reasoning and Sonar

**Input Tokens**

  1. Input tokens are priced at $1/1M tokens for both

  2. Input tokens comprise of Prompt tokens (user prompt)

**Search Queries**

  1. Each request does 1 search priced at $5/1000 searches

**Output Tokens**

  1. Output tokens (Completion tokens) are priced at $5/1M tokens and $1/1M tokens respectively

**Total Price**

Your total price per request finally is a sum of the above 2 components

[Supported Models](/guides/model-cards)[Rate Limits and Usage
Tiers](/guides/usage-tiers)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Structured Outputs Guide

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Structured Outputs Guide

Structured outputs is currently a beta feature and only available to users in
Tier-3

##

​

Overview

We currently support two types of structured outputs: **JSON Schema** and
**Regex**. LLM responses will work to match the specified format, except for
the following cases:

  * The output exceeds `max_tokens`

Enabling the structured outputs can be done by adding a `response_format`
field in the request:

**JSON Schema**

  * `response_format: { type: "json_schema", json_schema: {"schema": object} }` .

  * The schema should be a valid JSON schema object.

**Regex** (only avilable for `sonar` right now)

  * `response_format: { type: "regex", regex: {"regex": str} }` .

  * The regex is a regular expression string.

We recommend to give the LLM some hints about the output format in the
prompts.

The first request with a new JSON Schema or Regex expects to incur delay on
the first token. Typically, it takes 10 to 30 seconds to prepare the new
schema. Once the schema has been prepared, the subsequent requests will not
see such delay.

##

​

Examples

###

​

1\. Get a response in JSON format

**Request**

python

    
    
    import requests
    from pydantic import BaseModel
    
    class AnswerFormat(BaseModel):
        first_name: str
        last_name: str
        year_of_birth: int
        num_seasons_in_nba: int
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": (
                "Tell me about Michael Jordan. "
                "Please output a JSON object containing the following fields: "
                "first_name, last_name, year_of_birth, num_seasons_in_nba. "
            )},
        ],
        "response_format": {
    		    "type": "json_schema",
            "json_schema": {"schema": AnswerFormat.model_json_schema()},
        },
    }
    response = requests.post(url, headers=headers, json=payload).json()
    print(response["choices"][0]["message"]["content"])
    

**Response**

    
    
    {"first_name":"Michael","last_name":"Jordan","year_of_birth":1963,"num_seasons_in_nba":15}
    

###

​

2\. Use a regex to output the format

**Request**

python

    
    
    import requests
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": "What is the IPv4 address of OpenDNS DNS server?"},
        ],
        "response_format": {
    		    "type": "regex",
            "regex": {"regex": r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"},
        },
    }
    response = requests.post(url, headers=headers, json=payload).json()
    print(response["choices"][0]["message"]["content"])
    

**Response**

    
    
    208.67.222.222
    

##

​

Best Practices

###

​

Generating responses in a JSON Format

For Python users, we recommend using the Pydantic library to [generate JSON
schema](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_json_schema).

**Unsupported JSON Schemas**

Recursive JSON schema is not supported. As a result of that, unconstrained
objects are not supported either. Here’s a few example of unsupported schemas:

    
    
    # UNSUPPORTED!
    
    from typing import Any
    
    class UnconstrainedDict(BaseModel):
       unconstrained: dict[str, Any]
    
    class RecursiveJson(BaseModel):
       value: str
       child: list["RecursiveJson"]
    

###

​

Generating responses using a regex

**Supported Regex**

  * Characters: `\d`, `\w`, `\s` , `.`
  * Character classes: `[0-9A-Fa-f]` , `[^x]`
  * Quantifiers: `*`, `?` , `+`, `{3}`, `{2,4}` , `{3,}`
  * Alternation: `|`
  * Group: `( ... )`
  * Non-capturing group: `(?: ... )`
  * Positive lookahead: `(?= ... )`
  * Negative lookahead: `(?! ... )`

**Unsupported Regex**

  * Contents of group: `\1`
  * Anchors: `^`, `$`, `\b`
  * Positive look-behind: `(?<= ... )`
  * Negative look-behind: `(?<! ... )`
  * Recursion: `(?R)`

[Rate Limits and Usage Tiers](/guides/usage-tiers)[Prompt
Guide](/guides/prompt-guide)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

On this page

  * Overview
  * Examples
  * 1\. Get a response in JSON format
  * 2\. Use a regex to output the format
  * Best Practices
  * Generating responses in a JSON Format
  * Generating responses using a regex

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Prompt Guide

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Prompt Guide

##

​

System Prompt

You can use the system prompt to provide instructions related to style, tone,
and language of the response.

The real-time search component of our models does not attend to the system
prompt.

**Example of a system prompt**

    
    
    You are a helpful AI assistant.
    
    Rules:
    1. Provide only the final answer. It is important that you do not include any explanation on the steps below.
    2. Do not show the intermediate steps information.
    
    Steps:
    1. Decide if the answer should be a brief sentence or a list of suggestions.
    2. If it is a list of suggestions, first, write a brief and natural introduction based on the original query.
    3. Followed by a list of suggestions, each suggestion should be split by two newlines.
    

##

​

User Prompt

You should use the user prompt to pass in the actual query for which you need
an answer for. The user prompt will be used to kick off a real-time web search
to make sure the answer has the latest and the most relevant information
needed.

**Example of a user prompt**

    
    
    What are the best sushi restaurants in the world currently?
    

[Structured Outputs Guide](/guides/structured-outputs)[Perplexity
Crawlers](/guides/bots)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Guides

Perplexity Crawlers

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Guides

  * [Initial Setup](/guides/getting-started)
  * [Supported Models](/guides/model-cards)
  * [Pricing](/guides/pricing)
  * [Rate Limits and Usage Tiers](/guides/usage-tiers)
  * [Structured Outputs Guide](/guides/structured-outputs)
  * [Prompt Guide](/guides/prompt-guide)
  * [Perplexity Crawlers](/guides/bots)

Guides

# Perplexity Crawlers

We strive to improve our service every day by delivering the best search
experience possible. To achieve this, we collect data using web crawlers
(“robots”) and user agents that gather and index information from the
internet, operating either automatically or in response to user requests.
Webmasters can use the following robots.txt tags to manage how their sites and
content interact with Perplexity. Each setting works independently, and it may
take up to 24 hours for our systems to reflect changes.

User Agent| Description  
---|---  
PerplexityBot| `PerplexityBot` is designed to surface and link websites in
search results on Perplexity. It is not used to crawl content for AI
foundation models. To ensure your site appears in search results, we recommend
allowing `PerplexityBot` in your site’s `robots.txt` file and permitting
requests from our published IP ranges listed below.  
  
Full user-agent string: `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko;
compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)`  
  
Published IP addresses: <https://www.perplexity.com/perplexitybot.json>  
Perplexity‑User| `Perplexity-User` supports user actions within Perplexity.
When users ask Perplexity a question, it might visit a web page to help
provide an accurate answer and include a link to the page in its response.
`Perplexity-User` controls which sites these user requests can access. It is
not used for web crawling or to collect content for training AI foundation
models.  
  
Full user-agent string: `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko;
compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)`  
  
Published IP addresses: <https://www.perplexity.com/perplexity-user.json>  
  
Since a user requested the fetch, this fetcher generally ignores robots.txt
rules.  
  
[Prompt Guide](/guides/prompt-guide)

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

[Perplexity home page![light logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/SonarByPerplexity.svg)![dark
logo](https://mintlify.s3.us-
west-1.amazonaws.com/perplexity/logo/Sonar_Wordmark_Light.svg)](/home.mdx)

Search docs

  * [Playground](https://labs.perplexity.ai/)
  * [Playground](https://labs.perplexity.ai/)

Search...

Navigation

Perplexity API

Chat Completions

[Home](/home)[Guides](/guides/getting-started)[API Reference](/api-
reference/chat-completions)[Changelog](/changelog/changelog)[System
Status](/system-status/system-
status)[FAQ](/faq/faq)[Discussions](/discussions/discussions)

##### Perplexity API

  * [POSTChat Completions](/api-reference/chat-completions)

Perplexity API

# Chat Completions

Generates a model’s response for the given chat conversation.

POST

/

chat

/

completions

Try it

cURL

Python

JavaScript

PHP

Go

Java

    
    
    curl --request POST \
      --url https://api.perplexity.ai/chat/completions \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "model": "sonar",
      "messages": [
        {
          "role": "system",
          "content": "Be precise and concise."
        },
        {
          "role": "user",
          "content": "How many stars are there in our galaxy?"
        }
      ],
      "max_tokens": 123,
      "temperature": 0.2,
      "top_p": 0.9,
      "search_domain_filter": null,
      "return_images": false,
      "return_related_questions": false,
      "search_recency_filter": "<string>",
      "top_k": 0,
      "stream": false,
      "presence_penalty": 0,
      "frequency_penalty": 1,
      "response_format": null
    }'

200

422

    
    
    {
      "id": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
      "model": "sonar",
      "object": "chat.completion",
      "created": 1724369245,
      "citations": [
        "https://www.astronomy.com/science/astro-for-kids-how-many-stars-are-there-in-space/",
        "https://www.esa.int/Science_Exploration/Space_Science/Herschel/How_many_stars_are_there_in_the_Universe",
        "https://www.space.com/25959-how-many-stars-are-in-the-milky-way.html",
        "https://www.space.com/26078-how-many-stars-are-there.html",
        "https://en.wikipedia.org/wiki/Milky_Way"
      ],
      "choices": [
        {
          "index": 0,
          "finish_reason": "stop",
          "message": {
            "role": "assistant",
            "content": "The number of stars in the Milky Way galaxy is estimated to be between 100 billion and 400 billion stars. The most recent estimates from the Gaia mission suggest that there are approximately 100 to 400 billion stars in the Milky Way, with significant uncertainties remaining due to the difficulty in detecting faint red dwarfs and brown dwarfs."
          },
          "delta": {
            "role": "assistant",
            "content": ""
          }
        }
      ],
      "usage": {
        "prompt_tokens": 14,
        "completion_tokens": 70,
        "total_tokens": 84
      }
    }

#### Authorizations

​

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is
your auth token.

#### Body

application/json

​

model

string

required

The name of the model that will complete your prompt. Refer to [Supported
Models](https://docs.perplexity.ai/guides/model-cards) to find all the models
offered.

​

messages

object[]

required

A list of messages comprising the conversation so far.

Show child attributes

​

messages.content

string

required

The contents of the message in this turn of conversation.

​

messages.role

enum<string>

required

The role of the speaker in this turn of conversation. After the (optional)
system message, user and assistant roles should alternate with `user` then
`assistant`, ending in `user`.

Available options:

`system`,

`user`,

`assistant`

​

max_tokens

integer

The maximum number of completion tokens returned by the API. The number of
tokens requested in `max_tokens` plus the number of prompt tokens sent in
messages must not exceed the context window token limit of model requested. If
left unspecified, then the model will generate tokens until either it reaches
its stop token or the end of its context window.

​

temperature

number

default:

0.2

The amount of randomness in the response, valued between 0 inclusive and 2
exclusive. Higher values are more random, and lower values are more
deterministic.

Required range: `0 < x < 2`

​

top_p

number

default:

0.9

The nucleus sampling threshold, valued between 0 and 1 inclusive. For each
subsequent token, the model considers the results of the tokens with top_p
probability mass. We recommend either altering top_k or top_p, but not both.

Required range: `0 < x < 1`

​

search_domain_filter

any[]

Given a list of domains, limit the citations used by the online model to URLs
from the specified domains. Currently limited to only 3 domains for
whitelisting and blacklisting. For **blacklisting** add a `-` to the beginning
of the domain string. **Only available in certain tiers** \- refer to our
usage tiers [here](https://docs.perplexity.ai/guides/usage-tiers).

​

return_images

boolean

default:

false

Determines whether or not a request to an online model should return images.
**Only available in certain tiers** \- refer to our usage tiers
[here](https://docs.perplexity.ai/guides/usage-tiers).

​

return_related_questions

boolean

default:

false

Determines whether or not a request to an online model should return related
questions.**Only available in certain tiers** \- refer to our usage tiers
[here](https://docs.perplexity.ai/guides/usage-tiers).

​

search_recency_filter

string

Returns search results within the specified time interval - does not apply to
images. Values include `month`, `week`, `day`, `hour`.

​

top_k

number

default:

0

The number of tokens to keep for highest top-k filtering, specified as an
integer between 0 and 2048 inclusive. If set to 0, top-k filtering is
disabled. We recommend either altering top_k or top_p, but not both.

Required range: `0 < x < 2048`

​

stream

boolean

default:

false

Determines whether or not to incrementally stream the response with [server-
sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-
sent_events/Using_server-sent_events#event_stream_format) with `content-type:
text/event-stream`.

​

presence_penalty

number

default:

0

A value between -2.0 and 2.0. Positive values penalize new tokens based on
whether they appear in the text so far, increasing the model's likelihood to
talk about new topics. Incompatible with `frequency_penalty`.

Required range: `-2 < x < 2`

​

frequency_penalty

number

default:

1

A multiplicative penalty greater than 0. Values greater than 1.0 penalize new
tokens based on their existing frequency in the text so far, decreasing the
model's likelihood to repeat the same line verbatim. A value of 1.0 means no
penalty. Incompatible with `presence_penalty`.

Required range: `x > 0`

​

response_format

object

Enable structured outputs with a JSON or Regex schema. Refer to the guide
[here](https://docs.perplexity.ai/guides/structured-outputs) for more
information on how to use this parameter. **Only available in certain tiers**
\- refer to our usage tiers [here](https://docs.perplexity.ai/guides/usage-
tiers).

#### Response

200

200422

application/json

application/jsontext/event-stream

OK

​

id

string

An ID generated uniquely for each response.

​

model

string

The model used to generate the response.

​

object

string

The object type, which always equals `chat.completion`.

​

created

integer

The Unix timestamp (in seconds) of when the completion was created.

​

citations

any[]

Citations for the generated answer.

​

choices

object[]

The list of completion choices the model generated for the input prompt.

Show child attributes

​

choices.index

integer

​

choices.finish_reason

enum<string>

The reason the model stopped generating tokens. Possible values include `stop`
if the model hit a natural stopping point, or `length` if the maximum number
of tokens specified in the request was reached.

Available options:

`stop`,

`length`

​

choices.message

object

The message generated by the model.

Show child attributes

​

choices.message.content

string

required

The contents of the message in this turn of conversation.

​

choices.message.role

enum<string>

required

The role of the speaker in this turn of conversation. After the (optional)
system message, user and assistant roles should alternate with `user` then
`assistant`, ending in `user`.

Available options:

`system`,

`user`,

`assistant`

​

choices.delta

object

The incrementally streamed next tokens. Only meaningful when `stream = true`.

Show child attributes

​

choices.delta.content

string

required

The contents of the message in this turn of conversation.

​

choices.delta.role

enum<string>

required

The role of the speaker in this turn of conversation. After the (optional)
system message, user and assistant roles should alternate with `user` then
`assistant`, ending in `user`.

Available options:

`system`,

`user`,

`assistant`

​

usage

object

Usage statistics for the completion request.

Show child attributes

​

usage.prompt_tokens

integer

The number of tokens provided in the request prompt.

​

usage.completion_tokens

integer

The number of tokens generated in the response output.

​

usage.total_tokens

integer

The total number of tokens used in the chat completion (prompt + completion).

[twitter](https://twitter.com/perplexity_ai)[linkedin](https://www.linkedin.com/company/perplexity-
ai/)[discord](https://discord.com/invite/perplexity-
ai)[website](https://labs.perplexity.ai/)

cURL

Python

JavaScript

PHP

Go

Java

    
    
    curl --request POST \
      --url https://api.perplexity.ai/chat/completions \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "model": "sonar",
      "messages": [
        {
          "role": "system",
          "content": "Be precise and concise."
        },
        {
          "role": "user",
          "content": "How many stars are there in our galaxy?"
        }
      ],
      "max_tokens": 123,
      "temperature": 0.2,
      "top_p": 0.9,
      "search_domain_filter": null,
      "return_images": false,
      "return_related_questions": false,
      "search_recency_filter": "<string>",
      "top_k": 0,
      "stream": false,
      "presence_penalty": 0,
      "frequency_penalty": 1,
      "response_format": null
    }'

200

422

    
    
    {
      "id": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
      "model": "sonar",
      "object": "chat.completion",
      "created": 1724369245,
      "citations": [
        "https://www.astronomy.com/science/astro-for-kids-how-many-stars-are-there-in-space/",
        "https://www.esa.int/Science_Exploration/Space_Science/Herschel/How_many_stars_are_there_in_the_Universe",
        "https://www.space.com/25959-how-many-stars-are-in-the-milky-way.html",
        "https://www.space.com/26078-how-many-stars-are-there.html",
        "https://en.wikipedia.org/wiki/Milky_Way"
      ],
      "choices": [
        {
          "index": 0,
          "finish_reason": "stop",
          "message": {
            "role": "assistant",
            "content": "The number of stars in the Milky Way galaxy is estimated to be between 100 billion and 400 billion stars. The most recent estimates from the Gaia mission suggest that there are approximately 100 to 400 billion stars in the Milky Way, with significant uncertainties remaining due to the difficulty in detecting faint red dwarfs and brown dwarfs."
          },
          "delta": {
            "role": "assistant",
            "content": ""
          }
        }
      ],
      "usage": {
        "prompt_tokens": 14,
        "completion_tokens": 70,
        "total_tokens": 84
      }
    }

