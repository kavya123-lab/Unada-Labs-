"""
agents/research_agent.py
--------------------------
ResearchAgent: the first agent in the pipeline. Gathers raw web
research about the target company using the Tavily Search API.

This is the only agent that does NOT call Gemini — its job is purely
to collect raw material that the four LLM-powered agents downstream
will reason over.
"""

from typing import List
from agents.base_agent import BaseAgent
from core.context import ResearchContext
from services.tavily_service import TavilyService
from utils.exceptions import AgentExecutionError, TavilyAPIError


class ResearchAgent(BaseAgent):
    """
    Runs several targeted Tavily searches about the target company and
    stores the combined results in context.research_data.

    Parameters
    ----------
    tavily_service : TavilyService
        The search service this agent uses to gather data. Passed in
        (dependency injection) rather than created internally, so this
        agent can be tested with a fake service if needed, without
        ever calling the real Tavily API.
    """

    def __init__(self, tavily_service: TavilyService):
        super().__init__()
        self._tavily_service = tavily_service

    def _build_queries(self, company_name: str) -> List[str]:
        """
        Build a set of targeted search queries for the given company.

        Running several focused queries instead of one broad query
        gives the downstream Analysis Agent much richer, more varied
        raw material to work with.
        """
        return [
            f"{company_name} company overview",
            f"{company_name} recent news",
            f"{company_name} products and services",
            f"{company_name} competitors industry",
        ]

    def run(self, context: ResearchContext) -> ResearchContext:
        """
        Run all queries for context.company_name and store the
        combined results in context.research_data.

        Parameters
        ----------
        context : ResearchContext
            Must already have company_name set; research_data starts
            empty and is filled in by this method.

        Returns
        -------
        ResearchContext
            The same context, with research_data populated.

        Raises
        ------
        AgentExecutionError
            If every single search query fails or returns no usable
            results, meaning there would be nothing for downstream
            agents to work with.
        """
        self.logger.info(f"Starting research for '{context.company_name}'")
        queries = self._build_queries(context.company_name)

        all_snippets: List[str] = []
        failed_queries = 0

        for query in queries:
            try:
                snippets = self._tavily_service.search(query)
                all_snippets.extend(snippets)
            except TavilyAPIError as exc:
                # One failed query shouldn't sink the whole research
                # step — log it and keep trying the remaining queries.
                # This is only treated as fatal below if EVERY query fails.
                self.logger.error(f"Query failed: '{query}' — {exc}")
                failed_queries += 1

        if not all_snippets:
            raise AgentExecutionError(
                f"Research failed for '{context.company_name}': all "
                f"{len(queries)} search queries failed or returned no "
                f"results. Check your Tavily API key and network connection."
            )

        context.research_data = all_snippets
        self.logger.info(
            f"Research complete: {len(all_snippets)} snippet(s) gathered "
            f"from {len(queries) - failed_queries}/{len(queries)} successful queries"
        )
        return context
