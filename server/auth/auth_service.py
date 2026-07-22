"""Login and registration logic."""
from __future__ import annotations
import sqlite3
import bcrypt
from server.db import user_repository as repo
from server.db.user_repository import User
from server.errors import AuthError, DatabaseError


def register(username: str, password: str) -> User:
    if repo.get(username) is not None:
        raise AuthError("username already taken")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        return repo.create(username, hashed)
    except sqlite3.IntegrityError:
        raise AuthError("username already taken")
    except sqlite3.Error as e:
        raise DatabaseError(f"could not create user: {e}") from e


def login(username: str, password: str) -> User:
    try:
        user = repo.get(username)
    except sqlite3.Error as e:
        raise DatabaseError(f"could not fetch user: {e}") from e
    if user is None or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise AuthError("invalid credentials")
    return user
