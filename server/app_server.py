"""
AppServer — accepts WebSocket connections, assigns White/Black by join order,
then hands both connections to a GameSession.

Step 1 has no login: the first connection becomes White, the second Black.
The server waits for exactly two players before starting.
"""
from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import websockets

from shared.messages import RoomStateMsg, parse
from shared.constants import DEFAULT_PORT
from server.session.player_connection import PlayerConnection
from server.session.game_session import GameSession
from server.logging.server_logger import log


class AppServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self._port = port
        self._waiting: PlayerConnection | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        log(f"listening on ws://0.0.0.0:{self._port}")
        async with websockets.serve(self._on_connect, "0.0.0.0", self._port):
            await asyncio.Future()   # run forever

    async def _on_connect(self, websocket) -> None:
        # Step 1: read the player name from the first message (a HelloMsg or plain name)
        try:
            raw  = await websocket.recv()
            data = json.loads(raw)
            name = data.get("name", "Player")
        except Exception:
            return

        async with self._lock:
            if self._waiting is None:
                # first player → White, wait for second
                conn = PlayerConnection(websocket, color="w", name=name)
                self._waiting = conn
                log(f"{name} connected as White — waiting for Black")
                await conn.send(RoomStateMsg(
                    room_id="main",
                    players=[name],
                    started=False,
                ))
                # keep the connection alive until a second player arrives
                white = conn
                black = None
            else:
                # second player → Black, start the session
                black = PlayerConnection(websocket, color="b", name=name)
                white = self._waiting
                self._waiting = None
                log(f"{name} connected as Black — starting session")

        if black is None:
            # first player: just wait (the session will be started by the second player's handler)
            try:
                await websocket.wait_closed()
            except Exception:
                pass
            return

        # notify both players the game is starting
        for conn, opponent in ((white, black), (black, white)):
            await conn.send(RoomStateMsg(
                room_id="main",
                players=[white.name, black.name],
                started=True,
            ))

        session = GameSession(white, black)
        await session.run()
