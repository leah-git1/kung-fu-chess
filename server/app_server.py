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
        self._sessions: dict[str, asyncio.Event] = {}  # white_name -> done event
        self._session_lock = asyncio.Lock()

    async def start(self) -> None:
        init_db()
        log(f"listening on ws://0.0.0.0:{self._port}")
        async with websockets.serve(self._on_connect, "0.0.0.0", self._port):
            await self._match_loop()

    # ── match loop — driven by AppServer, not Matchmaker ─────────────────────

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

        # Wait for the first intent message
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=PLAY_REQUEST_TIMEOUT_S)
            msg = parse(json.loads(raw))
        except (asyncio.TimeoutError, json.JSONDecodeError, ValueError):
            return

        if isinstance(msg, RoomCreateMsg):
            await self._handle_room_create(conn)
        elif isinstance(msg, RoomJoinMsg):
            await self._handle_room_join(conn, msg.room_id)
        elif isinstance(msg, PlayRequestMsg):
            await self._handle_matchmaking(conn)

    # ── room: create ─────────────────────────────────────────────────────────

    async def _handle_room_create(self, conn: PlayerConnection) -> None:
        room = self._room_manager.create(conn)
        conn.color = Color.WHITE
        log(f"{conn.name} created room {room.room_id}")
        await conn.send(RoomStateMsg(room_id=room.room_id, players=room.player_names,
                                     started=False, color=Color.WHITE.value))
        # Park until a second player joins (ready event set by Room.add)
        await room.ready.wait()
        await self._start_room_session(room)

    # ── room: join ────────────────────────────────────────────────────────────

    async def _handle_room_join(self, conn: PlayerConnection, room_id: str) -> None:
        room = self._room_manager.join(room_id, conn)
        if room is None:
            await conn.send(RoomErrorMsg(reason=f"Room '{room_id}' not found."))
            return
        role = room.add(conn)          # "b" or ""
        conn.color = Color(role) if role else Color.WHITE  # spectators keep WHITE as placeholder
        log(f"{conn.name} joined room {room.room_id} as {'spectator' if not role else 'Black'}")

        if role == "b":
            done_event = await self._get_or_create_done_event(room.white.name)
            await done_event.wait()
        else:
            # Spectator — notify client and register on the session if already running
            players = room.player_names
            await conn.send(RoomStateMsg(room_id=room.room_id, players=players,
                                         started=True, color=""))
            if room.session is not None:
                room.session.add_spectator(conn)
            done_event = await self._get_or_create_done_event(room.white.name)
            await done_event.wait()

    # ── room: start session ───────────────────────────────────────────────────

    async def _start_room_session(self, room) -> None:
        white, black = room.white, room.black
        players = room.player_names
        for c in (white, black):
            try:
                await c.send(RoomStateMsg(room_id=room.room_id, players=players,
                                          started=True, color=c.color.value))
            except ConnectionClosed:
                pass
        for spec in room.spectators:
            try:
                await spec.send(RoomStateMsg(room_id=room.room_id, players=players,
                                             started=True, color=""))
            except ConnectionClosed:
                pass
        log(f"room {room.room_id}: {white.name} vs {black.name}")
        session_key = white.name
        async with self._session_lock:
            if session_key not in self._sessions:
                self._sessions[session_key] = asyncio.Event()
        done_event = self._sessions[session_key]
        session = GameSession(white, black, spectators=room.spectators,
                              on_done=done_event.set)
        room.session = session
        try:
            await session.run()
        finally:
            self._room_manager.remove(room.room_id)
            async with self._session_lock:
                self._sessions.pop(session_key, None)

    async def _get_or_create_done_event(self, key: str) -> asyncio.Event:
        async with self._session_lock:
            if key not in self._sessions:
                self._sessions[key] = asyncio.Event()
            return self._sessions[key]

    # ── matchmaking ───────────────────────────────────────────────────────────

    async def _handle_matchmaking(self, conn: PlayerConnection) -> None:
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

        players = [white.name, black.name]
        for c in (white, black):
            try:
                await c.send(RoomStateMsg(room_id=RoomId.MAIN, players=players,
                                          started=True, color=c.color.value))
            except ConnectionClosed:
                pass

        log(f"match found: {white.name} vs {black.name}")
        session_key = white.name
        async with self._session_lock:
            if session_key not in self._sessions:
                self._sessions[session_key] = asyncio.Event()
        done_event = self._sessions[session_key]

        if conn is white:
            try:
                await GameSession(white, black, on_done=done_event.set).run()
            finally:
                async with self._session_lock:
                    self._sessions.pop(session_key, None)
        else:
            await done_event.wait()
