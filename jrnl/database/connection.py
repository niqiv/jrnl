"""Database connection and initialization."""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path.home() / '.jrnl' / 'jrnl.db'


def init_database():
    """Initialize the database with schema."""
    from .sql_statements import CREATE_LOGS_TABLE, CREATE_DAILIES_TABLE

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript(CREATE_LOGS_TABLE)
    cursor.executescript(CREATE_DAILIES_TABLE)

    conn.commit()
    conn.close()


@contextmanager
def get_connection():
    """Get database connection context manager."""
    # Auto-initialize database on first access
    if not DB_PATH.exists():
        init_database()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        import sys
        print(f"Database error: {e}", file=sys.stderr)
        raise
    except Exception as e:
        conn.rollback()
        import sys
        print(f"Unexpected database operation error: {type(e).__name__}: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()
