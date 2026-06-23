"""
database/db.py
---------------
SQLite connection management and schema creation.

Why SQLite?
- Zero configuration: no separate database server to install or run.
  The entire database lives in one file (app.db) in the project root,
  making setup as simple as running the app.
- Built into Python's standard library (sqlite3), so no extra package
  to install.
- Perfectly adequate for a single-user or small-team tool like this.
  If the project ever needed to scale to many concurrent users, the
  database layer is isolated here — swapping SQLite for PostgreSQL
  would mean rewriting this file and models.py only.

Schema (two tables):

    users
    ------
    id            INTEGER  PRIMARY KEY AUTOINCREMENT
    name          TEXT     NOT NULL
    email         TEXT     UNIQUE NOT NULL
    password_hash TEXT     NOT NULL      ← bcrypt hash, never plaintext
    created_at    TEXT     NOT NULL      ← ISO-8601 timestamp string

    reports
    --------
    id               INTEGER  PRIMARY KEY AUTOINCREMENT
    user_id          INTEGER  NOT NULL  REFERENCES users(id)
    company_name     TEXT     NOT NULL
    overview         TEXT
    key_info         TEXT
    challenges       TEXT
    ai_opportunities TEXT
    ceo_pitch        TEXT
    created_at       TEXT     NOT NULL

One User → Many Reports enforced by the user_id foreign key.
"""

import sqlite3
from pathlib import Path

# The database file lives in the project root (same folder as app.py).
# Using an absolute path derived from this file's location means the
# database is always found regardless of which directory the user runs
# `streamlit run` from.
DB_PATH = Path(__file__).parent.parent / "app.db"

# SQL that creates both tables if they do not already exist.
# "IF NOT EXISTS" means this is safe to call every time the app starts
# without wiping existing data.
_CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);
"""

_CREATE_REPORTS_TABLE = """
CREATE TABLE IF NOT EXISTS reports (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    company_name     TEXT    NOT NULL,
    overview         TEXT    DEFAULT '',
    key_info         TEXT    DEFAULT '',
    challenges       TEXT    DEFAULT '',
    ai_opportunities TEXT    DEFAULT '',
    ceo_pitch        TEXT    DEFAULT '',
    created_at       TEXT    NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    """
    Open and return a connection to the SQLite database.

    check_same_thread=False is required for Streamlit because
    Streamlit runs each user session in its own thread, and SQLite's
    default setting would reject connections created on a different
    thread than the one that opened them.

    Every caller is responsible for closing the connection when done,
    or — better — using it as a context manager (with get_connection()
    as conn: ...) so it closes automatically even if an exception
    is raised mid-query.

    Returns
    -------
    sqlite3.Connection
        An open connection to app.db, with row_factory set to
        sqlite3.Row so query results can be accessed by column name
        (result["email"]) instead of just by index (result[2]).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the database tables if they don't already exist.

    Called once at app startup (in app.py's main(), before any
    rendering happens). Safe to call repeatedly — IF NOT EXISTS
    guarantees it never drops or modifies data that's already there.
    """
    with get_connection() as conn:
        conn.execute(_CREATE_USERS_TABLE)
        conn.execute(_CREATE_REPORTS_TABLE)
        conn.commit()
