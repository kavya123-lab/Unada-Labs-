"""
app.py
-------
Streamlit entry point for the AI-Powered Research & Recommendation Agent.

Phase changes reflected here:
  Phase 1 — card-based report UI          (ui/report_cards.py)
  Phase 2 — PDF + Markdown download,       auto-clear to history
  Phase 3 — professional sidebar          (ui/sidebar.py)
  Phase 4 — email/password authentication (auth/)
  Phase 5 — SQLite persistence            (database/)

App flow (Phase 8 specification):
  Unauthenticated → Login/Signup page
  Authenticated   → Dashboard (generate reports, view history)

Run with: streamlit run app.py
"""

from datetime import datetime

import streamlit as st

try:
    import config
except Exception as exc:
    st.set_page_config(page_title="Configuration Error", page_icon="⚠️")
    st.title("⚠️ Configuration Error")
    st.error(str(exc))
    st.info(
        "Copy `.env.example` to `.env` in your project folder, add "
        "your real GROQ_API_KEY and TAVILY_API_KEY values, then "
        "restart the app with `streamlit run app.py`."
    )
    st.stop()

from auth.auth_utils import (
    current_user_id,
    current_user_name,
    init_auth_state,
    is_logged_in,
    logout_user,
)
from auth.login import render_login_page
from auth.signup import render_signup_page
from core.context import ResearchContext
from core.orchestrator import ResearchOrchestrator
from database.db import init_db
from database.models import get_reports_for_user, save_report
from ui.report_cards import inject_dashboard_styles, render_report_cards
from ui.sidebar import render_sidebar
from utils.exceptions import ResearchAgentError
from utils.exporters import build_markdown_report, build_pdf_report
from utils.logger import get_logger

logger = get_logger(__name__)


# ── Session state ────────────────────────────────────────────────────

