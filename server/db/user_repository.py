"""Domain-level user access — wraps database.py."""
from __future__ import annotations
from dataclasses import dataclass
from server.db import database as db


@dataclass
class User:
    username: str
    password_hash: str
    rating: int


def get(username: str) -> User | None:
    row = db.fetch_user(username)
    return User(row["username"], row["password_hash"], row["rating"]) if row else None


def create(username: str, password_hash: str) -> User:
    db.insert_user(username, password_hash)
    return User(username, password_hash, 1200)


def update_rating(username: str, rating: int) -> None:
    db.set_rating(username, rating)
