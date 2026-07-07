"""
tools.py — The Agent's Hands

Each function below is a deterministic piece of Python that the LLM can choose
to call. The LLM never runs this code itself — LangGraph intercepts the model's
"I want to call tool X with arguments Y" request, runs the real Python function,
and feeds the return value back to the model as an Observation.

The docstring under each @tool IS the tool's description. The model reads it to
decide when (and when not) to use the tool. Weak docstrings = wrong tool calls.
"""

import re
import requests
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


@tool
def github_fetcher(url: str) -> str:
    """Fetches raw code from a GitHub URL. Use this ONLY when the user's prompt
    contains a github.com link (e.g. https://github.com/user/repo/blob/main/file.py).
    Do NOT use this for general web searches or for any URL that isn't github.com.
    Input must be the exact URL the user provided."""
    try:
        # Convert a normal GitHub "blob" URL into the raw-content URL.
        # https://github.com/user/repo/blob/main/script.py
        #   -> https://raw.githubusercontent.com/user/repo/main/script.py
        raw_url = re.sub(
            r"github\.com/([^/]+)/([^/]+)/blob/",
            r"raw.githubusercontent.com/\1/\2/",
            url,
        ).replace("https://github.com", "https://raw.githubusercontent.com") \
         if "raw.githubusercontent.com" not in url else url

        response = requests.get(raw_url, timeout=5)
        response.raise_for_status()
        return response.text[:6000]  # cap length so we don't blow the context window
    except requests.exceptions.RequestException as e:
        return f"Error fetching GitHub file: {e}"


@tool
def library_docs_search(query: str) -> str:
    """Search the web for programming library, framework, or built-in function
    documentation. Use this STRICTLY when you encounter an imported library or
    an unfamiliar API call in the user's code that you need to verify before
    explaining it. NEVER use this for general knowledge, opinions, or anything
    not directly about a library/API in the snippet."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)[:2000]
    except Exception as e:
        return f"Documentation search failed: {e}"


# All tools the agent is allowed to use, in one place so agent.py only imports one thing.
ALL_TOOLS = [github_fetcher, library_docs_search]
