from __future__ import annotations
import os
import httpx
from server.session.player_connection import PlayerConnection
from server.session.room import Room
from shared.enums import Color
from server.logging.server_logger import log

_ROOMS_URL = f"http://{os.getenv('ROOMS_HOST', 'localhost')}:{os.getenv('ROOMS_PORT', '8001')}"


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def create(self, conn: PlayerConnection) -> Room:
        resp = httpx.post(f"{_ROOMS_URL}/rooms", json={"creator": conn.name}, timeout=5.0)
        resp.raise_for_status()
        room_id = resp.json()["room_id"]
        room = Room(room_id, conn)
        self._rooms[room_id] = room
        log(f"rooms-api created room {room_id} for {conn.name}")
        return room

    def join(self, room_id: str, conn: PlayerConnection) -> tuple[Room, Color] | None:
        room_id = room_id.upper()
        resp = httpx.get(f"{_ROOMS_URL}/rooms/{room_id}", timeout=5.0)
        if resp.status_code != 200 or not resp.json().get("exists"):
            return None
        room = self._rooms.get(room_id)
        if room is None:
            return None
        return room, room.add(conn)

    def remove(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)
        try:
            httpx.delete(f"{_ROOMS_URL}/rooms/{room_id}", timeout=5.0)
        except httpx.RequestError:
            pass  # best-effort cleanup
