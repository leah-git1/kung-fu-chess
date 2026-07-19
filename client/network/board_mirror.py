from __future__ import annotations
import logging
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))

from board.piece import Piece, PieceState
from board.piece_type import PieceType
import config

_log = logging.getLogger(__name__)


def _make_piece(key: str) -> Piece:
    color    = key[0]
    pt_value = key[1]
    p = Piece(
        color=color,
        piece_type=PieceType(pt_value),
        is_royal=(pt_value in config.ROYAL_PIECE_TYPES),
        forward_direction=config.FORWARD_DIRECTION.get(color, 0),
    )
    _log.debug("Piece CREATED id=%d key=%s", id(p), key)
    return p


# ── lightweight motion stubs (same interface PieceRenderer reads) ─────────────

class _MoveMotionStub:
    def __init__(self, piece, origin, destination, actual_destination, start_time, finish_time):
        self.piece              = piece
        self.origin             = tuple(origin)
        self.destination        = tuple(destination)
        self.actual_destination = tuple(actual_destination)
        self.start_time         = start_time
        self.finish_time        = finish_time


class _JumpMotionStub:
    def __init__(self, piece, cell, finish_time):
        self.piece       = piece
        self.cell        = tuple(cell)
        self.finish_time = finish_time


class _CooldownStub:
    def __init__(self, piece, rest_type, start_time, finish_time):
        self.piece      = piece
        self.rest_type  = rest_type
        self.start_time = start_time
        self.finish_time = finish_time


# ── mirror ────────────────────────────────────────────────────────────────────

class BoardMirror:
    ROWS = 8
    COLS = 8

    def __init__(self):
        self.current_time: int    = 0
        self.game_over: bool      = False
        self.winner_color: str | None = None
        self._grid: list[list]    = [[None] * self.COLS for _ in range(self.ROWS)]
        # stable piece registry: sprite_key -> [Piece, ...]
        self._registry: dict[str, list[Piece]] = {}
        # live motion stubs keyed to survive across snapshots
        self._move_stubs: dict[tuple, _MoveMotionStub] = {}   # (key, origin, dest) -> stub
        self._jump_stubs: dict[tuple, _JumpMotionStub] = {}   # (key, cell) -> stub
        self._cd_stubs:   dict[tuple, _CooldownStub]   = {}   # (key, rest_type, finish) -> stub

    def _get_or_create(self, key: str, index: int) -> Piece:
        bucket = self._registry.setdefault(key, [])
        while len(bucket) <= index:
            bucket.append(_make_piece(key))
        return bucket[index]

    def apply_state_update(self, board: list, time_ms: int, motions: dict = None) -> None:
        self.current_time = time_ms
        motions = motions or {"moves": [], "jumps": [], "cooldowns": []}

        # ── rebuild grid with stable piece instances ──────────────────────────
        new_grid = [[None] * self.COLS for _ in range(self.ROWS)]
        counters: dict[str, int] = {}

        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell is None:
                    continue
                key        = cell["k"] if isinstance(cell, dict) else cell
                state_name = cell.get("s", "idle") if isinstance(cell, dict) else "idle"
                idx        = counters.get(key, 0)
                counters[key] = idx + 1
                piece = self._get_or_create(key, idx)
                try:
                    piece.state = PieceState(state_name)
                except ValueError:
                    piece.state = PieceState.IDLE
                new_grid[r][c] = piece

        self._grid = new_grid

        # ── update move stubs — preserve existing ones, add new, drop finished ─
        motion_counters: dict[str, int] = {}

        def _piece_for_motion(key: str) -> Piece:
            idx = motion_counters.get(key, 0)
            motion_counters[key] = idx + 1
            return self._get_or_create(key, idx)

        incoming_move_keys = set()
        for m in motions.get("moves", []):
            stub_key = (m["key"], tuple(m["origin"]), tuple(m["destination"]))
            incoming_move_keys.add(stub_key)
            if stub_key not in self._move_stubs:
                _log.debug("MoveMotionStub CREATED %s", stub_key)
                self._move_stubs[stub_key] = _MoveMotionStub(
                    piece=_piece_for_motion(m["key"]),
                    origin=m["origin"],
                    destination=m["destination"],
                    actual_destination=m["actual_dest"],
                    start_time=m.get("start_time", m["finish_time"]),
                    finish_time=m["finish_time"],
                )
            else:
                # update actual_dest in case it changed (blocking piece appeared)
                self._move_stubs[stub_key].actual_destination = tuple(m["actual_dest"])
        self._move_stubs = {k: v for k, v in self._move_stubs.items() if k in incoming_move_keys}

        incoming_jump_keys = set()
        for m in motions.get("jumps", []):
            stub_key = (m["key"], tuple(m["cell"]))
            incoming_jump_keys.add(stub_key)
            if stub_key not in self._jump_stubs:
                _log.debug("JumpMotionStub CREATED %s", stub_key)
                self._jump_stubs[stub_key] = _JumpMotionStub(
                    piece=_piece_for_motion(m["key"]),
                    cell=m["cell"],
                    finish_time=m.get("finish_time", time_ms + config.JUMP_DURATION),
                )
        self._jump_stubs = {k: v for k, v in self._jump_stubs.items() if k in incoming_jump_keys}

        incoming_cd_keys = set()
        for m in motions.get("cooldowns", []):
            stub_key = (m["key"], m["rest_type"], m["finish_time"])
            incoming_cd_keys.add(stub_key)
            if stub_key not in self._cd_stubs:
                _log.debug("CooldownStub CREATED %s", stub_key)
                self._cd_stubs[stub_key] = _CooldownStub(
                    piece=_piece_for_motion(m["key"]),
                    rest_type=m["rest_type"],
                    start_time=m["start_time"],
                    finish_time=m["finish_time"],
                )
        self._cd_stubs = {k: v for k, v in self._cd_stubs.items() if k in incoming_cd_keys}

    def apply_game_over(self, winner: str) -> None:
        self.game_over    = True
        self.winner_color = winner

    # ── interface expected by PieceRenderer ───────────────────────────────────

    def snapshot(self) -> list:
        return [row[:] for row in self._grid]

    def active_moves(self) -> list:
        return list(self._move_stubs.values())

    def active_jumps(self) -> list:
        return list(self._jump_stubs.values())

    def cooldown_progress(self, piece) -> tuple | None:
        for stub in self._cd_stubs.values():
            if stub.piece is piece:
                duration = (config.LONG_REST_DURATION if stub.rest_type == "long"
                            else config.SHORT_REST_DURATION)
                elapsed  = duration - (stub.finish_time - self.current_time)
                progress = max(0.0, min(1.0, elapsed / duration))
                return progress, stub.rest_type
        return None

    def get_piece_at(self, cell: tuple) -> Piece:
        r, c = cell
        if not self.is_inside(cell):
            return Piece.EMPTY
        return self._grid[r][c] or Piece.EMPTY

    def is_inside(self, cell: tuple) -> bool:
        r, c = cell
        return 0 <= r < self.ROWS and 0 <= c < self.COLS
