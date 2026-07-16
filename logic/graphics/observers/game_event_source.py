from graphics.observers.game_events import GameSubject, PieceMovedEvent, PieceCapturedEvent
import time

class GameEventSource(GameSubject):
    def __init__(self):
        super().__init__()
        self._prev = {}
        self._primed = False
        self._start_ms = int(time.monotonic() * 1000)

    def poll(self, game):
        curr = self._index(game.snapshot())
        if self._primed:
            self._diff(self._prev, curr)
        self._prev, self._primed = curr, True

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
                    self.notify_piece_moved(PieceMovedEvent(
                        piece, prev_cell, curr[pid][1], ms,
                        piece_name=piece.sprite_key[1]))
            else:
                by_piece = next((p2 for p2, c2 in curr.values() if c2 == prev_cell), None)
                self.notify_piece_captured(PieceCapturedEvent(
                    piece, prev_cell, by_piece, ms,
                    piece_value=piece.value))