"""
auth/auth_utils.py
--------------------
Password hashing with bcrypt, and session-state helpers that track
whether a user is currently logged in.

Why bcrypt?
- bcrypt is deliberately slow (it runs thousands of rounds of hashing)
  which makes brute-force attacks impractically expensive, even if an
  attacker somehow obtained the raw database file.
- It automatically generates and embeds a random "salt" into every
  hash, so two users with the same password still produce completely
  different hashes — meaning a pre-computed rainbow-table attack
  doesn't work.
- It is the industry-standard choice for password storage and is
  exactly what your Phase 4 spec asks for.

Session state keys owned by this module:
    user_id     int   — the logged-in user's database id, or None
    user_name   str   — the logged-in user's display name, or ""
    user_email  str   — the logged-in user's email address, or ""
"""

import bcrypt
import streamlit as st


# ── password helpers ────────────────────────────────────────────────

def hash_password(plaintext: str) -> str:
    """
    Hash a plaintext password with bcrypt and return the hash as a
    UTF-8 string suitable for storing in the database.

    Parameters
    ----------
    plaintext : str
        The raw password the user typed. Never stored.

    Returns
    -------
    str
        A bcrypt hash string, e.g.
        "$2b$12$...52 characters...".
        Always 60 characters long, regardless of the input length.
    """
    # bcrypt.gensalt() creates a random salt and encodes the work
    # factor (rounds=12 here). Higher rounds = slower hashing =
    # harder for attackers, but also slightly slower for users at
    # login. 12 is the widely recommended default (takes ~0.3s on
    # modern hardware).
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
    # bcrypt returns bytes; we store as a UTF-8 string in SQLite.
    return hashed_bytes.decode("utf-8")


def verify_password(plaintext: str, stored_hash: str) -> bool:
    """
    Check whether a plaintext password matches a stored bcrypt hash.

    Parameters
    ----------
    plaintext : str
        The raw password the user just typed into the login form.
    stored_hash : str
        The bcrypt hash string retrieved from the database.

    Returns
    -------
    bool
        True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )
    except Exception:
        # bcrypt.checkpw raises if stored_hash is not a valid bcrypt
        # string. Returning False (rather than propagating the
        # exception) ensures a corrupted hash row in the DB produces
        # a "wrong password" result rather than a server error.
        return False


# ── session state helpers ────────────────────────────────────────────

def init_auth_state() -> None:
    """
    Initialise the authentication-related session state keys if they
    don't already exist. Called once at app startup, before any page
    renders — safe to call multiple times (idempotent).
    """
    auth_defaults = {
        "user_id": None,
        "user_name": "",
        "user_email": "",
    }
    for key, value in auth_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(user: dict) -> None:
    """
    Write the authenticated user's details into session state,
    marking them as logged in for the rest of this browser session.

    Parameters
    ----------
    user : dict
        A user row dict as returned by database.models.get_user_by_email.
        Must contain 'id', 'name', and 'email' keys.
    """
    st.session_state.user_id = user["id"]
    st.session_state.user_name = user["name"]
    st.session_state.user_email = user["email"]


def logout_user() -> None:
    """
    Clear all authentication and report state from session, logging
    the user out. After this, is_logged_in() returns False and the
    app will redirect to the login page on the next rerun.
    """
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    # Also clear any in-progress report so the next user who logs in
    # on this browser doesn't briefly see the previous user's data.
    st.session_state.report_context = None
    st.session_state.report_history = []


def is_logged_in() -> bool:
    """
    Return True if a user is currently authenticated in this session.

    Used by app.py to decide whether to show the login page or the
    main dashboard.
    """
    return st.session_state.get("user_id") is not None


def current_user_id() -> int:
    """
    Return the logged-in user's database id.

    Should only be called after confirming is_logged_in() is True.
    """
    return st.session_state.user_id


def current_user_name() -> str:
    """Return the logged-in user's display name."""
    return st.session_state.get("user_name", "")
