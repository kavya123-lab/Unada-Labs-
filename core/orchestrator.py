"""
core/orchestrator.py
----------------------
ResearchOrchestrator: wires together every service and agent built so
far into one runnable pipeline, and exposes a single run(company_name)
method as the one entry point app.py needs to call.
"""

from typing import List

import config
from agents.analysis_agent import AnalysisAgent
from agents.base_agent import BaseAgent
from agents.challenge_agent import ChallengeAgent
from agents.opportunity_agent import OpportunityAgent
from agents.pitch_agent import PitchAgent
from agents.research_agent import ResearchAgent
from core.context import ResearchContext
from services.groq_service import GroqService
from services.tavily_service import TavilyService
from utils.exceptions import ResearchAgentError
from utils.logger import get_logger

logger = get_logger(__name__)


class ResearchOrchestrator:
    """
    Builds the Tavily and Gemini services, builds all five agents on
    top of them, and runs the agents in the correct order for a given
    company name.

    This class is the only place in the project that knows the full
    pipeline order — every individual agent only knows its own job,
    not what comes before or after it.
    """

    def __init__(self):
        tavily_service = TavilyService(
            api_key=config.TAVILY_API_KEY,
            max_results=config.TAVILY_MAX_RESULTS,
            search_depth=config.TAVILY_SEARCH_DEPTH,
        )
        groq_service= GroqService(
            api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL_NAME,
            temperature=config.GROQ_TEMPERATURE,
            max_tokens=config.GROQ_MAX_TOKENS,
        )

        # The order of this list IS the pipeline order. Each agent
        # depends on fields written by the agent(s) before it, so this
        # sequence must never be reordered without also reconsidering
        # every agent's precondition checks.
        self._agents: List[BaseAgent] = [
            ResearchAgent(tavily_service),
            AnalysisAgent( groq_service),
            ChallengeAgent( groq_service),
            OpportunityAgent( groq_service),
            PitchAgent(groq_service),
        ]

    def run(self, company_name: str) -> ResearchContext:
        """
        Run the full agent pipeline for the given company name.

        Parameters
        ----------
        company_name : str
            The company to research, as typed by the user in the
            Streamlit UI.

        Returns
        -------
        ResearchContext
            The completed context, with every section populated and
            ready to be rendered by the UI.

        Raises
        ------
        ValueError
            If company_name is empty or only whitespace.
        ResearchAgentError
            If any agent in the pipeline fails. The error message
            indicates which agent failed and why.
        """
        company_name = company_name.strip()
        if not company_name:
            raise ValueError("Company name cannot be empty.")

        logger.info(f"=== Starting pipeline for '{company_name}' ===")
        context = ResearchContext(company_name=company_name)

        for agent in self._agents:
            agent_name = agent.__class__.__name__
            try:
                context = agent.run(context)
            except ResearchAgentError:
                # No need to wrap or modify the exception here — it's
                # already a clear, specific error raised from inside
                # the agent or one of its services. We just log which
                # pipeline stage it happened at, then let it propagate
                # up to app.py, which displays it to the user.
                logger.error(f"Pipeline stopped at {agent_name}")
                raise

        if not context.is_complete():
            logger.warning(
                f"Pipeline finished but context is not fully complete "
                f"for '{company_name}'. Some sections may be missing."
            )
        else:
            logger.info(f"=== Pipeline complete for '{company_name}' ===")

        return context
