"""Domain-level user access — wraps database.py."""
from __future__ import annotations
from dataclasses import dataclass
from server.db import database as db
from shared.constants import ELO_DEFAULT


@dataclass
class User:
    user_id: int
    username: str
    password_hash: str
    rating: int


def get(username: str) -> User | None:
    row = db.fetch_user(username)
    return User(row["user_id"], row["username"], row["password_hash"], row["rating"]) if row else None


def create(username: str, password_hash: str) -> User:
    user_id = db.insert_user(username, password_hash)
    return User(user_id, username, password_hash, ELO_DEFAULT)


def update_rating(username: str, rating: int) -> None:
    db.set_rating(username, rating)
