"""Handles LOGIN / REGISTER on a raw websocket before the player enters matchmaking."""
from __future__ import annotations
import json
from shared.messages import LoginOkMsg, LoginFailMsg, parse
from server.auth import auth_service


async def authenticate(websocket) -> tuple[str, int] | None:
    """
    Reads LoginMsg messages until authentication succeeds.
    msg.register=True  → register a new account
    msg.register=False → login to an existing account
    Returns (username, rating) on success, None if the socket closes.
    """
    async for raw in websocket:
        try:
            msg = parse(json.loads(raw))
        except Exception:
            continue

        if msg.__class__.__name__ != "LoginMsg":
            continue

        try:
            user = auth_service.register(msg.name, msg.password) if msg.register \
                else auth_service.login(msg.name, msg.password)
            await websocket.send(json.dumps(LoginOkMsg(name=user.username, elo=user.rating).to_json()))
            return user.username, user.rating
        except ValueError as e:
            await websocket.send(json.dumps(LoginFailMsg(reason=str(e)).to_json()))
