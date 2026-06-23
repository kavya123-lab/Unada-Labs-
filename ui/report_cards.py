"""
ui/report_cards.py
--------------------
Renders a completed ResearchContext as a modern, card-based dashboard
instead of one long scrolling page: a small summary strip at the top,
followed by five expandable, individually styled cards — one per
report section.

This module owns ALL Streamlit code related to displaying a report.
app.py only ever calls render_report_cards(context) — it doesn't know
or care how the cards are built, styled, or ordered.
"""

from typing import List, Tuple

import streamlit as st

from core.context import ResearchContext

# Each card is defined as (icon, title, ResearchContext attribute
# name, accent color). Defining this once as data — rather than
# writing five separate, nearly-identical blocks of Streamlit calls —
# means adding a sixth report section later is a one-line change
# here, not a copy-pasted new block of UI code.
_CARD_DEFINITIONS: List[Tuple[str, str, str, str]] = [
    ("📊", "Company Overview", "overview", "#4F46E5"),
    ("📈", "Key Business Information", "key_info", "#0EA5E9"),
    ("⚠️", "Business Challenges", "challenges", "#F59E0B"),
    ("🤖", "AI Opportunities", "ai_opportunities", "#10B981"),
    ("🎯", "CEO Pitch", "ceo_pitch", "#EF4444"),
]


def inject_dashboard_styles() -> None:
    """
    Inject the CSS that turns Streamlit's default expanders into
    visually separated, professionally styled "cards": rounded
    corners, a subtle shadow, breathing room between sections, and a
    colored accent stripe per card matching _CARD_DEFINITIONS above.

    This targets Streamlit's documented data-testid hooks rather than
    its internal (and frequently changing) auto-generated CSS class
    names, which keeps it reasonably stable across Streamlit
    versions. That said, Streamlit's exact DOM structure can still
    shift between major releases — if cards ever look unstyled after
    upgrading Streamlit, this function is the first place to check
    (inspect the page in your browser's dev tools and update the
    data-testid selectors below to match).

    Call this once near the top of app.py's main(), before anything
    else is rendered on the page.
    """
    # Build one CSS rule per card, giving each expander a colored
    # left border matching its position in _CARD_DEFINITIONS. CSS's
    # :nth-of-type selector is 1-indexed, so we start counting at 1.
    accent_rules = "\n".join(
        f'div[data-testid="stExpander"]:nth-of-type({position}) {{ '
        f'border-left: 4px solid {color}; }}'
        for position, (_, _, _, color) in enumerate(_CARD_DEFINITIONS, start=1)
    )

    st.markdown(
        f"""
        <style>
        div[data-testid="stExpander"] {{
            border: 1px solid rgba(49, 51, 63, 0.15);
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }}
        div[data-testid="stExpander"] summary {{
            font-size: 1.05rem;
            font-weight: 600;
            padding: 0.9rem 1rem;
        }}
        div[data-testid="stExpanderDetails"] {{
            padding: 0.25rem 1.25rem 1.25rem 1.25rem;
        }}
        {accent_rules}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _section_word_count(text: str) -> int:
    """
    Count words in a single report section's text.

    Parameters
    ----------
    text : str
        The section's text, possibly empty.

    Returns
    -------
    int
        The word count, or 0 if the text is empty.
    """
    return len(text.split()) if text else 0


def _render_summary_strip(context: ResearchContext) -> None:
    """
    Render a small dashboard-style summary row above the cards,
    showing the company name, how many sections were successfully
    generated, and the total word count across the whole report.

    Parameters
    ----------
    context : ResearchContext
        The completed (or partially completed) pipeline output.
    """
    section_values = [getattr(context, attr) for _, _, attr, _ in _CARD_DEFINITIONS]
    completed_count = sum(1 for value in section_values if value)
    total_words = sum(_section_word_count(value) for value in section_values)

    col1, col2, col3 = st.columns(3)
    col1.metric("Company", context.company_name)
    col2.metric("Sections generated", f"{completed_count}/{len(_CARD_DEFINITIONS)}")
    col3.metric("Total words", total_words)


def render_report_cards(context: ResearchContext) -> None:
    """
    Render a completed ResearchContext as a modern card dashboard:
    a summary strip followed by five expandable, color-accented cards.

    Parameters
    ----------
    context : ResearchContext
        The completed pipeline output to display. A section with no
        content (for example, if a partial pipeline failure left one
        field empty) is still shown as its own card with a visible
        placeholder message, rather than being silently hidden.
    """
    st.header(f"Research Report: {context.company_name}")
    _render_summary_strip(context)
    st.write("")  # small vertical spacer between the summary strip and the cards

    for index, (icon, title, attr_name, _color) in enumerate(_CARD_DEFINITIONS):
        content = getattr(context, attr_name)
        # The first card starts expanded so the user immediately sees
        # content after generating a report; the rest start collapsed
        # to keep the page scannable, since reading all five sections
        # of dense text at once is exactly what Phase 1 set out to fix.
        with st.expander(f"{icon}  {title}", expanded=(index == 0)):
            if content:
                st.markdown(content)
            else:
                st.caption("No content was generated for this section.")
