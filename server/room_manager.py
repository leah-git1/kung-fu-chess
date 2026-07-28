from __future__ import annotations
import os
import uuid
import redis
from server.session.player_connection import PlayerConnection
from server.session.room import Room
from shared.constants import ROOM_ID_LENGTH, ROOM_TTL_S
from shared.enums import Color
from server.logging.server_logger import log


def _make_redis() -> redis.Redis | None:
    host = os.getenv("REDIS_HOST")
    if not host:
        return None
    return redis.Redis(host=host, port=6379, decode_responses=True)


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}
        self._redis = _make_redis()

    def create(self, conn: PlayerConnection) -> Room:
        room_id = self._unique_id()
        room = Room(room_id, conn)
        self._rooms[room_id] = room
        if self._redis:
            self._redis.set(f"room:{room_id}", conn.name, ex=ROOM_TTL_S)
            log(f"redis SET room:{room_id} = {conn.name}")
        return room

    def join(self, room_id: str, conn: PlayerConnection) -> tuple[Room, Color] | None:
        room_id = room_id.upper()
        if self._redis and not self._redis.exists(f"room:{room_id}"):
            return None
        room = self._rooms.get(room_id)
        if room is None:
            return None
        return room, room.add(conn)

    def remove(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)
        if self._redis:
            self._redis.delete(f"room:{room_id}")

    def _unique_id(self) -> str:
        while True:
            code = uuid.uuid4().hex[:ROOM_ID_LENGTH].upper()
            if self._redis:
                if not self._redis.exists(f"room:{code}"):
                    return code
            elif code not in self._rooms:
                return code
