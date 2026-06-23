"""
database/models.py
-------------------
All database query functions for the users and reports tables.

Design rules followed throughout this file:
- Every function opens its own connection via get_connection() and
  closes it when done. This is safe and simple for SQLite; there is
  no connection-pool overhead worth worrying about at this scale.
- All SQL uses parameterised queries (?  placeholders) — never
  string formatting. This is the standard protection against SQL
  injection attacks and is non-negotiable for any code that handles
  user-supplied input like email addresses or company names.
- Functions return plain Python dicts or None, not sqlite3.Row
  objects, so callers don't need to know anything about the database
  layer's internals.
"""

from datetime import datetime, timezone
from typing import Optional

from database.db import get_connection


# ── helpers ────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row) -> Optional[dict]:
    """Convert a sqlite3.Row to a plain dict, or return None."""
    return dict(row) if row else None


# ── user queries ────────────────────────────────────────────────────

def create_user(name: str, email: str, password_hash: str) -> Optional[dict]:
    """
    Insert a new user row and return it as a dict.

    Parameters
    ----------
    name : str
        The user's full name.
    email : str
        The user's email address (must be unique).
    password_hash : str
        The bcrypt hash of the user's password — never the
        plaintext password itself.

    Returns
    -------
    dict or None
        The newly created user row, or None if the insert failed
        (e.g. because the email already exists).
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (name.strip(), email.strip().lower(), password_hash, _now_iso()),
            )
            conn.commit()
            return get_user_by_id(cursor.lastrowid)
    except Exception:
        return None


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Fetch one user row by email address.

    Parameters
    ----------
    email : str
        Email is stored in lowercase; this function lowercases the
        input before querying so lookups are case-insensitive.

    Returns
    -------
    dict or None
        The user row as a plain dict, or None if not found.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Fetch one user row by primary key.

    Returns
    -------
    dict or None
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_dict(row)


def email_exists(email: str) -> bool:
    """
    Return True if the given email address is already registered.
    Used during signup validation before attempting an insert.
    """
    return get_user_by_email(email) is not None


# ── report queries ──────────────────────────────────────────────────

def save_report(user_id: int, company_name: str, overview: str,
                key_info: str, challenges: str,
                ai_opportunities: str, ceo_pitch: str) -> Optional[dict]:
    """
    Insert a new report row for the given user.

    Parameters
    ----------
    user_id : int
        The id of the authenticated user who generated this report.
    company_name : str
        The company that was researched.
    overview, key_info, challenges, ai_opportunities, ceo_pitch : str
        The five output sections produced by the agent pipeline.

    Returns
    -------
    dict or None
        The newly created report row, or None if the insert failed.
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO reports "
                "(user_id, company_name, overview, key_info, challenges, "
                " ai_opportunities, ceo_pitch, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, company_name.strip(), overview, key_info,
                 challenges, ai_opportunities, ceo_pitch, _now_iso()),
            )
            conn.commit()
            return get_report_by_id(cursor.lastrowid)
    except Exception:
        return None


def get_reports_for_user(user_id: int) -> list:
    """
    Fetch all reports belonging to the given user, newest first.

    IMPORTANT — Phase 6 requirement: this query always filters by
    user_id, so User A's reports are never visible to User B.

    Returns
    -------
    list of dict
        Every report row as a plain dict, ordered by created_at DESC.
        Returns an empty list if the user has no reports yet.
    """
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_report_by_id(report_id: int) -> Optional[dict]:
    """
    Fetch one report row by primary key.

    Returns
    -------
    dict or None
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    return _row_to_dict(row)


def delete_report(report_id: int, user_id: int) -> bool:
    """
    Delete a report only if it belongs to the given user.

    The user_id check in the WHERE clause is the critical security
    control here — it ensures User A cannot delete User B's reports
    even if they somehow know a report's id.

    Returns
    -------
    bool
        True if exactly one row was deleted, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        )
        conn.commit()
    return cursor.rowcount == 1