def _init_session_state() -> None:
    """Initialise every session_state key the app uses."""
    defaults = {
        # Report state
        "report_context": None,
        "report_history": [],
        "company_name_input": "",
        # Navigation flags
        "_clear_input": False,
        "_archive_and_clear": False,
        # Auth page toggle (login vs signup)
        "auth_page": "login",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Archive / clear helpers ──────────────────────────────────────────

def _archive_current_report() -> None:
    """
    Archive the active report to session history AND the database
    (if the user is logged in), then clear the screen.
    """
    context = st.session_state.report_context
    if context is not None:
        # Always save to in-session history for the sidebar.
        st.session_state.report_history.append(
            {
                "company_name": context.company_name,
                "generated_at": datetime.now(),
                "context": context,
            }
        )
        # Also persist to the database so it survives page refreshes
        # and future logins (Phase 5 requirement).
        if is_logged_in():
            save_report(
                user_id=current_user_id(),
                company_name=context.company_name,
                overview=context.overview,
                key_info=context.key_info,
                challenges=context.challenges,
                ai_opportunities=context.ai_opportunities,
                ceo_pitch=context.ceo_pitch,
            )

    st.session_state.report_context = None
    st.session_state._clear_input = True
    st.rerun()


# ── Auth pages ───────────────────────────────────────────────────────

def _show_auth_pages() -> None:
    """
    Show either the login or the signup page based on the auth_page
    flag in session state. Each page receives a callback to switch
    to the other page, avoiding any circular import between login.py
    and signup.py.
    """
    st.set_page_config(
        page_title="AI Research Agent — Sign In",
        page_icon="🔎",
        layout="centered",
    )
    if st.session_state.auth_page == "signup":
        render_signup_page(
            on_go_to_login=lambda: _switch_auth_page("login")
        )
    else:
        render_login_page(
            on_go_to_signup=lambda: _switch_auth_page("signup")
        )


def _switch_auth_page(page: str) -> None:
    """Toggle between 'login' and 'signup' auth pages."""
    st.session_state.auth_page = page
    st.rerun()


# ── Dashboard (authenticated users only) ─────────────────────────────

def _load_db_history_into_session() -> None:
    """
    On first login, pull the user's past reports from the database
    into st.session_state.report_history so they appear in the sidebar
    immediately — without the user needing to regenerate anything.

    Only runs when report_history is empty (i.e. fresh login), so it
    doesn't re-add entries the user already has in their sidebar.
    """
    if st.session_state.report_history:
        return   # already populated this session

    db_reports = get_reports_for_user(current_user_id())
    for row in reversed(db_reports):   # reversed → oldest first in list
        # Reconstruct a ResearchContext from the saved database fields
        # so clicking a history entry loads the full report correctly.
        context = ResearchContext(
            company_name=row["company_name"],
            overview=row["overview"] or "",
            key_info=row["key_info"] or "",
            challenges=row["challenges"] or "",
            ai_opportunities=row["ai_opportunities"] or "",
            ceo_pitch=row["ceo_pitch"] or "",
        )
        st.session_state.report_history.append(
            {
                "company_name": row["company_name"],
                "generated_at": datetime.fromisoformat(row["created_at"]),
                "context": context,
                "db_id": row["id"],   # kept for future delete-from-db support
            }
        )


def _show_dashboard() -> None:
    """Render the full authenticated dashboard."""
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="🔎",
        layout="centered",
    )
    inject_dashboard_styles()

    # ── Consume navigation flags before any widget renders ───────
    if st.session_state._archive_and_clear:
        st.session_state._archive_and_clear = False
        _archive_current_report()
        return   # _archive_current_report calls st.rerun()

    if st.session_state._clear_input:
        st.session_state.company_name_input = ""
        st.session_state._clear_input = False

    # ── Load DB history on first login ───────────────────────────
    _load_db_history_into_session()

    # ── Sidebar ───────────────────────────────────────────────────
    render_sidebar(model_name=config.GROQ_MODEL_NAME)

    # Logout button at the very bottom of the sidebar
    with st.sidebar:
        st.divider()
        col_name, col_logout = st.columns([3, 1])
        col_name.caption(f"👤 {current_user_name()}")
        if col_logout.button("Log out", use_container_width=True):
            logout_user()
            st.rerun()

    # ── Main content ──────────────────────────────────────────────
    st.title(config.APP_TITLE)
    st.caption(
        "Enter a company name to generate an AI-powered research "
        "brief and a personalized outreach pitch, using live web "
        "search and Groq."
    )

    company_name = st.text_input(
        label="Company name",
        placeholder="e.g. Tesla, Notion, Zerodha",
        key="company_name_input",
    )
    generate_clicked = st.button("⚡  Generate Report", type="primary")

    if generate_clicked:
        if not company_name.strip():
            st.warning("Please enter a company name before generating a report.")
        else:
            try:
                orchestrator = ResearchOrchestrator()
                with st.spinner(
                    f"Researching **{company_name}**… this usually takes 30-60 seconds."
                ):
                    st.session_state.report_context = orchestrator.run(company_name)
            except ResearchAgentError as exc:
                logger.error(f"Pipeline error: {exc}")
                st.error(f"Something went wrong:\n\n{exc}")
            except ValueError as exc:
                st.warning(str(exc))

    # ── Report + download buttons ─────────────────────────────────
    if st.session_state.report_context is not None:
        render_report_cards(st.session_state.report_context)

        st.write("")
        st.markdown("---")
        st.markdown("##### Download & save report")

        col_md, col_pdf, col_new = st.columns([2, 2, 1])
        with col_md:
            md_clicked = st.download_button(
                label="📄 Markdown",
                data=build_markdown_report(st.session_state.report_context),
                file_name=f"{st.session_state.report_context.company_name}_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_pdf:
            pdf_clicked = st.download_button(
                label="📑 PDF",
                data=build_pdf_report(st.session_state.report_context),
                file_name=f"{st.session_state.report_context.company_name}_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with col_new:
            if st.button("🆕 New", use_container_width=True):
                _archive_current_report()

        if md_clicked or pdf_clicked:
            _archive_current_report()


# ── Entry point ──────────────────────────────────────────────────────

def main() -> None:
    """
    Initialise the database and session state, then route to either
    the auth pages or the main dashboard based on login status.
    """
    # Create the SQLite tables if this is the first ever run.
    # init_db() is safe to call on every startup — it's idempotent.
    init_db()

    _init_session_state()
    init_auth_state()

    if is_logged_in():
        _show_dashboard()
    else:
        _show_auth_pages()


if __name__ == "__main__":
    main()
