from graphics.observers.game_events import PieceMovedEvent, PieceCapturedEvent, GameOverEvent
import time


class GameEventSource:
    def __init__(self, bus):
        self._bus = bus
        self._prev = {}
        self._primed = False
        self._game_over_published = False
        self._start_ms = int(time.monotonic() * 1000)

    def poll(self, game):
        curr = self._index(game.snapshot())
        if self._primed:
            self._diff(self._prev, curr)
        self._prev, self._primed = curr, True
        if game.game_over and not self._game_over_published:
            self._game_over_published = True
            self._bus.publish(GameOverEvent(winner_color=game.winner_color))

    def _elapsed(self):
        return int(time.monotonic() * 1000) - self._start_ms

    @staticmethod
    def _index(grid):
        return {id(p): (p, (r, c))
                for r, row in enumerate(grid)
                for c, p in enumerate(row) if p is not None}

    def _diff(self, prev, curr):
        ms = self._elapsed()
        for pid, (piece, prev_cell) in prev.items():
            if pid in curr:
                if curr[pid][1] != prev_cell:
                    self._bus.publish(PieceMovedEvent(
                        piece.color, prev_cell, curr[pid][1], ms,
                        piece_name=piece.sprite_key[1]))
            else:
                by = next((p2 for p2, c2 in curr.values() if c2 == prev_cell), None)
                self._bus.publish(PieceCapturedEvent(
                    prev_cell, ms,
                    piece_value=piece.value,
                    by_color=by.color if by else None,
                    captured_color=piece.color,
                    captured_type=piece.piece_type.value))
