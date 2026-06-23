"""
prompts/templates.py
---------------------
All Gemini prompt text for the project, centralized in one file.

Why centralize prompts instead of writing them inline inside each
agent?
- Prompt wording is something you'll tune repeatedly while testing —
  having it all in one file means you can compare and adjust every
  prompt side by side, without hunting through five agent files.
- It keeps agent classes focused on *control flow* (when to call
  Gemini, what to do with the result) rather than mixing in large
  blocks of prompt text, which makes agent code much easier to read.
- In version control, a prompt-wording change shows up as a small,
  obvious diff in this one file, instead of being buried inside a
  larger agent class.

Each function below builds and returns ONE complete prompt string for
ONE specific agent. Agents call these functions and pass the result
straight to GeminiService.generate().
"""


def build_analysis_prompt(company_name: str, research_text: str) -> str:
    """
    Build the prompt for the Analysis Agent, which produces the
    "Company Overview" and "Key Business Information" sections.

    Parameters
    ----------
    company_name : str
        The company being researched.
    research_text : str
        Raw search snippets gathered by the Research Agent
        (ResearchContext.research_data_as_text()).

    Returns
    -------
    str
        The complete prompt to send to Gemini.
    """
    return f"""You are a business analyst preparing a research brief on {company_name}.

Below is raw web search data about the company:

---
{research_text}
---

Using ONLY the information above, write two sections in markdown:

## Company Overview
Write 2-3 short paragraphs covering what the company does, its
industry, approximate size, and founding background if available.

## Key Business Information
Write a short bulleted list covering: headquarters location, industry,
main products or services, key markets, and leadership (if known).

Important rules:
- Only state facts that are supported by the search data above.
- If a specific detail (e.g. founding year, headquarters) is not
  present in the search data, write "Not publicly available" for that
  detail instead of guessing or inventing it.
- Do not add any section other than the two requested above.
- Write in clear, professional business English."""


def build_challenge_prompt(company_name: str, overview: str, research_text: str) -> str:
    """
    Build the prompt for the Challenge Agent, which produces the
    "Potential Business Challenges" section.

    Parameters
    ----------
    company_name : str
        The company being researched.
    overview : str
        The Company Overview text already produced by the Analysis Agent.
    research_text : str
        Raw search snippets, used for extra context (e.g. recent news).

    Returns
    -------
    str
        The complete prompt to send to Gemini.
    """
    return f"""You are a management consultant analyzing {company_name}.

Company overview:
{overview}

Additional raw research (recent news, industry context, etc.):
---
{research_text}
---

Identify 3 to 5 plausible, specific business challenges this company
likely faces, grounded in its actual industry, size, and any recent
news mentioned above. Avoid vague, generic challenges that could apply
to any company (e.g. "there is competition").

Format your answer in markdown as a list. For each challenge:
- Start with a short bolded title (3-6 words).
- Follow it with one clear sentence explaining the challenge.

Example format:
- **Rising customer acquisition costs** — As the market matures,
  attracting new customers is becoming more expensive relative to
  customer lifetime value.

Write only the list, with no introduction or closing remarks."""


def build_opportunity_prompt(company_name: str, overview: str, challenges: str) -> str:
    """
    Build the prompt for the Opportunity Agent, which produces the
    "AI Opportunities" section.

    Parameters
    ----------
    company_name : str
        The company being researched.
    overview : str
        The Company Overview text from the Analysis Agent.
    challenges : str
        The Potential Business Challenges text from the Challenge Agent.

    Returns
    -------
    str
        The complete prompt to send to Gemini.
    """
    return f"""You are an AI solutions consultant advising {company_name}.

Company overview:
{overview}

Identified business challenges:
{challenges}

For each challenge listed above, propose one concrete, specific AI or
automation opportunity that could help address it. Name an actual
technique or application (for example, "a demand-forecasting model
trained on historical sales data" or "an AI-powered customer support
triage system") rather than vague buzzwords like "leverage AI
synergies" or "implement AI solutions."

Format your answer in markdown as a list, with one entry per
challenge, in the same order as the challenges above:
- Start with a short bolded title for the opportunity (3-6 words).
- Follow it with one or two sentences explaining the opportunity and
  how it addresses the related challenge.

Write only the list, with no introduction or closing remarks."""


def build_pitch_prompt(
    company_name: str,
    overview: str,
    challenges: str,
    ai_opportunities: str,
) -> str:
    """
    Build the prompt for the Pitch Agent, which produces the
    "Personalized CEO Pitch" section — the final output of the pipeline.

    Parameters
    ----------
    company_name : str
        The company being researched.
    overview : str
        The Company Overview text from the Analysis Agent.
    challenges : str
        The Potential Business Challenges text from the Challenge Agent.
    ai_opportunities : str
        The AI Opportunities text from the Opportunity Agent.

    Returns
    -------
    str
        The complete prompt to send to Gemini.
    """
    return f"""You are writing a short, personalized outreach message to
the CEO of {company_name}, on behalf of an AI solutions provider.

Company overview:
{overview}

Business challenges:
{challenges}

AI opportunities:
{ai_opportunities}

Write a pitch of 150-200 words, in first person, addressed directly to
the CEO. The pitch must:
- Open by referencing something specific and real about the company
  (not a generic greeting like "I hope this finds you well").
- Name ONE specific challenge from the list above and ONE specific AI
  opportunity that addresses it.
- Explain the value in plain business terms, not technical jargon.
- Close with a soft, low-pressure call to action (e.g. suggesting a
  short call), not a hard sell.

Do not use generic flattery or filler phrases. Write only the pitch
text itself, with no heading, label, or explanation before or after it."""
