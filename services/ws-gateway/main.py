"""
WS Gateway — stateless WebSocket entry point.

Responsibilities (only):
  1. Validate the session token from Redis (issued by API Gateway)
  2. Send RoomStateMsg(started=False) — lobby confirmation
  3. Route the next client message to the right backend service:
       PlayRequestMsg  → matchmaker-service (poll loop) → allocator → ShardConnectMsg
       RoomCreateMsg   → rooms-api → wait for second player → allocator → ShardConnectMsg
       RoomJoinMsg     → rooms-api existence check → ShardConnectMsg (if room already started)

No GameSession, no game logic, no DB access.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
import uuid

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import httpx
import nats
import redis.asyncio as aioredis
import websockets
from websockets.exceptions import ConnectionClosed

from shared.messages import (
    RoomStateMsg, RoomErrorMsg, SearchTimeoutMsg, ShardConnectMsg,
    parse, PlayRequestMsg, RoomCreateMsg, RoomJoinMsg,
)
from shared.constants import DEFAULT_PORT, MATCH_TIMEOUT_S, PLAY_REQUEST_TIMEOUT_S, RoomId
from shared.enums import Color
from server.session.player_connection import PlayerConnection
from server.logging.server_logger import log

_MM_URL        = f"http://{os.getenv('MM_HOST','localhost')}:{os.getenv('MM_PORT','8003')}"
_ROOMS_URL     = f"http://{os.getenv('ROOMS_HOST','localhost')}:{os.getenv('ROOMS_PORT','8001')}"
_ALLOCATOR_URL = f"http://{os.getenv('ALLOCATOR_HOST','localhost')}:{os.getenv('ALLOCATOR_PORT','8004')}"
_NATS_URL      = os.getenv("NATS_URL", "nats://localhost:4222")
_SESSION_TTL   = 300

# in-process registry of connections waiting for a match (same-process only)
_pending: dict[str, PlayerConnection] = {}
# futures resolved when kfc.allocated arrives for a player: name → Future
_alloc_futures: dict[str, asyncio.Future] = {}
_nc = None   # nats client


def _r() -> aioredis.Redis:
    return aioredis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                          decode_responses=True)


async def _validate_token(token: str) -> str | None:
    r = _r()
    username = await r.get(f"session:{token}")
    if username:
        await r.delete(f"session:{token}")
    await r.aclose()
    return username


async def _issue_token(username: str) -> str:
    token = uuid.uuid4().hex
    r = _r()
    await r.set(f"session:{token}", username, ex=_SESSION_TTL)
    await r.aclose()
    return token


async def _on_connect(websocket) -> None:
    # ── 1. token validation ───────────────────────────────────────────────────
    try:
        raw = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        d   = json.loads(raw)
    except Exception:
        return

    if d.get("type") != "token":
        return

    username = await _validate_token(d.get("token", ""))
    if not username:
        await websocket.send(json.dumps({"type": "login_fail", "reason": "invalid or expired token"}))
        return
    rating = int(d.get("rating", 1200))

    conn = PlayerConnection(websocket, color=Color.WHITE, name=username, rating=rating)
    log(f"{username} (ELO {rating}) connected to WS gateway")

    # ── 2. lobby confirmation ─────────────────────────────────────────────────
    await conn.send(RoomStateMsg(room_id=RoomId.MAIN, players=[username], started=False))

    # ── 3. wait for action ────────────────────────────────────────────────────
    try:
        raw = await asyncio.wait_for(websocket.recv(), timeout=PLAY_REQUEST_TIMEOUT_S)
        msg = parse(json.loads(raw))
    except (asyncio.TimeoutError, json.JSONDecodeError, ValueError):
        return

    registry = {
        PlayRequestMsg: _handle_matchmaking,
        RoomCreateMsg:  _handle_room_create,
        RoomJoinMsg:    _handle_room_join,
    }
    if handler := registry.get(type(msg)):
        await handler(msg, conn)


# ── matchmaking ───────────────────────────────────────────────────────────────

async def _on_allocated(msg) -> None:
    """NATS handler for kfc.allocated — resolves the waiting future for each player."""
    data = json.loads(msg.data.decode())
    for name in (data["white"], data["black"]):
        fut = _alloc_futures.get(name)
        if fut and not fut.done():
            fut.set_result(data)


async def _handle_matchmaking(msg: PlayRequestMsg, conn: PlayerConnection) -> None:
    log(f"{conn.name} searching for game")
    async with httpx.AsyncClient() as client:
        await client.post(f"{_MM_URL}/queue",
                          json={"name": conn.name, "rating": conn.rating}, timeout=5.0)

    _pending[conn.name] = conn
    fut: asyncio.Future = asyncio.get_event_loop().create_future()
    _alloc_futures[conn.name] = fut

    try:
        alloc = await asyncio.wait_for(fut, timeout=MATCH_TIMEOUT_S)
    except asyncio.TimeoutError:
        await conn.send(SearchTimeoutMsg())
        log(f"{conn.name} search timed out")
        return
    finally:
        _pending.pop(conn.name, None)
        _alloc_futures.pop(conn.name, None)
        async with httpx.AsyncClient() as client:
            await client.delete(f"{_MM_URL}/queue/{conn.name}", timeout=5.0)

    room_id   = alloc["room_id"]
    shard_url = alloc["shard_url"]
    conn.color = Color.WHITE if conn.name == alloc["white"] else Color.BLACK
    log(f"{conn.name} allocated room {room_id} → {shard_url}")

    players = [alloc["white"], alloc["black"]]
    await _safe_send(conn, ShardConnectMsg(
        shard_url=shard_url, room_id=room_id,
        token=await _issue_token(conn.name), color=conn.color.value, players=players,
    ))
    await asyncio.sleep(3)


# ── room: create ──────────────────────────────────────────────────────────────

async def _handle_room_create(msg: RoomCreateMsg, conn: PlayerConnection) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{_ROOMS_URL}/rooms",
                                 json={"creator": conn.name}, timeout=5.0)
    resp.raise_for_status()
    room_id = resp.json()["room_id"]
    conn.color = Color.WHITE
    log(f"{conn.name} created room {room_id}")

    _pending[conn.name] = conn
    await conn.send(RoomStateMsg(room_id=room_id, players=[conn.name],
                                 started=False, color=Color.WHITE.value))

    r = _r()
    try:
        deadline = asyncio.get_event_loop().time() + PLAY_REQUEST_TIMEOUT_S
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(1)
            black_name = await r.get(f"room_ready:{room_id}")
            if black_name:
                await r.delete(f"room_ready:{room_id}")
                black_conn = _pending.get(black_name)
                if black_conn is None:
                    return
                async with httpx.AsyncClient() as client:
                    alloc = (await client.post(f"{_ALLOCATOR_URL}/allocate",
                                               json={"white": conn.name, "black": black_name},
                                               timeout=5.0)).json()
                players = [conn.name, black_name]
                for c, col in ((conn, Color.WHITE), (black_conn, Color.BLACK)):
                    await _safe_send(c, ShardConnectMsg(
                        shard_url=alloc["shard_url"], room_id=alloc["room_id"],
                        token=await _issue_token(c.name), color=col.value, players=players,
                    ))
                _pending.pop(black_name, None)
                await asyncio.sleep(3)  # keep socket open so client receives ShardConnectMsg
                return
    finally:
        _pending.pop(conn.name, None)
        await r.aclose()


# ── room: join ────────────────────────────────────────────────────────────────

async def _handle_room_join(msg: RoomJoinMsg, conn: PlayerConnection) -> None:
    room_id = msg.room_id.upper()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_ROOMS_URL}/rooms/{room_id}", timeout=5.0)
    if resp.status_code != 200 or not resp.json().get("exists"):
        await conn.send(RoomErrorMsg(reason=f"Room '{room_id}' not found."))
        return

    conn.color = Color.BLACK
    _pending[conn.name] = conn
    log(f"{conn.name} joining room {room_id}")

    await conn.send(RoomStateMsg(room_id=room_id, players=[conn.name],
                                 started=False, color=Color.BLACK.value))

    r = _r()
    await r.set(f"room_ready:{room_id}", conn.name, ex=300)
    await r.aclose()

    # wait until WHITE pops us from _pending (after sending ShardConnectMsg)
    deadline = asyncio.get_event_loop().time() + PLAY_REQUEST_TIMEOUT_S
    while asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(1)
        if conn.name not in _pending:
            return
    _pending.pop(conn.name, None)


# ── helpers ───────────────────────────────────────────────────────────────────

async def _safe_send(conn: PlayerConnection, msg) -> None:
    try:
        await conn.send(msg)
    except ConnectionClosed:
        pass


async def main() -> None:
    global _nc
    port = int(os.getenv("WS_PORT", DEFAULT_PORT))
    _nc = await nats.connect(_NATS_URL)
    await _nc.subscribe("kfc.allocated", cb=_on_allocated)
    log(f"WS gateway listening on ws://0.0.0.0:{port}")
    async with websockets.serve(_on_connect, "0.0.0.0", port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
