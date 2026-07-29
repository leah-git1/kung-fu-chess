"""
Game Server Shard — runs authoritative GameSession for allocated rooms.

Clients connect here (address resolved from Redis shard:{room_id}) after
the WS Gateway has matched and allocated them.

Each connecting client sends a ShardJoinMsg: { type: "shard_join", room_id, token, color }
The shard validates the token against Redis, then waits for both players before
starting the GameSession.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import redis
import websockets
from websockets.exceptions import ConnectionClosed

from shared.enums import Color
from shared.constants import DEFAULT_SHARD_PORT
from server.session.player_connection import PlayerConnection
from server.session.game_session import GameSession
from server.logging.server_logger import log


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


# room_id → {white_conn, black_conn, event}
_waiting: dict[str, dict] = {}
_waiting_lock = asyncio.Lock()


async def _on_connect(websocket) -> None:
    try:
        raw = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        d   = json.loads(raw)
    except Exception:
        return

    if d.get("type") != "shard_join":
        return

    room_id = d.get("room_id", "").upper()
    token   = d.get("token", "")
    color   = d.get("color", "")

    # validate token
    r = _r()
    stored = r.get(f"session:{token}")
    if not stored:
        await websocket.send(json.dumps({"type": "error", "reason": "invalid token"}))
        return
    r.delete(f"session:{token}")

    # validate room exists
    shard_raw = r.get(f"shard:{room_id}")
    if not shard_raw:
        await websocket.send(json.dumps({"type": "error", "reason": "room not found"}))
        return

    shard_info = json.loads(shard_raw)
    conn_color = Color.WHITE if color == Color.WHITE.value else Color.BLACK
    conn = PlayerConnection(websocket, color=conn_color, name=stored, rating=1200)

    log(f"shard: {stored} joined room {room_id} as {conn_color.name}")

    async with _waiting_lock:
        if room_id not in _waiting:
            _waiting[room_id] = {"white": None, "black": None,
                                 "ready": asyncio.Event(), "done": asyncio.Event()}
        slot = _waiting[room_id]
        if conn_color == Color.WHITE:
            slot["white"] = conn
        else:
            slot["black"] = conn

        if slot["white"] and slot["black"]:
            slot["ready"].set()

    # wait for both players
    await _waiting[room_id]["ready"].wait()

    slot = _waiting[room_id]
    white, black = slot["white"], slot["black"]
    done_event = slot["done"]

    if conn_color == Color.WHITE:
        log(f"shard: starting session room={room_id} w={white.name} b={black.name}")
        session = GameSession(white, black, on_done=lambda: _cleanup(room_id, done_event))
        await session.run()
    else:
        # BLACK: GameSession owns the websocket — just wait until the session ends
        await done_event.wait()


def _cleanup(room_id: str, done_event: asyncio.Event | None = None) -> None:
    _waiting.pop(room_id, None)
    _r().delete(f"shard:{room_id}")
    log(f"shard: room {room_id} cleaned up")
    if done_event:
        done_event.set()


async def main() -> None:
    port = int(os.getenv("SHARD_PORT", DEFAULT_SHARD_PORT))
    log(f"game shard listening on ws://0.0.0.0:{port}")
    async with websockets.serve(_on_connect, "0.0.0.0", port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
