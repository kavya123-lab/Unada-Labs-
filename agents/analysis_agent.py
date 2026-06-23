"""
agents/analysis_agent.py
--------------------------
AnalysisAgent: the first Gemini-powered agent in the pipeline. Reads
the raw research data gathered by the Research Agent and produces the
"Company Overview" and "Key Business Information" sections.
"""

from typing import Tuple

from agents.base_agent import BaseAgent
from core.context import ResearchContext
from prompts.templates import build_analysis_prompt
from services.groq_service import GroqService
from utils.exceptions import AgentExecutionError

# These must exactly match the markdown headers requested in
# build_analysis_prompt() — if you ever edit the prompt's headers,
# update these two constants to match.
OVERVIEW_HEADER = "## Company Overview"
KEY_INFO_HEADER = "## Key Business Information"


class AnalysisAgent(BaseAgent):
    """
    Uses Gemini to turn raw research data into a structured Company
    Overview and Key Business Information.

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
        Generate the Company Overview and Key Business Information
        sections and store them in context.overview / context.key_info.

        Parameters
        ----------
        context : ResearchContext
            Must already have research_data populated by ResearchAgent.

        Returns
        -------
        ResearchContext
            The same context, with overview and key_info populated.

        Raises
        ------
        AgentExecutionError
            If research_data is empty (this agent ran out of order),
            or if Gemini's response can't be split into the two
            expected sections.
        """
        if not context.has_research_data():
            raise AgentExecutionError(
                "AnalysisAgent cannot run before research_data has been "
                "populated. Make sure ResearchAgent runs first."
            )

        self.logger.info(f"Analyzing research data for '{context.company_name}'")
        prompt = build_analysis_prompt(
            company_name=context.company_name,
            research_text=context.research_data_as_text(),
        )
        response_text = self._groq_service.generate(prompt)

        overview, key_info = self._split_sections(response_text)
        context.overview = overview
        context.key_info = key_info

        self.logger.info("Analysis complete")
        return context

    def _split_sections(self, response_text: str) -> Tuple[str, str]:
        """
        Split Gemini's raw markdown response into the Company Overview
        and Key Business Information sections.

        Parameters
        ----------
        response_text : str
            The full text Gemini returned, expected to contain both
            "## Company Overview" and "## Key Business Information"
            headers, in that order.

        Returns
        -------
        Tuple[str, str]
            (overview_text, key_info_text), each with its section
            header stripped off and surrounding whitespace trimmed.

        Raises
        ------
        AgentExecutionError
            If either expected header is missing from the response,
            meaning Gemini did not follow the requested format.
        """
        if OVERVIEW_HEADER not in response_text or KEY_INFO_HEADER not in response_text:
            raise AgentExecutionError(
                "Gemini's response did not include both expected section "
                "headers ('Company Overview' and 'Key Business "
                "Information'). The model may have ignored the requested "
                "format — try regenerating."
            )

        # Split once on the Key Business Information header: everything
        # before it is the overview section (including its own header,
        # which we strip off next), everything after it is the key info.
        overview_part, key_info_part = response_text.split(KEY_INFO_HEADER, 1)

        overview = overview_part.replace(OVERVIEW_HEADER, "", 1).strip()
        key_info = key_info_part.strip()

        return overview, key_info
