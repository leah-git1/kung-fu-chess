from __future__ import annotations
import asyncio
from server.session.player_connection import PlayerConnection
from shared.enums import Color


class Room:
    """
    Data container for one private room.

    white  : first player to join — always White
    black  : second player to join — always Black
    spectators : any further connections (receive STATE_UPDATE, cannot move)
    ready  : asyncio.Event set when both white and black are present
    """

    def __init__(self, room_id: str, white: PlayerConnection):
        self.room_id    = room_id
        self.white      = white
        self.black: PlayerConnection | None = None
        self.spectators: list[PlayerConnection] = []
        self.ready      = asyncio.Event()
        self.session: object | None = None  # set to GameSession once started

    @property
    def player_names(self) -> list[str]:
        names = [self.white.name]
        if self.black:
            names.append(self.black.name)
        return names

    def add(self, conn: PlayerConnection) -> Color:
        """
        Add a connection to the room.
        Returns the assigned role: Color.BLACK for Black, Color.SPECTATOR for spectator.
        """
        if self.black is None:
            self.black = conn
            self.ready.set()
            return Color.BLACK
        self.spectators.append(conn)
        return Color.SPECTATOR
