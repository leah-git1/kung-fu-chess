from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import websockets
from websockets.exceptions import ConnectionClosed

from shared.messages import RoomStateMsg, RoomErrorMsg, SearchTimeoutMsg, parse, PlayRequestMsg, RoomCreateMsg, RoomJoinMsg, ShardConnectMsg
from shared.constants import DEFAULT_PORT, MATCH_TIMEOUT_S, PLAY_REQUEST_TIMEOUT_S, RoomId
import httpx
import uuid
import redis as _redis_lib

_ALLOCATOR_URL = f"http://{os.getenv('ALLOCATOR_HOST', 'localhost')}:{os.getenv('ALLOCATOR_PORT', '8004')}"
_SHARD_WS_URL  = os.getenv('SHARD_WS_URL', 'ws://localhost:5556')
_SESSION_TTL   = 300


def _issue_token(username: str) -> str:
    token = uuid.uuid4().hex
    r = _redis_lib.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)
    r.set(f"session:{token}", username, ex=_SESSION_TTL)
    return token
from shared.enums import Color
from server.session.player_connection import PlayerConnection
from server.session.game_session import GameSession
from server.logging.server_logger import log
from server.auth.auth_handler import authenticate
from server.db.database import init_db
from server.matchmaker import Matchmaker
from server.room_manager import RoomManager


class AppServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self._port         = port
        self._matchmaker   = Matchmaker()
        self._room_manager = RoomManager()
        self._sessions: dict[str, asyncio.Event] = {}  # room_id -> done event
        self._session_lock = asyncio.Lock()
        self._pending: dict[str, PlayerConnection] = {}  # name -> conn waiting for match
        self._registry = {
            RoomCreateMsg:  self._handle_room_create,
            RoomJoinMsg:    self._handle_room_join,
            PlayRequestMsg: self._handle_matchmaking,
        }

    async def start(self) -> None:
        init_db()
        self._ping_redis()
        log(f"listening on ws://0.0.0.0:{self._port}")
        async with websockets.serve(self._on_connect, "0.0.0.0", self._port):
            await asyncio.Future()  # run forever

    @staticmethod
    def _ping_redis() -> None:
        import os, redis as _redis
        host = os.getenv("REDIS_HOST")
        if not host:
            return
        try:
            r = _redis.Redis(host=host, port=6379, decode_responses=True)
            r.set("kfc:ping", "pong")
            log(f"redis ping ok — GET kfc:ping = {r.get('kfc:ping')}")
        except Exception as e:
            log(f"redis ping failed: {e}", level="warning")

    # ── one coroutine per connected client ────────────────────────────────────

    async def _on_connect(self, websocket) -> None:
        result = await authenticate(websocket)
        if result is None:
            return
        name, rating = result

        conn = PlayerConnection(websocket, color=Color.WHITE, name=name, rating=rating)
        log(f"{name} (ELO {rating}) connected — waiting for action")
        await conn.send(RoomStateMsg(room_id=RoomId.MAIN, players=[name], started=False))

        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=PLAY_REQUEST_TIMEOUT_S)
            msg = parse(json.loads(raw))
        except (asyncio.TimeoutError, json.JSONDecodeError, ValueError):
            return

        if handler := self._registry.get(type(msg)):
            await handler(msg, conn)

    # ── room: create ─────────────────────────────────────────────────────────

    async def _handle_room_create(self, msg: RoomCreateMsg, conn: PlayerConnection) -> None:
        room = self._room_manager.create(conn)
        conn.color = Color.WHITE
        log(f"{conn.name} created room {room.room_id}")
        await conn.send(RoomStateMsg(room_id=room.room_id, players=room.player_names,
                                     started=False, color=Color.WHITE.value))
        await room.ready.wait()
        await self._start_room_session(room)

    # ── room: join ────────────────────────────────────────────────────────────

    async def _handle_room_join(self, msg: RoomJoinMsg, conn: PlayerConnection) -> None:
        result = self._room_manager.join(msg.room_id, conn)
        if result is None:
            await conn.send(RoomErrorMsg(reason=f"Room '{room_id}' not found."))
            return
        room, role = result
        conn.color = role if role != Color.SPECTATOR else Color.WHITE
        log(f"{conn.name} joined room {room.room_id} as {role.name.lower()}")

        if role == Color.BLACK:
            await (await self._get_or_create_done_event(room.room_id)).wait()
        else:
            await self._safe_send(conn, RoomStateMsg(room_id=room.room_id, players=room.player_names,
                                                     started=True, color=Color.SPECTATOR.value))
            if room.session is not None:
                room.session.add_spectator(conn)
            await (await self._get_or_create_done_event(room.room_id)).wait()

    # ── room: start session ───────────────────────────────────────────────────

    async def _start_room_session(self, room) -> None:
        white, black = room.white, room.black
        players = room.player_names
        for c in (white, black):
            await self._safe_send(c, RoomStateMsg(room_id=room.room_id, players=players,
                                                  started=True, color=c.color.value))
        for spec in room.spectators:
            await self._safe_send(spec, RoomStateMsg(room_id=room.room_id, players=players,
                                                     started=True, color=Color.SPECTATOR.value))
        log(f"room {room.room_id}: {white.name} vs {black.name}")
        session = GameSession(white, black, spectators=room.spectators,
                              on_done=(await self._get_or_create_done_event(room.room_id)).set)
        room.session = session
        await self._run_session(room.room_id, session)

    # ── matchmaking ───────────────────────────────────────────────────────────

    async def _handle_matchmaking(self, msg: PlayRequestMsg, conn: PlayerConnection) -> None:
        log(f"{conn.name} (ELO {conn.rating}) searching for game")
        self._matchmaker.enqueue(conn)
        self._pending[conn.name] = conn
        deadline = asyncio.get_event_loop().time() + MATCH_TIMEOUT_S
        try:
            while asyncio.get_event_loop().time() < deadline:
                await asyncio.sleep(1)
                result = self._matchmaker.poll(conn)
                if result:
                    opponent_name = result["opponent"]
                    # determine color by name order (deterministic)
                    if conn.name < opponent_name:
                        conn.color = Color.WHITE
                    else:
                        conn.color = Color.BLACK

                    if conn.color == Color.WHITE:
                        opponent_conn = self._pending.get(opponent_name)
                        if opponent_conn is None:
                            await asyncio.sleep(1)
                            opponent_conn = self._pending.get(opponent_name)
                        if opponent_conn is None:
                            log(f"opponent conn not found for {opponent_name}", level="warning")
                            return

                        alloc = httpx.post(
                            f"{_ALLOCATOR_URL}/allocate",
                            json={"white": conn.name, "black": opponent_name},
                            timeout=5.0,
                        ).json()
                        room_id = alloc["room_id"]
                        log(f"allocated room {room_id} on shard {alloc['shard']}")

                        opponent_conn.color = Color.BLACK
                        players = [conn.name, opponent_name]
                        white_token = _issue_token(conn.name)
                        black_token = _issue_token(opponent_name)
                        for c, col, tok in ((conn, Color.WHITE, white_token),
                                            (opponent_conn, Color.BLACK, black_token)):
                            await self._safe_send(c, ShardConnectMsg(
                                shard_url=_SHARD_WS_URL,
                                room_id=room_id,
                                token=tok,
                                color=col.value,
                                players=players,
                            ))
                        log(f"sent ShardConnectMsg to both players for room {room_id}")
                    else:
                        log(f"match found (black): {conn.name} vs {opponent_name} — waiting for shard redirect")
                    return
        finally:
            self._pending.pop(conn.name, None)
            self._matchmaker.dequeue(conn)

        await conn.send(SearchTimeoutMsg())
        log(f"{conn.name} search timed out")

    # ── shared helpers ────────────────────────────────────────────────────────

    async def _run_session(self, room_id: str, session: GameSession) -> None:
        try:
            await session.run()
        finally:
            self._room_manager.remove(room_id)
            async with self._session_lock:
                self._sessions.pop(room_id, None)

    async def _get_or_create_done_event(self, room_id: str) -> asyncio.Event:
        async with self._session_lock:
            if room_id not in self._sessions:
                self._sessions[room_id] = asyncio.Event()
            return self._sessions[room_id]

    @staticmethod
    async def _safe_send(conn: PlayerConnection, msg) -> None:
        try:
            await conn.send(msg)
        except ConnectionClosed:
            pass
