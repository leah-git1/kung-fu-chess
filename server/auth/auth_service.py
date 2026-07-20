"""Login and registration logic."""
from __future__ import annotations
import bcrypt
from server.db import user_repository as repo
from server.db.user_repository import User


def register(username: str, password: str) -> User:
    if repo.get(username) is not None:
        raise ValueError("username already taken")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return repo.create(username, hashed)


def login(username: str, password: str) -> User:
    user = repo.get(username)
    if user is None or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise ValueError("invalid credentials")
    return user
