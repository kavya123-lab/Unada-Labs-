"""
core/context.py
----------------
Defines ResearchContext: the single shared data object that flows
through every agent in the pipeline.

Why a dataclass instead of a plain dictionary?
- A dataclass gives every field a name, a type, and a default value up
  front, so your editor can autocomplete `context.overview` instead of
  you guessing whether a dict key was "overview" or "Overview".
- It documents the entire shape of the pipeline's data in one place —
  reading this file alone tells you exactly what each agent produces.
- It catches typos at development time rather than failing silently:
  `context.overveiw` (a typo) raises an AttributeError immediately,
  while `research_data["overveiw"]` on a plain dict would just quietly
  return None or raise a KeyError somewhere unrelated, much later.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ResearchContext:
    """
    Holds all data for a single company's research run, from the
    initial company name through to every output section.

    The orchestrator creates exactly one ResearchContext per run and
    passes it to each agent in sequence. Each agent reads whatever
    fields earlier agents have already filled in, then writes its own
    result into its own field(s) before returning the same object.

    Attributes
    ----------
    company_name : str
        The company name the user typed into the Streamlit UI. This is
        the only field set before the pipeline starts; every other
        field begins empty and is filled in by exactly one agent.
    research_data : List[str]
        Raw search result snippets gathered by the Research Agent from
        Tavily. Stored as a list of plain strings (each combining a
        result's title, URL, and content) so downstream agents can
        easily join them into a single block of text for a Gemini prompt.
    overview : str
        The "Company Overview" section, written by the Analysis Agent.
    key_info : str
        The "Key Business Information" section, also written by the
        Analysis Agent.
    challenges : str
        The "Potential Business Challenges" section, written by the
        Challenge Agent.
    ai_opportunities : str
        The "AI Opportunities" section, written by the Opportunity Agent.
    ceo_pitch : str
        The "Personalized CEO Pitch" section, written by the Pitch Agent.
    """

    company_name: str
    research_data: List[str] = field(default_factory=list)
    overview: str = ""
    key_info: str = ""
    challenges: str = ""
    ai_opportunities: str = ""
    ceo_pitch: str = ""

    def has_research_data(self) -> bool:
        """
        Return True if the Research Agent has gathered at least one
        usable search result.

        Later agents call this before doing any work, so they fail
        fast with a clear error if they're accidentally run before
        research has happened, instead of silently sending an empty
        or near-empty prompt to Gemini.
        """
        return len(self.research_data) > 0

    def research_data_as_text(self) -> str:
        """
        Combine all raw research snippets into a single block of text,
        ready to be inserted into a Gemini prompt.

        Returns
        -------
        str
            All research snippets joined with a blank line between
            each one, or an empty string if no research has been
            gathered yet.
        """
        return "\n\n".join(self.research_data)

    def is_complete(self) -> bool:
        """
        Return True only if every output section has been filled in by
        its corresponding agent.

        Used by the orchestrator as a final sanity check before
        handing the context back to the Streamlit UI, so an agent
        that silently failed to write its section gets caught here
        instead of showing up as a blank area in the final report.
        """
        return all([
            self.overview,
            self.key_info,
            self.challenges,
            self.ai_opportunities,
            self.ceo_pitch,
        ])
