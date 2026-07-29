"""PostgreSQL connection and raw CRUD for the users table."""
import os
import psycopg2
import psycopg2.extras
from shared.constants import ELO_DEFAULT

_DSN = os.environ["DATABASE_URL"]


def _connect() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(_DSN)
    conn.autocommit = False
    return conn


def init_db() -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(1)")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id       SERIAL PRIMARY KEY,
                    username      TEXT   NOT NULL UNIQUE,
                    password_hash TEXT   NOT NULL,
                    rating        INTEGER NOT NULL DEFAULT {ELO_DEFAULT}
                )
            """)
        conn.commit()


def insert_user(username: str, password_hash: str) -> int:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id",
                (username, password_hash),
            )
            user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def fetch_user(username: str) -> dict | None:
    with _connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cur.fetchone()


def set_rating(username: str, rating: int) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET rating = %s WHERE username = %s", (rating, username)
            )
        conn.commit()
