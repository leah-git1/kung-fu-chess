"""SQLite connection and raw CRUD for the users table."""
import sqlite3
import os

_DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                rating        INTEGER NOT NULL DEFAULT 1200
            )
        """)


def insert_user(username: str, password_hash: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )


def fetch_user(username: str) -> sqlite3.Row | None:
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def set_rating(username: str, rating: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE users SET rating = ? WHERE username = ?", (rating, username)
        )
