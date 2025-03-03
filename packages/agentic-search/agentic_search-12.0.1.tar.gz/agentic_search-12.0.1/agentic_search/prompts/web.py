from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate


def get_claim_verification_web_search_query_prompt() -> ChatPromptTemplate:
    """
    Get a prompt to generate a single search engine query from a claim to verify.

    Input keys are:
    - `claim`: the claim to verify
    """
    claim_verification_search_query_prompt_template = """Create a single, focused web search engine query to verify this claim:
---
{claim}
---

Strictly output valid JSON (no markdown or other formatting): {{"query": "query"}}"""
    return ChatPromptTemplate.from_template(
        claim_verification_search_query_prompt_template
    )


def get_route_search_type_prompt() -> ChatPromptTemplate:
    route_search_type_prompt_template = """You are an AI assistant that helps determine what type of results would be more appropriate for a user's query.

Available search types are:
- news
- text
- video

Choose news type if the user query involves:
- a current event
- a live indicator
- a news person or topic

Choose video type if the user query involves:
- a physical demonstration
- a visual process
- DIY work or sequences of steps to be executed by a human
- some spatial understanding

Otherwise, choose text type.

Here is the user query, delimited by triple dashes:
---
{query}
---

Strictly output valid JSON (no markdown or other formatting): {{"search_type": "news" | "text" | "video"}}
"""
    return ChatPromptTemplate.from_template(route_search_type_prompt_template)


def get_web_search_agent_system_prompt() -> str:
    prompt = """You are a precise research assistant equipped with a web search tool. Your tasks:
1. Provide accurate, current information
2. Synthesize multi-source information concisely
3. Include citations and maintain objectivity

Focus on authoritative, verifiable sources only.

Skip web search if you are completely certain of information and if the user query is not about a current event, live indicator, news person or topic.
Otherwise, perform targeted searches as needed.
You will give an answer that contains your findings, whatever they are.
No need to use the web search tool if you have enough information to answer the user query, even if incomplete.

Answer in JSON format without any preamble, formatting, or explanatory text, just a valid JSON object in this format:

{{
    "content": "your results as a string or the video URL if type is video",
    "metadata": "any additional metadata that was attached to the web search results" | null,
    "type": "text" | "video"
}}"""
    # ground the LLM in time
    prompt += f"""
Today is {datetime.now().strftime('%Y-%m-%d')}."""
    return prompt


def get_web_search_query_prompt(excluded_queries: list[str] = []) -> ChatPromptTemplate:
    """
    Get a prompt to generate a single search engine query from a user query.

    Input keys are:
    - `query`: the user query to expand
    """
    web_search_query_prompt_template = """Generate appropriate a single web search engine query to maximize the quality of the search results following a user query.

Here is the user query, delimited by triple dashes:
---
{query}
---

IMPORTANT: generate ONLY one query to best cover the topic

Strictly output valid JSON (no markdown or other formatting):
{{"query": "query"}}"""
    # ground the LLM in time
    web_search_query_prompt_template += f"""
Today is {datetime.now().strftime('%Y-%m-%d')}."""
    # add excluded queries to the prompt
    if len(excluded_queries) > 0:
        web_search_query_prompt_template += f"""
Your output MUST NOT include the following queries:
- {"\n- ".join(excluded_queries)}"""
    return ChatPromptTemplate.from_template(web_search_query_prompt_template)


def get_web_search_queries_prompt(
    excluded_queries: list[str] = [],
) -> ChatPromptTemplate:
    """
    Get a prompt to generate a list of search engine queries from a user query.

    Input keys are:
    - `query`: the user query to expand
    """
    web_search_queries_prompt_template = """Generate appropriate web search engine queries to find objective information about this user query:

---
{query}
---

IMPORTANT: 
- generate as many queries as needed to thoroughly cover the topic
- use fewer queries for simple topics, more for complex ones
- each query should target a distinct aspect of the information needed
- avoid redundant queries

Strictly output valid JSON (no markdown or other formatting):
{{"queries": ["query 1", "query 2", ...]}}"""
    # ground the LLM in time
    web_search_queries_prompt_template += f"""
Today is {datetime.now().strftime('%Y-%m-%d')}."""
    # add excluded queries to the prompt
    if len(excluded_queries) > 0:
        web_search_queries_prompt_template += f"""
Your output MUST NOT include the following queries:
- {"\n- ".join(excluded_queries)}"""
    return ChatPromptTemplate.from_template(web_search_queries_prompt_template)
