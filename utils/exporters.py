"""
utils/exporters.py
--------------------
Converts a completed ResearchContext into downloadable file formats:
plain Markdown and PDF. This module has no Streamlit code in it at
all — it's pure data transformation, which means it can be tested
(and was tested, see the project notes) without ever needing a
running Streamlit server.
"""

import re
from io import BytesIO
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from core.context import ResearchContext

# The five sections in display order, as (display title, attribute
# name) pairs. Both the Markdown and PDF builders below loop over
# this same list, so the two export formats can never accidentally
# drift out of sync with each other or with the card UI's own
# ordering in ui/report_cards.py.
_SECTIONS = [
    ("Company Overview", "overview"),
    ("Key Business Information", "key_info"),
    ("Potential Business Challenges", "challenges"),
    ("AI Opportunities", "ai_opportunities"),
    ("Personalized CEO Pitch", "ceo_pitch"),
]

_BOLD_MARKDOWN_PATTERN = re.compile(r"\*\*(.+?)\*\*")


def build_markdown_report(context: ResearchContext) -> str:
    """
    Combine every section of a completed ResearchContext into one
    plain Markdown document.

    Parameters
    ----------
    context : ResearchContext
        The completed pipeline output to format.

    Returns
    -------
    str
        A single Markdown string containing all five report sections,
        ready to be offered as a .md download.
    """
    lines = [f"# Research Report: {context.company_name}", ""]
    for title, attr_name in _SECTIONS:
        content = getattr(context, attr_name) or "_No content was generated for this section._"
        lines.append(f"## {title}")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def _markdown_inline_to_reportlab(text: str) -> str:
    """
    Convert the one inline markdown construct our prompts actually
    produce — **bold** — into ReportLab's own markup tags.

    Parameters
    ----------
    text : str
        A single line of markdown-ish text.

    Returns
    -------
    str
        The same text with **bold** replaced by <b>bold</b>.
    """
    return _BOLD_MARKDOWN_PATTERN.sub(r"<b>\1</b>", text)


def _markdown_block_to_flowables(text: str, styles) -> List:
    """
    Convert one report section's markdown-ish text into a list of
    ReportLab flowables (Paragraph and Spacer objects) that can be
    added to a PDF's story.

    This is a small, purpose-built converter for the specific
    markdown patterns our Groq prompts are instructed to produce —
    "## " headers, "- " bullet lists, and **bold** emphasis — not a
    general-purpose markdown parser. If the report content ever needs
    richer formatting (tables, nested lists), a dedicated library
    like `markdown` plus `xhtml2pdf` would be a better fit, at the
    cost of extra dependencies this project doesn't need yet.

    Parameters
    ----------
    text : str
        One section's raw text, as produced by an agent.
    styles : reportlab.lib.styles.StyleSheet1
        The ReportLab stylesheet to pull paragraph styles from.

    Returns
    -------
    List
        A list of ReportLab flowables ready to append to a PDF story.
    """
    flowables: List = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("## "):
            flowables.append(Paragraph(_markdown_inline_to_reportlab(line[3:]), styles["Heading2"]))
        elif line.startswith("- ") or line.startswith("* "):
            bullet_text = _markdown_inline_to_reportlab(line[2:])
            flowables.append(Paragraph(f"• {bullet_text}", styles["BodyText"]))
        else:
            flowables.append(Paragraph(_markdown_inline_to_reportlab(line), styles["BodyText"]))

        flowables.append(Spacer(1, 4))

    return flowables


def build_pdf_report(context: ResearchContext) -> bytes:
    """
    Render a completed ResearchContext as a PDF document.

    Parameters
    ----------
    context : ResearchContext
        The completed pipeline output to format.

    Returns
    -------
    bytes
        The raw PDF file bytes, ready to be offered as a .pdf
        download via st.download_button.
    """
    # SimpleDocTemplate can write to an in-memory buffer just as
    # easily as to a real file path, which is exactly what we want
    # here — this PDF only needs to exist long enough to be handed to
    # the browser, never saved to disk on the server side.
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=f"Research Report - {context.company_name}",
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()

    story: List = [
        Paragraph(f"Research Report: {context.company_name}", styles["Title"]),
        Spacer(1, 16),
    ]

    for title, attr_name in _SECTIONS:
        content = getattr(context, attr_name)
        story.append(Paragraph(title, styles["Heading1"]))
        story.append(Spacer(1, 6))
        if content:
            story.extend(_markdown_block_to_flowables(content, styles))
        else:
            story.append(Paragraph("No content was generated for this section.", styles["Italic"]))
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
