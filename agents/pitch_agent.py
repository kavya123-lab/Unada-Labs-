"""
agents/pitch_agent.py
-----------------------
PitchAgent: the final agent in the pipeline. Combines the company
overview, business challenges, and AI opportunities into a short,
personalized pitch written directly to the company's CEO.
"""

from agents.base_agent import BaseAgent
from core.context import ResearchContext
from prompts.templates import build_pitch_prompt
from services.groq_service import GroqService
from utils.exceptions import AgentExecutionError

# A pitch shorter than this is almost certainly a malformed or
# truncated response rather than a genuine, usable pitch — the prompt
# asks for 150-200 words, so anything drastically below that is
# treated as a sign something went wrong.
MIN_EXPECTED_WORDS = 40


class PitchAgent(BaseAgent):
    """
    Uses Gemini to write a short, personalized outreach pitch to the
    target company's CEO, referencing one specific challenge and one
    specific AI opportunity by name.

    Parameters
    ----------
    gemini_service : GeminiService
        The LLM service this agent uses to generate text.
    """

    def __init__(self, groq_service: GroqService):
        super().__init__()
        self._groq_service = groq_service

    def run(self, context: ResearchContext) -> ResearchContext:
        """
        Generate the Personalized CEO Pitch and store it in
        context.ceo_pitch.

        Parameters
        ----------
        context : ResearchContext
            Must already have overview, challenges, and
            ai_opportunities populated by the three agents before it.

        Returns
        -------
        ResearchContext
            The same context, with ceo_pitch populated. This is the
            final agent in the pipeline, so the context should now be
            fully complete — see ResearchContext.is_complete().

        Raises
        ------
        AgentExecutionError
            If ai_opportunities is empty (this agent ran out of
            order), or if Gemini's response is suspiciously short to
            plausibly be a usable pitch.
        """
        if not context.ai_opportunities:
            raise AgentExecutionError(
                "PitchAgent cannot run before context.ai_opportunities "
                "has been populated. Make sure OpportunityAgent runs first."
            )

        self.logger.info(f"Writing CEO pitch for '{context.company_name}'")
        prompt = build_pitch_prompt(
            company_name=context.company_name,
            overview=context.overview,
            challenges=context.challenges,
            ai_opportunities=context.ai_opportunities,
        )
        response_text = self._groq_service.generate(prompt)

        word_count = len(response_text.split())
        if word_count < MIN_EXPECTED_WORDS:
            raise AgentExecutionError(
                f"Gemini's pitch response was only {word_count} words, "
                f"far shorter than the requested 150-200 — it may be "
                f"malformed. Try regenerating."
            )

        context.ceo_pitch = response_text
        self.logger.info(f"Pitch complete ({word_count} words)")
        return context
