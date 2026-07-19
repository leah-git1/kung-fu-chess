from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))

from board.piece import Piece, PieceState
from board.piece_type import PieceType
import config


def _make_piece(key: str) -> Piece:
    color    = key[0]
    pt_value = key[1]
    return Piece(
        color=color,
        piece_type=PieceType(pt_value),
        is_royal=(pt_value in config.ROYAL_PIECE_TYPES),
        forward_direction=config.FORWARD_DIRECTION.get(color, 0),
    )


# ── lightweight motion stubs (same interface PieceRenderer reads) ─────────────

class _MoveMotionStub:
    def __init__(self, piece, origin, destination, actual_destination, finish_time):
        self.piece              = piece
        self.origin             = tuple(origin)
        self.destination        = tuple(destination)
        self.actual_destination = tuple(actual_destination)
        self.finish_time        = finish_time


class _JumpMotionStub:
    def __init__(self, piece, cell):
        self.piece = piece
        self.cell  = tuple(cell)


# ── mirror ────────────────────────────────────────────────────────────────────

class BoardMirror:
    ROWS = 8
    COLS = 8

    def __init__(self):
        self.current_time: int    = 0
        self.game_over: bool      = False
        self.winner_color: str | None = None
        self._grid: list[list]    = [[None] * self.COLS for _ in range(self.ROWS)]
        self._active_moves: list  = []
        self._active_jumps: list  = []
        # stable piece registry: sprite_key -> [Piece, ...]
        self._registry: dict[str, list[Piece]] = {}

    def _get_or_create(self, key: str, index: int) -> Piece:
        bucket = self._registry.setdefault(key, [])
        while len(bucket) <= index:
            bucket.append(_make_piece(key))
        return bucket[index]

    def apply_state_update(self, board: list, time_ms: int, motions: dict = None) -> None:
        self.current_time = time_ms
        motions = motions or {"moves": [], "jumps": []}

        # ── rebuild grid with stable piece instances ──────────────────────────
        new_grid = [[None] * self.COLS for _ in range(self.ROWS)]
        counters: dict[str, int] = {}

        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell is None:
                    continue
                key        = cell["k"] if isinstance(cell, dict) else cell
                state_name = cell.get("s", "idle") if isinstance(cell, dict) else "idle"
                cd_finish  = cell.get("cd_finish") if isinstance(cell, dict) else None
                idx        = counters.get(key, 0)
                counters[key] = idx + 1
                piece = self._get_or_create(key, idx)
                try:
                    piece.state = PieceState(state_name)
                except ValueError:
                    piece.state = PieceState.IDLE
                piece._cd_finish = cd_finish
                new_grid[r][c] = piece

        self._grid = new_grid

        # ── rebuild motion stubs ──────────────────────────────────────────────
        # For motions we need the same Piece instances that are in the grid.
        # Moving pieces are NOT in the grid (they're in-flight), so we look
        # them up by sprite_key using a separate counter.
        motion_counters: dict[str, int] = {}

        def _piece_for_motion(key: str) -> Piece:
            idx = motion_counters.get(key, 0)
            motion_counters[key] = idx + 1
            return self._get_or_create(key, idx)

        self._active_moves = [
            _MoveMotionStub(
                piece=_piece_for_motion(m["key"]),
                origin=m["origin"],
                destination=m["destination"],
                actual_destination=m["actual_dest"],
                finish_time=m["finish_time"],
            )
            for m in motions.get("moves", [])
        ]

        self._active_jumps = [
            _JumpMotionStub(
                piece=_piece_for_motion(m["key"]),
                cell=m["cell"],
            )
            for m in motions.get("jumps", [])
        ]

    def apply_game_over(self, winner: str) -> None:
        self.game_over    = True
        self.winner_color = winner

    # ── interface expected by PieceRenderer ───────────────────────────────────

    def snapshot(self) -> list:
        return [row[:] for row in self._grid]

    def active_moves(self) -> list:
        return self._active_moves

    def active_jumps(self) -> list:
        return self._active_jumps

    def cooldown_progress(self, piece) -> tuple | None:
        cd_finish = getattr(piece, "_cd_finish", None)
        if cd_finish is None:
            return None
        state = piece.state.value
        if state == "long_rest":
            duration  = config.LONG_REST_DURATION
            rest_type = "long"
        elif state == "short_rest":
            duration  = config.SHORT_REST_DURATION
            rest_type = "short"
        else:
            return None
        elapsed  = duration - (cd_finish - self.current_time)
        progress = max(0.0, min(1.0, elapsed / duration))
        return progress, rest_type

    def get_piece_at(self, cell: tuple) -> Piece:
        r, c = cell
        if not self.is_inside(cell):
            return Piece.EMPTY
        return self._grid[r][c] or Piece.EMPTY

    def is_inside(self, cell: tuple) -> bool:
        r, c = cell
        return 0 <= r < self.ROWS and 0 <= c < self.COLS
