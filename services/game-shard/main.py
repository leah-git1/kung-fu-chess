"""
Game Server Shard — supervisor + N worker processes.

Supervisor (main process):
  - Spawns NUM_WORKERS worker processes, each on BASE_PORT + index.
  - Monitors workers and restarts any that die.

Each worker process:
  - Runs its own asyncio event loop + WebSocket server on its assigned port.
  - Writes a heartbeat key to Redis every HEARTBEAT_S seconds:
      shard:worker:{pid}  →  {"host": <SHARD_HOST>, "port": <port>, "rooms": <count>}
  - Handles GameSession lifecycle exactly as before.
  - Deletes its heartbeat key on clean shutdown.
"""
from __future__ import annotations
import asyncio
import json
import multiprocessing
import os
import signal
import sys
import time

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

_SHARD_HOST  = os.getenv("SHARD_HOST", "game-shard")
_REDIS_HOST  = os.getenv("REDIS_HOST", "localhost")
_BASE_PORT   = int(os.getenv("SHARD_PORT", DEFAULT_SHARD_PORT))
_NUM_WORKERS = int(os.getenv("NUM_WORKERS", os.cpu_count() or 2))
_HEARTBEAT_S = 10
_HEARTBEAT_TTL = _HEARTBEAT_S * 3   # missed 3 beats → considered dead
_SHARD_TTL   = 7200


# ── Redis helpers ─────────────────────────────────────────────────────────────

def _r() -> redis.Redis:
    return redis.Redis(host=_REDIS_HOST, port=6379, decode_responses=True)


# ── Worker process ────────────────────────────────────────────────────────────

_waiting: dict[str, dict] = {}
_active_rooms: int = 0
_waiting_lock: asyncio.Lock | None = None  # created inside the worker's event loop


async def _on_connect(websocket) -> None:
    global _active_rooms, _waiting_lock
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

    r = _r()
    stored = r.get(f"session:{token}")
    if not stored:
        await websocket.send(json.dumps({"type": "error", "reason": "invalid token"}))
        return
    r.delete(f"session:{token}")

    shard_raw = r.get(f"shard:{room_id}")
    if not shard_raw:
        await websocket.send(json.dumps({"type": "error", "reason": "room not found"}))
        return

    conn_color = Color.WHITE if color == Color.WHITE.value else Color.BLACK
    conn = PlayerConnection(websocket, color=conn_color, name=stored, rating=1200)
    log(f"worker {os.getpid()}: {stored} joined room {room_id} as {conn_color.name}")

    lock = _waiting_lock
    async with lock:
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

    await _waiting[room_id]["ready"].wait()

    slot = _waiting[room_id]
    white, black = slot["white"], slot["black"]
    done_event   = slot["done"]
    
    if conn_color == Color.WHITE:
        _active_rooms += 1
        log(f"worker {os.getpid()}: starting session room={room_id} "
            f"w={white.name} b={black.name}  active={_active_rooms}")
        session = GameSession(white, black,
                              on_done=lambda: _cleanup(room_id, done_event))
        await session.run()
    else:
        await done_event.wait()


def _cleanup(room_id: str, done_event: asyncio.Event | None = None) -> None:
    global _active_rooms
    _waiting.pop(room_id, None)
    _r().delete(f"shard:{room_id}")
    _active_rooms = max(0, _active_rooms - 1)
    log(f"worker {os.getpid()}: room {room_id} cleaned up  active={_active_rooms}")
    if done_event:
        done_event.set()


async def _heartbeat_loop(port: int) -> None:
    r = _r()
    key = f"shard:worker:{os.getpid()}"
    try:
        while True:
            r.set(key,
                  json.dumps({"host": _SHARD_HOST, "port": port,
                               "rooms": _active_rooms}),
                  ex=_HEARTBEAT_TTL)
            await asyncio.sleep(_HEARTBEAT_S)
    finally:
        r.delete(key)


def _run_worker(port: int) -> None:
    """Entry point for each worker process."""
    async def _worker_main():
        global _waiting_lock
        _waiting_lock = asyncio.Lock()

        log(f"worker {os.getpid()} listening on ws://0.0.0.0:{port}")
        async with websockets.serve(_on_connect, "0.0.0.0", port):
            await asyncio.gather(
                _heartbeat_loop(port),
                asyncio.Future(),   # run forever
            )

    # ignore SIGINT in workers — supervisor handles shutdown
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    asyncio.run(_worker_main())


# ── Supervisor ────────────────────────────────────────────────────────────────

def main() -> None:
    log(f"supervisor: starting {_NUM_WORKERS} workers on ports "
        f"{_BASE_PORT}–{_BASE_PORT + _NUM_WORKERS - 1}")

    processes: list[multiprocessing.Process] = []
    ports = [_BASE_PORT + i for i in range(_NUM_WORKERS)]

    for port in ports:
        p = multiprocessing.Process(target=_run_worker, args=(port,), daemon=False)
        p.start()
        processes.append(p)

    def _shutdown(sig, frame):
        log("supervisor: shutting down workers")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join(timeout=5)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT,  _shutdown)

    # monitor and restart dead workers
    while True:
        time.sleep(5)
        for i, p in enumerate(processes):
            if not p.is_alive():
                port = ports[i]
                log(f"supervisor: worker on port {port} died (exit {p.exitcode}), restarting")
                new_p = multiprocessing.Process(target=_run_worker, args=(port,), daemon=False)
                new_p.start()
                processes[i] = new_p


if __name__ == "__main__":
    main()
