"""
auth/login.py
--------------
Renders the login page: email + password form with a link to the
signup page. On successful login, writes the user into session state
and triggers a rerun so app.py redirects to the dashboard.
"""

import streamlit as st

from auth.auth_utils import login_user, verify_password
from database.models import get_user_by_email


def render_login_page(on_go_to_signup) -> None:
    """
    Render the full login page.

    Parameters
    ----------
    on_go_to_signup : callable
        A zero-argument function that app.py passes in; calling it
        switches the visible page to signup. Using a callback instead
        of importing app.py directly avoids a circular import.
    """
    # Centre the form on the page using Streamlit's column layout.
    _, col, _ = st.columns([1, 2, 1])

    with col:
        st.markdown("## 🔎 AI Research Agent")
        st.markdown("### Welcome back")
        st.caption("Log in to access your research dashboard.")
        st.write("")

        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Your password",
            key="login_password",
        )
        st.write("")

        login_clicked = st.button(
            "Log in",
            type="primary",
            use_container_width=True,
        )

        if login_clicked:
            _handle_login(email, password)

        st.divider()
        st.caption("Don't have an account?")
        if st.button("Create an account →", use_container_width=True):
            on_go_to_signup()


def _handle_login(email: str, password: str) -> None:
    """
    Validate the login form, check credentials against the database,
    and either log the user in or show an error message.

    Parameters
    ----------
    email : str
        The email address the user typed.
    password : str
        The plaintext password the user typed (never stored).
    """
    # ── Input validation ─────────────────────────────────────────
    if not email.strip():
        st.warning("Please enter your email address.")
        return
    if not password:
        st.warning("Please enter your password.")
        return

    # ── Database lookup ──────────────────────────────────────────
    user = get_user_by_email(email)

    # We deliberately give the same vague error whether the email
    # doesn't exist OR the password is wrong. This is a security
    # best practice — telling attackers "that email isn't registered"
    # would let them enumerate valid accounts.
    if user is None or not verify_password(password, user["password_hash"]):
        st.error("Incorrect email or password. Please try again.")
        return

    # ── Success ──────────────────────────────────────────────────
    login_user(user)
    st.success(f"Welcome back, {user['name']}!")
    st.rerun()
