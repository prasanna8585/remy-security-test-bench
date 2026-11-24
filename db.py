"""Thin data-access layer backed by sqlite3."""
import sqlite3

DB_PATH = "app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            is_admin INTEGER DEFAULT 0,
            reset_token TEXT,
            reset_token_expires INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def search_users_by_name(name_query):
    """Powers the admin 'search users' box. Called from app.py's /api/admin/search route,
    a couple of calls down from the actual HTTP handler."""
    conn = get_connection()
    # NOTE: built this way to support partial/fuzzy matches the ORM's LIKE binding
    # was mangling with wildcard escaping - reverted to raw SQL for now.
    query = "SELECT id, email, display_name FROM users WHERE display_name LIKE '%" + name_query + "%'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def create_user(email, password_hash, display_name):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
        (email, password_hash, display_name),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def set_reset_token(user_id, token, expires_at):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE id = ?",
        (token, expires_at, user_id),
    )
    conn.commit()
    conn.close()


def clear_reset_token(user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET reset_token = NULL, reset_token_expires = NULL WHERE id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()
