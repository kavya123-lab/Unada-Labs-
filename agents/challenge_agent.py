"""
agents/challenge_agent.py
---------------------------
ChallengeAgent: produces the "Potential Business Challenges" section.
Reads the Company Overview written by the Analysis Agent plus the raw
research data, and asks Gemini to identify realistic, specific
challenges the company likely faces.
"""

from agents.base_agent import BaseAgent
from core.context import ResearchContext
from prompts.templates import build_challenge_prompt
from services.groq_service import GroqService
from utils.exceptions import AgentExecutionError


class ChallengeAgent(BaseAgent):
    """
    Uses Gemini to identify 3-5 plausible business challenges facing
    the target company, grounded in its overview and raw research.

    Parameters
    ----------
    gemini_service : GeminiService
        The LLM service this agent uses to generate text.
    """

    def __init__(self, groq_service: GroqService):
        super().__init__()
        self._groq_service= groq_service

    def run(self, context: ResearchContext) -> ResearchContext:
        """
        Generate the Potential Business Challenges section and store
        it in context.challenges.

        Parameters
        ----------
        context : ResearchContext
            Must already have research_data and overview populated by
            ResearchAgent and AnalysisAgent respectively.

        Returns
        -------
        ResearchContext
            The same context, with challenges populated.

        Raises
        ------
        AgentExecutionError
            If overview is empty (this agent ran out of order), or if
            Gemini returns a response that doesn't look usable.
        """
        if not context.overview:
            raise AgentExecutionError(
                "ChallengeAgent cannot run before context.overview has "
                "been populated. Make sure AnalysisAgent runs first."
            )

        self.logger.info(f"Identifying business challenges for '{context.company_name}'")
        prompt = build_challenge_prompt(
            company_name=context.company_name,
            overview=context.overview,
            research_text=context.research_data_as_text(),
        )
        response_text = self._groq_service.generate(prompt)

        # Unlike AnalysisAgent, this prompt asks for ONE section only,
        # so no header-splitting is needed — the whole response IS the
        # challenges list. We still do a light sanity check that it
        # looks like a markdown list before trusting and storing it.
        if "-" not in response_text and "*" not in response_text:
            raise AgentExecutionError(
                "Gemini's response for business challenges did not look "
                "like a markdown list. The model may have ignored the "
                "requested format — try regenerating."
            )

        context.challenges = response_text
        self.logger.info("Challenge identification complete")
        return context
