from __future__ import annotations
import os
import httpx
from server.session.player_connection import PlayerConnection

_MM_URL = f"http://{os.getenv('MM_HOST', 'localhost')}:{os.getenv('MM_PORT', '8003')}"


class Matchmaker:
    def enqueue(self, conn: PlayerConnection) -> None:
        httpx.post(f"{_MM_URL}/queue",
                   json={"name": conn.name, "rating": conn.rating}, timeout=5.0)

    def dequeue(self, conn: PlayerConnection) -> None:
        httpx.delete(f"{_MM_URL}/queue/{conn.name}", timeout=5.0)

    def poll(self, conn: PlayerConnection) -> dict | None:
        """Returns opponent info dict if matched, None if still waiting."""
        resp = httpx.get(f"{_MM_URL}/queue/{conn.name}/match", timeout=5.0)
        data = resp.json()
        return data if data["matched"] else None
