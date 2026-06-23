"""
auth/signup.py
---------------
Renders the signup page: full name, email, password, and confirm
password fields with validation. On success, creates the user in the
database, logs them in immediately, and reruns to the dashboard.
"""

import re

import streamlit as st

from auth.auth_utils import hash_password, login_user
from database.models import create_user, email_exists

# Minimum password length enforced both in the error message shown to
# the user and in the validation check, defined once so they can't drift.
MIN_PASSWORD_LENGTH = 8

# Very simple email format check — not a full RFC 5322 parser, just
# enough to catch obvious typos like "user@" or "notanemail".
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def render_signup_page(on_go_to_login) -> None:
    """
    Render the full signup page.

    Parameters
    ----------
    on_go_to_login : callable
        A zero-argument function that switches the visible page back
        to login when the user clicks "Already have an account?".
    """
    _, col, _ = st.columns([1, 2, 1])

    with col:
        st.markdown("## 🔎 AI Research Agent")
        st.markdown("### Create your account")
        st.caption("Free to use. No credit card required.")
        st.write("")

        full_name = st.text_input(
            "Full name",
            placeholder="Ada Lovelace",
            key="signup_name",
        )
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="signup_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder=f"At least {MIN_PASSWORD_LENGTH} characters",
            key="signup_password",
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
            key="signup_confirm",
        )
        st.write("")

        signup_clicked = st.button(
            "Create account",
            type="primary",
            use_container_width=True,
        )

        if signup_clicked:
            _handle_signup(full_name, email, password, confirm_password)

        st.divider()
        st.caption("Already have an account?")
        if st.button("Log in →", use_container_width=True):
            on_go_to_login()


def _validate_signup(name: str, email: str,
                     password: str, confirm: str) -> str:
    """
    Validate all signup fields and return the first error message
    found, or an empty string if everything is valid.

    Returning the first error only (rather than all errors at once)
    keeps the UI clean — one issue fixed at a time.

    Parameters
    ----------
    name, email, password, confirm : str
        The raw values from the four signup form fields.

    Returns
    -------
    str
        An error message to show, or "" if all fields are valid.
    """
    if not name.strip():
        return "Please enter your full name."
    if len(name.strip()) < 2:
        return "Name must be at least 2 characters."
    if not email.strip():
        return "Please enter your email address."
    if not _EMAIL_REGEX.match(email.strip()):
        return "Please enter a valid email address."
    if not password:
        return "Please enter a password."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return "Passwords do not match. Please try again."
    return ""


def _handle_signup(name: str, email: str,
                   password: str, confirm: str) -> None:
    """
    Validate the form, check for duplicate emails, hash the password,
    create the user in the database, and log them in — or show the
    appropriate error message if any step fails.
    """
    # ── Field validation ─────────────────────────────────────────
    error = _validate_signup(name, email, password, confirm)
    if error:
        st.warning(error)
        return

    # ── Duplicate email check ────────────────────────────────────
    if email_exists(email):
        st.error(
            "An account with that email address already exists. "
            "Please log in instead."
        )
        return

    # ── Create the user ──────────────────────────────────────────
    # Hash the password BEFORE passing it to create_user — the
    # database layer never sees or stores the plaintext password.
    password_hash = hash_password(password)
    user = create_user(
        name=name.strip(),
        email=email.strip().lower(),
        password_hash=password_hash,
    )

    if user is None:
        st.error(
            "Something went wrong while creating your account. "
            "Please try again."
        )
        return

    # ── Log in immediately after signup ─────────────────────────
    login_user(user)
    st.success(f"Account created! Welcome, {user['name']} 🎉")
    st.rerun()
