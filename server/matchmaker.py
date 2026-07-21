"""
Matchmaker — holds players waiting for a game.

Responsibilities:
- add(conn) → asyncio.Future  — enqueue a player, return a Future that resolves
                                 to the matched PlayerConnection when a pair is found
- remove(conn)                — cancel and dequeue (player disconnected while waiting)
- match()                     — try to pair two players within ELO_RANGE;
                                 called externally (by AppServer) on a schedule

The Matchmaker owns no asyncio tasks and sets no timeouts.
AppServer drives the match loop and handles MATCH_TIMEOUT_S.
"""
from __future__ import annotations
import asyncio
from server.session.player_connection import PlayerConnection
from shared.constants import ELO_RANGE


class Matchmaker:
    def __init__(self):
        # list of (PlayerConnection, Future) in arrival order
        self._queue: list[tuple[PlayerConnection, asyncio.Future]] = []

    def add(self, conn: PlayerConnection) -> asyncio.Future:
        """Enqueue a player. Returns a Future that resolves to the opponent
        PlayerConnection when a match is found, or raises CancelledError on timeout."""
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._queue.append((conn, fut))
        return fut

    def remove(self, conn: PlayerConnection) -> None:
        """Remove a player from the queue (disconnected before match)."""
        remaining = []
        for c, f in self._queue:
            if c is conn:
                f.cancel()
            else:
                remaining.append((c, f))
        self._queue = remaining

    def match(self) -> list[tuple[PlayerConnection, PlayerConnection]]:
        """
        Scan the queue for compatible pairs (ELO within range).
        Returns a list of (player_a, player_b) tuples that were matched and
        resolves their futures. Matched players are removed from the queue.
        """
        matched: set[int] = set()
        pairs: list[tuple[PlayerConnection, PlayerConnection]] = []

        for i, (a, fa) in enumerate(self._queue):
            if i in matched:
                continue
            for j, (b, fb) in enumerate(self._queue):
                if j <= i or j in matched:
                    continue
                if abs(a.rating - b.rating) <= ELO_RANGE:
                    matched.add(i)
                    matched.add(j)
                    pairs.append((a, b))
                    fa.set_result(b)
                    fb.set_result(a)
                    break

        self._queue = [(c, f) for k, (c, f) in enumerate(self._queue) if k not in matched]
        return pairs
