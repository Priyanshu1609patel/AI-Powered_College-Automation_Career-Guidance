"""
Database layer using psycopg2 for direct PostgreSQL access to Supabase.
Provides get_db() for connection management in Flask request context.
"""
import psycopg2
import psycopg2.extras
from config import DATABASE_URL


def get_db():
    """Return a new database connection with dict-cursor support."""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn.autocommit = False
    return conn


def query_db(sql, params=None, one=False):
    """Execute a read query and return results as list of dicts (or single dict)."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return rows[0] if one and rows else (rows if not one else None)
    finally:
        conn.close()


def execute_db(sql, params=None, returning=False):
    """Execute a write query (INSERT/UPDATE/DELETE). Returns rows if RETURNING clause used."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            result = None
            if returning:
                result = cur.fetchall()
            conn.commit()
            return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
