"""
Tests for server/protocol/serializer.py

No network, no asyncio — pure function calls against a real Game instance.
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

import config
from board.board import Board
from board.piece import Piece, PieceState
from board.piece_type import PieceType
from game.game import Game
from server.protocol.serializer import (
    board_to_json, motions_to_json, cooldowns_to_json,
    apply_move, apply_jump, _move_duration,
)
from shared.messages import MoveMsg, JumpMsg


# ── helpers ───────────────────────────────────────────────────────────────────

def _p(token):
    return Piece(token[0], PieceType(token[1]))


def _game(pieces: dict, rows=8, cols=8) -> Game:
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Game(Board(grid))


# ── _move_duration ────────────────────────────────────────────────────────────

def test_move_duration_horizontal():
    assert _move_duration((0, 0), (0, 3)) == 3 * config.MOVE_DURATION_PER_CELL


def test_move_duration_vertical():
    assert _move_duration((0, 0), (4, 0)) == 4 * config.MOVE_DURATION_PER_CELL


def test_move_duration_diagonal_uses_max():
    # diagonal (2,3) -> max(2,3) = 3
    assert _move_duration((0, 0), (2, 3)) == 3 * config.MOVE_DURATION_PER_CELL


# ── board_to_json ─────────────────────────────────────────────────────────────

def test_board_to_json_empty_cell_is_none():
    game = _game({(0, 0): "wR"})
    rows = board_to_json(game)
    assert rows[1][0] is None


def test_board_to_json_piece_has_key_and_state():
    game = _game({(0, 0): "wR"})
    cell = board_to_json(game)[0][0]
    assert cell["k"] == "wR"
    assert cell["s"] == "idle"


def test_board_to_json_moving_piece_state_is_moving():
    # The board still holds the piece at origin while it travels (the arbiter
    # only clears it on arrival). board_to_json reflects that: the cell is
    # present and its state is "moving".
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 4))
    cell = board_to_json(game)[0][0]
    assert cell is not None
    assert cell["s"] == "moving"


def test_board_to_json_cooldown_finish_present_after_arrival():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    game.advance_time(2 * config.MOVE_DURATION_PER_CELL)
    rows = board_to_json(game)
    cell = rows[0][2]
    assert cell is not None
    assert cell["cd_finish"] is not None


def test_board_to_json_no_cooldown_for_idle_piece():
    game = _game({(0, 0): "wR"})
    cell = board_to_json(game)[0][0]
    assert cell["cd_finish"] is None


# ── motions_to_json ───────────────────────────────────────────────────────────

def test_motions_to_json_empty_when_no_motions():
    game = _game({(0, 0): "wR"})
    m = motions_to_json(game)
    assert m["moves"] == [] and m["jumps"] == []


def test_motions_to_json_move_fields():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 4))
    moves = motions_to_json(game)["moves"]
    assert len(moves) == 1
    m = moves[0]
    assert m["key"] == "wR"
    assert m["origin"] == [0, 0]
    assert m["destination"] == [0, 4]
    assert m["actual_dest"] == [0, 4]
    assert m["finish_time"] > m["start_time"]


def test_motions_to_json_start_time_equals_finish_minus_duration():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 4))
    m = motions_to_json(game)["moves"][0]
    expected_duration = 4 * config.MOVE_DURATION_PER_CELL
    assert m["finish_time"] - m["start_time"] == expected_duration


def test_motions_to_json_jump_fields():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_jump(rook, (0, 0))
    jumps = motions_to_json(game)["jumps"]
    assert len(jumps) == 1
    j = jumps[0]
    assert j["key"] == "wR"
    assert j["cell"] == [0, 0]
    assert "finish_time" in j


def test_motions_to_json_clears_after_arrival():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    game.advance_time(2 * config.MOVE_DURATION_PER_CELL)
    assert motions_to_json(game)["moves"] == []


# ── cooldowns_to_json ─────────────────────────────────────────────────────────

def test_cooldowns_to_json_empty_initially():
    game = _game({(0, 0): "wR"})
    assert cooldowns_to_json(game) == []


def test_cooldowns_to_json_long_rest_after_move():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    game.advance_time(2 * config.MOVE_DURATION_PER_CELL)
    cds = cooldowns_to_json(game)
    assert len(cds) == 1
    cd = cds[0]
    assert cd["key"] == "wR"
    assert cd["rest_type"] == "long"
    assert cd["finish_time"] - cd["start_time"] == config.LONG_REST_DURATION


def test_cooldowns_to_json_short_rest_after_jump():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_jump(rook, (0, 0))
    game.advance_time(config.JUMP_DURATION)
    cds = cooldowns_to_json(game)
    assert len(cds) == 1
    assert cds[0]["rest_type"] == "short"
    assert cds[0]["finish_time"] - cds[0]["start_time"] == config.SHORT_REST_DURATION


def test_cooldowns_to_json_empty_after_cooldown_expires():
    game = _game({(0, 0): "wR"})
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    # Advance to arrival, then advance past the full cooldown in a second step
    game.advance_time(2 * config.MOVE_DURATION_PER_CELL)
    game.advance_time(config.LONG_REST_DURATION + 1)
    assert cooldowns_to_json(game) == []


# ── apply_move ────────────────────────────────────────────────────────────────

def test_apply_move_legal_returns_true():
    game = _game({(0, 0): "wR"})
    msg = MoveMsg(from_cell=[0, 0], to_cell=[0, 4])
    assert apply_move(msg, game) is True


def test_apply_move_illegal_returns_false():
    game = _game({(0, 0): "wR"})
    msg = MoveMsg(from_cell=[0, 0], to_cell=[3, 5])  # not a rook move
    assert apply_move(msg, game) is False


def test_apply_move_piece_enters_moving_state():
    game = _game({(0, 0): "wR"})
    msg = MoveMsg(from_cell=[0, 0], to_cell=[0, 4])
    apply_move(msg, game)
    assert game.get_piece_at((0, 0)).state == PieceState.MOVING


def test_apply_move_rejected_when_already_moving():
    game = _game({(0, 0): "wR"})
    msg = MoveMsg(from_cell=[0, 0], to_cell=[0, 4])
    apply_move(msg, game)
    assert apply_move(msg, game) is False


# ── apply_jump ────────────────────────────────────────────────────────────────

def test_apply_jump_returns_true():
    game = _game({(0, 0): "wR"})
    assert apply_jump(JumpMsg(cell=[0, 0]), game) is True


def test_apply_jump_piece_enters_jumping_state():
    game = _game({(0, 0): "wR"})
    apply_jump(JumpMsg(cell=[0, 0]), game)
    assert game.get_piece_at((0, 0)).state == PieceState.JUMPING


def test_apply_jump_rejected_when_already_airborne():
    game = _game({(0, 0): "wR"})
    apply_jump(JumpMsg(cell=[0, 0]), game)
    assert apply_jump(JumpMsg(cell=[0, 0]), game) is False
