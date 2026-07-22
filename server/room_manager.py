from __future__ import annotations
import uuid
from server.session.player_connection import PlayerConnection
from server.session.room import Room
from shared.constants import ROOM_ID_LENGTH


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def create(self, conn: PlayerConnection) -> Room:
        room_id = self._unique_id()
        room = Room(room_id, conn)
        self._rooms[room_id] = room
        return room

    def join(self, room_id: str, conn: PlayerConnection) -> Room | None:
        """Return the room if found, None otherwise."""
        return self._rooms.get(room_id.upper())

    def remove(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)

    def _unique_id(self) -> str:
        while True:
            code = uuid.uuid4().hex[:ROOM_ID_LENGTH].upper()
            if code not in self._rooms:
                return code
