"""
services/tavily_service.py
---------------------------
A thin wrapper around the Tavily Search API.

Why wrap a third-party SDK in our own class instead of calling it
directly from agents?
- If Tavily ever changes their SDK's method names or response format,
  you only need to update this one file — every agent that uses
  search keeps working unchanged.
- It lets us add consistent error handling and logging in exactly one
  place, instead of repeating try/except blocks inside every agent.
- It makes testing easier: in a unit test, you could create a fake
  TavilyService with the same search() method and hand it to an
  agent, without ever calling the real API or needing a real API key.
"""

from typing import List

from tavily import TavilyClient

from utils.exceptions import TavilyAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


class TavilyService:
    """
    Wraps the Tavily Python SDK behind a single, simple search() method.

    Parameters
    ----------
    api_key : str
        Your Tavily API key (loaded from config.py, which in turn
        loads it from your .env file).
    max_results : int
        How many search results Tavily should return per query.
    search_depth : str
        Either "basic" (faster, cheaper) or "advanced" (slower, more
        thorough). See config.py for the project's default choice.
    """

    def __init__(self, api_key: str, max_results: int = 5, search_depth: str = "basic"):
        self._client = TavilyClient(api_key=api_key)
        self._max_results = max_results
        self._search_depth = search_depth

    def search(self, query: str) -> List[str]:
        """
        Run a single search query against Tavily and return a list of
        readable text snippets.

        Parameters
        ----------
        query : str
            The search query string, e.g. "Tesla company overview".

        Returns
        -------
        List[str]
            Each item combines one result's title, URL, and content
            into a single readable string, ready to be joined into a
            Gemini prompt later.

        Raises
        ------
        TavilyAPIError
            If the request to Tavily fails for any reason — an invalid
            key, a network issue, or an unexpected response shape.
        """
        logger.info(f"Searching Tavily for: '{query}'")
        try:
            response = self._client.search(
                query=query,
                max_results=self._max_results,
                search_depth=self._search_depth,
            )
        except Exception as exc:
            # Tavily's SDK can raise several different exception types
            # depending on what went wrong (auth errors, connection
            # errors, timeouts, etc.). We deliberately catch all of
            # them here and translate them into our own TavilyAPIError,
            # so every agent only ever needs to handle ONE exception
            # type from this service, regardless of the root cause.
            raise TavilyAPIError(
                f"Tavily search failed for query '{query}': {exc}"
            ) from exc

        results = response.get("results", [])
        if not results:
            logger.info(f"Tavily returned no results for: '{query}'")
            return []

        snippets = []
        for result in results:
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            content = result.get("content", "")
            snippets.append(f"Title: {title}\nURL: {url}\nContent: {content}")

        logger.info(f"Tavily returned {len(snippets)} result(s) for: '{query}'")
        return snippets
