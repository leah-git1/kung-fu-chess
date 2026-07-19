from __future__ import annotations
import json


class PlayerConnection:
    """Wraps one WebSocket connection and the color assigned to that player."""

    def __init__(self, websocket, color: str, name: str):
        self.websocket = websocket
        self.color = color          
        self.name  = name

    async def send(self, msg) -> None:
        await self.websocket.send(json.dumps(msg.to_json()))

    async def send_raw(self, d: dict) -> None:
        await self.websocket.send(json.dumps(d))
