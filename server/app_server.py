from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import websockets

from shared.messages import RoomStateMsg, SearchTimeoutMsg, parse
from shared.constants import DEFAULT_PORT, MATCH_TIMEOUT_S, PLAY_REQUEST_TIMEOUT_S, PLAY_REQUEST_TIMEOUT_S
from server.session.player_connection import PlayerConnection
from server.session.game_session import GameSession
from server.logging.server_logger import log
from server.auth.auth_handler import authenticate
from server.db.database import init_db
from server.matchmaker import Matchmaker


class AppServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self._port       = port
        self._matchmaker = Matchmaker()
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

        conn = PlayerConnection(websocket, color="w", name=name, rating=rating)
        log(f"{name} (ELO {rating}) connected — waiting for Play")
        await conn.send(RoomStateMsg(room_id="main", players=[name], started=False))

        # Wait for PlayRequestMsg before entering matchmaking
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=PLAY_REQUEST_TIMEOUT_S)
            msg = parse(json.loads(raw))
            if msg.__class__.__name__ != "PlayRequestMsg":
                return
        except Exception:
            return

        log(f"{name} (ELO {rating}) searching for game")
        fut = self._matchmaker.add(conn)
        try:
            await asyncio.wait_for(asyncio.shield(fut), timeout=MATCH_TIMEOUT_S)
        except asyncio.TimeoutError:
            self._matchmaker.remove(conn)
            await conn.send(SearchTimeoutMsg())
            log(f"{name} search timed out")
            return
        except asyncio.CancelledError:
            return

        if not fut.done() or fut.cancelled():
            return

        opponent: PlayerConnection = fut.result()

        white, black = (conn, opponent) if id(conn) < id(opponent) else (opponent, conn)
        white.color = "w"
        black.color = "b"

        players = [white.name, black.name]
        for c in (white, black):
            try:
                await c.send(RoomStateMsg(room_id="main", players=players,
                                          started=True, color=c.color))
            except Exception:
                pass

        log(f"match found: {white.name} vs {black.name}")

        # Both _on_connect handlers must stay alive for the full game duration
        # (websockets closes the socket the moment the handler returns).
        # Use a shared Event keyed by white's name so both handlers wait on
        # the exact same object regardless of scheduling order.
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
