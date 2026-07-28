"""Handles LOGIN / REGISTER — delegates to the auth-service over HTTP."""
from __future__ import annotations
import json
import os
import httpx
from shared.messages import LoginOkMsg, LoginFailMsg, parse, LoginMsg
from server.logging.server_logger import log

_AUTH_URL = f"http://{os.getenv('AUTH_HOST', 'localhost')}:{os.getenv('AUTH_PORT', '8000')}"


async def authenticate(websocket) -> tuple[str, int] | None:
    async for raw in websocket:
        try:
            msg = parse(json.loads(raw))
        except (json.JSONDecodeError, ValueError):
            continue

        if not isinstance(msg, LoginMsg):
            continue

        endpoint = "/register" if msg.register else "/login"
        try:
            resp = httpx.post(
                f"{_AUTH_URL}{endpoint}",
                json={"username": msg.name, "password": msg.password},
                timeout=5.0,
            )
        except httpx.RequestError as e:
            log(f"auth service unreachable: {e}", level="error")
            return None

        if resp.status_code == 200:
            data = resp.json()
            log(f"auth ok: {data['username']} (ELO {data['rating']}) "
                f"{'registered' if msg.register else 'logged in'}")
            await websocket.send(json.dumps(
                LoginOkMsg(name=data["username"], elo=data["rating"]).to_json()
            ))
            return data["username"], data["rating"]
        else:
            reason = resp.json().get("error", "auth failed")
            log(f"auth failed for '{msg.name}': {reason}", level="warning")
            await websocket.send(json.dumps(LoginFailMsg(reason=reason).to_json()))
