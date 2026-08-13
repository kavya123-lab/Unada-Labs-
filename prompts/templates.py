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
Write a concise summary (2-3 short paragraphs) that clearly covers:
- What the company does (its core business, in plain terms)
- Industry (the specific industry/sector it competes in)
- Scale (employee count, revenue, funding stage, number of
  customers/locations, or any other size indicator found in the data)
- Geographic presence (headquarters and the countries/regions it
  operates in or serves)

## Key Business Information
Write a bulleted list that identifies:
- Major offerings (its main products, services, or business lines)
- Recent developments (recent news, launches, funding rounds,
  partnerships, leadership changes, etc.)
- Expansion plans (any stated plans to enter new markets, launch new
  products, grow headcount, or scale operations)
- Important public information (anything else notable and verifiable —
  e.g. awards, certifications, major clients, regulatory matters,
  public statements from leadership)

Important rules:
- Only state facts that are supported by the search data above.
- If a specific detail above (e.g. scale, geographic presence,
  expansion plans) is not present in the search data, write "Not
  publicly available" for that detail instead of guessing or
  inventing it.
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

Based on the research and your own reasoning, identify 4 to 6 plausible,
specific business challenges this company likely faces. Draw from
across these angles, and only include ones that are actually plausible
for this company (skip any angle that genuinely doesn't apply rather
than forcing it):
- Possible challenges (broader strategic or market challenges)
- Operational bottlenecks (supply chain, capacity, process, staffing,
  or infrastructure constraints)
- Sales challenges (lead generation, conversion, pricing pressure,
  sales cycle length, channel issues)
- Customer experience challenges (support quality, onboarding,
  retention, satisfaction, personalization)

Avoid vague, generic challenges that could apply to any company (e.g.
"there is competition"). Ground every challenge in this company's
actual industry, size, geography, and any recent news mentioned above.

Format your answer in markdown as a list. For each challenge:
- Start with a short bolded title (3-6 words), and note in parentheses
  which category it falls under (Strategic / Operational / Sales /
  Customer Experience).
- Follow it with 1-2 sentences explaining the challenge AND your
  reasoning for why this company specifically is likely to face it
  (tie it back to a fact from the overview or research above).

Example format:
- **Rising customer acquisition costs** (Sales) — As the market
  matures, attracting new customers is becoming more expensive
  relative to customer lifetime value; this is likely to affect
  {company_name} given its stated reliance on digital marketing
  channels.

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
automation opportunity that could help address it. Where relevant,
draw on these categories (do not force all of them — only use what
genuinely fits each challenge):
- Automation (workflow, RPA, back-office process automation)
- Customer engagement (chatbots, personalization, recommendation
  engines)
- Sales (lead scoring, forecasting, sales enablement tools)
- Operations (demand forecasting, scheduling, supply chain
  optimization)
- Analytics (predictive analytics, dashboards, anomaly detection)
- Document processing (OCR, extraction, summarization, automated
  compliance checks)

Name an actual technique or application specific to THIS company's
context (for example, "a demand-forecasting model trained on
[company]'s historical sales data" or "an AI-powered support triage
system for [company]'s customer service queue") rather than vague
buzzwords like "leverage AI synergies" or "implement AI solutions."
Every suggestion must be clearly tailored to this company — do not
write anything generic enough to paste into a brief for a different
company unchanged.

Format your answer in markdown as a list, with one entry per
challenge, in the same order as the challenges above:
- Start with a short bolded title for the opportunity (3-6 words).
- Follow it with one or two sentences explaining the opportunity, how
  it works, and how it directly addresses the related challenge for
  {company_name}.

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
    return f"""You are preparing to meet the CEO of {company_name} in person, and
are writing a one-page personalized pitch to bring to that meeting, on
behalf of an AI solutions provider.

Company overview:
{overview}

Business challenges identified:
{challenges}

AI opportunities identified:
{ai_opportunities}

Write a one-page pitch (roughly 350-450 words), in first person,
addressed directly to the CEO by title (e.g. "Dear [CEO's name]," if a
name is available in the overview above, otherwise "Dear [Company]
Leadership Team,"). Structure it in markdown with these sections,
using the exact section headings below:

## Why I'm Reaching Out
Open by referencing something specific and real about the company from
the overview above (not a generic greeting like "I hope this finds you
well"). Briefly explain why this company, specifically, prompted the
outreach.

## Opportunities We Identified
Summarize 2-3 of the most compelling business challenges from the list
above, in plain business language, showing you understand their
situation.

## Recommended AI Solutions
For each challenge summarized above, describe the specific AI solution
recommended and the concrete business value it delivers (time saved,
cost reduced, revenue enabled, experience improved) — in plain
business terms, not technical jargon.

## Next Step
Close with a soft, low-pressure call to action (e.g. suggesting a
short call or a 15-minute walkthrough), not a hard sell.

Do not use generic flattery or filler phrases. Write only the pitch
itself with the four headings above — no extra preamble or
explanation before or after it."""
