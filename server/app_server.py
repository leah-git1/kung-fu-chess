from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import websockets

from shared.messages import RoomStateMsg
from shared.constants import DEFAULT_PORT
from server.session.player_connection import PlayerConnection
from server.session.game_session import GameSession
from server.logging.server_logger import log


class AppServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self._port = port
        self._waiting: PlayerConnection | None = None
        self._waiting_done: asyncio.Event | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        log(f"listening on ws://0.0.0.0:{self._port}")
        async with websockets.serve(self._on_connect, "0.0.0.0", self._port):
            await asyncio.Future()

    async def _on_connect(self, websocket) -> None:
        try:
            raw  = await websocket.recv()
            data = json.loads(raw)
            name = data.get("name") or data.get("player_name", "Player")
        except Exception:
            return

        async with self._lock:
            if self._waiting is None:
                done  = asyncio.Event()
                conn  = PlayerConnection(websocket, color="w", name=name)
                self._waiting      = conn
                self._waiting_done = done
                log(f"{name} connected as White — waiting for Black")
                await conn.send(RoomStateMsg(room_id="main", players=[name], started=False))
                # store locally so we can wait outside the lock
                my_done = done
                session_to_run = None
            else:
                black = PlayerConnection(websocket, color="b", name=name)
                white = self._waiting
                done  = self._waiting_done
                self._waiting      = None
                self._waiting_done = None
                log(f"{name} connected as Black — starting session")

                players = [white.name, black.name]
                for conn in (white, black):
                    await conn.send(RoomStateMsg(room_id="main", players=players,
                                                 started=True, color=conn.color))

                session_to_run = GameSession(white, black, on_done=done.set)
                my_done = None

        if session_to_run is not None:
            # Black's handler runs the session
            await session_to_run.run()
        else:
            # White's handler waits until the session finishes
            await my_done.wait()
