from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import websockets
from websockets.exceptions import ConnectionClosed

from shared.messages import RoomStateMsg, RoomErrorMsg, SearchTimeoutMsg, parse, PlayRequestMsg, RoomCreateMsg, RoomJoinMsg
from shared.constants import DEFAULT_PORT, MATCH_TIMEOUT_S, PLAY_REQUEST_TIMEOUT_S, RoomId
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
        self._registry = {
            RoomCreateMsg:  self._handle_room_create,
            RoomJoinMsg:    self._handle_room_join,
            PlayRequestMsg: self._handle_matchmaking,
        }

    async def start(self) -> None:
        init_db()
        log(f"listening on ws://0.0.0.0:{self._port}")
        async with websockets.serve(self._on_connect, "0.0.0.0", self._port):
            await self._match_loop()

    # ── match loop ────────────────────────────────────────────────────────────

    async def _match_loop(self) -> None:
        while True:
            await asyncio.sleep(1)
            self._matchmaker.match()

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
        fut = self._matchmaker.add(conn)
        try:
            await asyncio.wait_for(asyncio.shield(fut), timeout=MATCH_TIMEOUT_S)
        except asyncio.TimeoutError:
            self._matchmaker.remove(conn)
            await conn.send(SearchTimeoutMsg())
            log(f"{conn.name} search timed out")
            return
        except asyncio.CancelledError:
            return

        if not fut.done() or fut.cancelled():
            return

        opponent: PlayerConnection = fut.result()
        white, black = (conn, opponent) if id(conn) < id(opponent) else (opponent, conn)
        white.color = Color.WHITE
        black.color = Color.BLACK

        room_id = RoomId.MAIN
        players = [white.name, black.name]
        for c in (white, black):
            await self._safe_send(c, RoomStateMsg(room_id=room_id, players=players,
                                                  started=True, color=c.color.value))

        log(f"match found: {white.name} vs {black.name}")
        session = GameSession(white, black,
                              on_done=(await self._get_or_create_done_event(room_id)).set)

        if conn is white:
            await self._run_session(room_id, session)
        else:
            await (await self._get_or_create_done_event(room_id)).wait()

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
