"""
ui/sidebar.py
---------------
Renders the application's sidebar: a logo/brand header, a "New
Report" button that resets the workspace, and the list of reports
generated this session ("history"), each one clickable to reload it
into the main view.

The history shown here is currently backed by st.session_state only
(see app.py's report_history key) — it will be swapped for a real,
per-user database query once the database and authentication phases
land. The render_sidebar() function signature and its call site in
app.py are designed to stay the same when that happens; only the
internals of _render_history() will change.
"""

import streamlit as st


def _render_logo() -> None:
    """Render the small brand header at the top of the sidebar."""
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.5rem; padding-bottom:0.25rem;">
            <span style="font-size:1.6rem;">🔎</span>
            <span style="font-size:1.25rem; font-weight:700;">AI Research Agent</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Company research & AI opportunity pitches")


def _render_new_report_button() -> None:
    """
    Render the "New Report" button.

    Sets two flags and reruns — app.py reads both flags BEFORE any
    widget is created on the next run:

    _archive_and_clear  → app.py archives the active report (if any)
                          to history, then clears report_context.
    _clear_input        → app.py resets the text input widget value.

    We cannot call _archive_current_report() from here directly
    (that would require importing from app.py, creating a circular
    import), and we cannot write to the widget key
    company_name_input here because the widget may already have been
    rendered earlier this run (StreamlitAPIException). Flags fix both.
    """
    if st.button("🆕  New Report", use_container_width=True, type="primary"):
        st.session_state._archive_and_clear = True
        st.session_state._clear_input = True
        st.rerun()


def _render_history() -> None:
    """
    Render the report history list, most recent first. Each row has
    two buttons side-by-side — a load button (company name) and a
    small red delete button (🗑) — matching the ChatGPT pattern where
    each history item has an inline delete control.

    Deletion works by rebuilding report_history without the selected
    entry and rerunning. Because we're iterating over a reversed copy
    of the list, the real index into the original list is calculated
    as: real_index = (len(history) - 1) - reversed_index.

    If the entry being deleted is the one currently on screen,
    report_context is also cleared so the user isn't left looking at
    a report that no longer exists in history.
    """
    history = st.session_state.get("report_history", [])
    st.subheader(f"Report history ({len(history)})")

    if not history:
        st.caption("No reports generated yet this session.")
        return

    for reversed_index, entry in enumerate(reversed(history)):
        # The real position in the original (oldest-first) list:
        real_index = (len(history) - 1) - reversed_index
        timestamp = entry["generated_at"].strftime("%H:%M")

        # Two columns: wide one for the company name (load button),
        # narrow one for the delete button — same visual rhythm as
        # ChatGPT's sidebar history rows.
        col_name, col_del = st.columns([5, 1])

        with col_name:
            if st.button(
                f"📄 {entry['company_name']}  ·  {timestamp}",
                key=f"history_load_{real_index}",
                use_container_width=True,
            ):
                # Load this report back onto the main screen.
                st.session_state.report_context = entry["context"]
                st.rerun()

        with col_del:
            if st.button(
                "🗑",
                key=f"history_delete_{real_index}",
                help=f"Delete '{entry['company_name']}' from history",
                type="secondary",
            ):
                # If the entry being deleted is the one currently
                # displayed, clear the main screen too — otherwise
                # the user would see a report with no matching
                # history entry, which is confusing.
                current = st.session_state.get("report_context")
                if current is not None and current is entry["context"]:
                    st.session_state.report_context = None
                    st.session_state._clear_input = True

                # Rebuild the list without this entry and rerun.
                st.session_state.report_history = [
                    e for i, e in enumerate(history) if i != real_index
                ]
                st.rerun()


def render_sidebar(model_name: str) -> None:
    """
    Render the complete sidebar: logo, New Report button, and history.

    Parameters
    ----------
    model_name : str
        The Groq model name currently configured, shown as a small
        caption at the bottom of the sidebar.
    """
    with st.sidebar:
        _render_logo()
        st.divider()
        _render_new_report_button()
        st.divider()
        _render_history()
        st.divider()
        st.caption(f"Model: {model_name} (via Groq)")
