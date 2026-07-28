"""
WS handshake — validates the session token issued by the API Gateway.

The client sends a single TokenMsg: { type: "token", token: "...", username: "...", rating: N }
The server checks Redis for session:{token} == username, then deletes it (single-use).
"""
from __future__ import annotations
import json
import os
import redis
from server.logging.server_logger import log


def _redis() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


async def authenticate(websocket) -> tuple[str, int] | None:
    try:
        raw = await websocket.recv()
        d   = json.loads(raw)
    except Exception:
        return None

    if d.get("type") != "token":
        return None

    token    = d.get("token", "")
    username = d.get("username", "")
    rating   = int(d.get("rating", 1200))

    r = _redis()
    stored = r.get(f"session:{token}")
    if stored != username:
        log(f"invalid token for '{username}'", level="warning")
        await websocket.send(json.dumps({"type": "login_fail", "reason": "invalid or expired token"}))
        return None

    r.delete(f"session:{token}")  # single-use
    log(f"token ok: {username} (ELO {rating})")
    return username, rating
