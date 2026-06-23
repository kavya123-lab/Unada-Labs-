"""
agents/opportunity_agent.py
------------------------------
OpportunityAgent: produces the "AI Opportunities" section. Reads the
Potential Business Challenges identified by the Challenge Agent and
asks Gemini to propose a specific AI or automation opportunity
addressing each one.

This is the first agent in the pipeline whose prompt depends on the
*output* of the immediately preceding agent, rather than only on the
original research data — which is exactly why the pipeline must run
these agents strictly in order, not in parallel.
"""

from agents.base_agent import BaseAgent
from core.context import ResearchContext
from prompts.templates import build_opportunity_prompt
from services.groq_service import GroqService
from utils.exceptions import AgentExecutionError


class OpportunityAgent(BaseAgent):
    """
    Uses Gemini to map each identified business challenge to a
    concrete AI or automation opportunity.

    Parameters
    ----------
    gemini_service : GeminiService
        The LLM service this agent uses to generate text.
    """

    def __init__(self,  groq_service: GroqService):
        super().__init__()
        self._groq_service = groq_service

    def run(self, context: ResearchContext) -> ResearchContext:
        """
        Generate the AI Opportunities section and store it in
        context.ai_opportunities.

        Parameters
        ----------
        context : ResearchContext
            Must already have overview and challenges populated by
            AnalysisAgent and ChallengeAgent respectively.

        Returns
        -------
        ResearchContext
            The same context, with ai_opportunities populated.

        Raises
        ------
        AgentExecutionError
            If challenges is empty (this agent ran out of order), or
            if Gemini returns a response that doesn't look usable.
        """
        if not context.challenges:
            raise AgentExecutionError(
                "OpportunityAgent cannot run before context.challenges "
                "has been populated. Make sure ChallengeAgent runs first."
            )

        self.logger.info(f"Generating AI opportunities for '{context.company_name}'")
        prompt = build_opportunity_prompt(
            company_name=context.company_name,
            overview=context.overview,
            challenges=context.challenges,
        )
        response_text = self._groq_service.generate(prompt)

        # Same lightweight sanity check as ChallengeAgent: confirm the
        # response looks like a markdown list before trusting it,
        # without being so strict that minor formatting variation
        # causes a false failure.
        if "-" not in response_text and "*" not in response_text:
            raise AgentExecutionError(
                "Gemini's response for AI opportunities did not look "
                "like a markdown list. The model may have ignored the "
                "requested format — try regenerating."
            )

        context.ai_opportunities = response_text
        self.logger.info("AI opportunity generation complete")
        return context
