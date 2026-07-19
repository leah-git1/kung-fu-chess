"""
Tests for client/network/board_mirror.py

No logic-layer imports — BoardMirror now depends only on shared/ and its own
view model (PieceVM).
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

from client.network.board_mirror import BoardMirror
from shared.constants import LONG_REST_DURATION, SHORT_REST_DURATION


# ── helpers ───────────────────────────────────────────────────────────────────

def _cell(key, state="idle"):
    return {"k": key, "s": state}


def _empty_board():
    return [[None] * 8 for _ in range(8)]


def _board_with(placements: dict):
    rows = _empty_board()
    for (r, c), token in placements.items():
        rows[r][c] = _cell(token)
    return rows


def _move(key, origin, dest, actual=None, start=0, finish=600):
    return {
        "key": key,
        "origin": list(origin),
        "destination": list(dest),
        "actual_dest": list(actual or dest),
        "start_time": start,
        "finish_time": finish,
    }


def _jump(key, cell, finish=1000):
    return {"key": key, "cell": list(cell), "finish_time": finish}


def _cd(key, rest_type="long", start=0, finish=None):
    if finish is None:
        finish = start + (LONG_REST_DURATION if rest_type == "long" else SHORT_REST_DURATION)
    return {"key": key, "rest_type": rest_type, "start_time": start, "finish_time": finish}


def _no_motions():
    return {"moves": [], "jumps": [], "cooldowns": []}


# ── grid ──────────────────────────────────────────────────────────────────────

def test_empty_board_all_none():
    m = BoardMirror()
    m.apply_state_update(_empty_board(), time_ms=0)
    assert all(m._grid[r][c] is None for r in range(8) for c in range(8))


def test_piece_placed_at_correct_cell():
    m = BoardMirror()
    m.apply_state_update(_board_with({(3, 4): "wR"}), time_ms=0)
    assert m.get_piece_at((3, 4)).sprite_key == "wR"


def test_piece_state_name_set_from_snapshot():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    board[0][0]["s"] = "long_rest"
    m.apply_state_update(board, time_ms=0)
    assert m.get_piece_at((0, 0)).state_name == "long_rest"


def test_invalid_state_stored_as_given():
    # BoardMirror no longer validates state names — it stores whatever the server sends
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    board[0][0]["s"] = "not_a_state"
    m.apply_state_update(board, time_ms=0)
    assert m.get_piece_at((0, 0)).state_name == "not_a_state"


def test_current_time_updated():
    m = BoardMirror()
    m.apply_state_update(_empty_board(), time_ms=999)
    assert m.current_time == 999


# ── piece identity stability ──────────────────────────────────────────────────

def test_same_piece_vm_reused_across_snapshots():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    m.apply_state_update(board, time_ms=0)
    p1 = m.get_piece_at((0, 0))
    m.apply_state_update(board, time_ms=50)
    p2 = m.get_piece_at((0, 0))
    assert p1 is p2


def test_two_pieces_same_type_distinct_objects():
    m = BoardMirror()
    m.apply_state_update(_board_with({(0, 0): "wP", (0, 1): "wP"}), time_ms=0)
    assert m.get_piece_at((0, 0)) is not m.get_piece_at((0, 1))


def test_piece_vm_stable_after_state_change():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    m.apply_state_update(board, time_ms=0)
    p1 = m.get_piece_at((0, 0))
    board[0][0]["s"] = "long_rest"
    m.apply_state_update(board, time_ms=50)
    assert m.get_piece_at((0, 0)) is p1


# ── snapshot / get_piece_at / is_inside ───────────────────────────────────────

def test_snapshot_is_a_copy():
    m = BoardMirror()
    m.apply_state_update(_board_with({(0, 0): "wR"}), time_ms=0)
    snap = m.snapshot()
    snap[0][0] = None
    assert m.get_piece_at((0, 0)) is not None


def test_get_piece_at_out_of_bounds_returns_none():
    m = BoardMirror()
    m.apply_state_update(_empty_board(), time_ms=0)
    assert m.get_piece_at((9, 9)) is None


def test_is_inside_valid():
    m = BoardMirror()
    assert m.is_inside((0, 0)) is True
    assert m.is_inside((7, 7)) is True


def test_is_inside_invalid():
    m = BoardMirror()
    assert m.is_inside((8, 0)) is False
    assert m.is_inside((-1, 0)) is False


# ── move stubs ────────────────────────────────────────────────────────────────

def test_move_stub_created():
    m = BoardMirror()
    motions = {"moves": [_move("wR", (0, 0), (0, 4))], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    assert len(m.active_moves()) == 1


def test_move_stub_not_recreated_on_repeat_snapshot():
    m = BoardMirror()
    motions = {"moves": [_move("wR", (0, 0), (0, 4))], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    stub1 = m.active_moves()[0]
    m.apply_state_update(_empty_board(), time_ms=50, motions=motions)
    stub2 = m.active_moves()[0]
    assert stub1 is stub2


def test_move_stub_start_time_preserved():
    m = BoardMirror()
    motions = {"moves": [_move("wR", (0, 0), (0, 4), start=100, finish=700)], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    m.apply_state_update(_empty_board(), time_ms=50, motions=motions)
    assert m.active_moves()[0].start_time == 100


def test_move_stub_actual_dest_updated():
    m = BoardMirror()
    motions = {"moves": [_move("wR", (0, 0), (0, 4), actual=(0, 4))], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    motions2 = {"moves": [_move("wR", (0, 0), (0, 4), actual=(0, 2))], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=50, motions=motions2)
    assert m.active_moves()[0].actual_destination == (0, 2)


def test_move_stub_removed_when_gone():
    m = BoardMirror()
    motions = {"moves": [_move("wR", (0, 0), (0, 4))], "jumps": [], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    m.apply_state_update(_empty_board(), time_ms=700, motions=_no_motions())
    assert m.active_moves() == []


# ── jump stubs ────────────────────────────────────────────────────────────────

def test_jump_stub_created():
    m = BoardMirror()
    motions = {"moves": [], "jumps": [_jump("wR", (0, 0))], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    assert len(m.active_jumps()) == 1


def test_jump_stub_not_recreated():
    m = BoardMirror()
    motions = {"moves": [], "jumps": [_jump("wR", (0, 0))], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    j1 = m.active_jumps()[0]
    m.apply_state_update(_empty_board(), time_ms=50, motions=motions)
    j2 = m.active_jumps()[0]
    assert j1 is j2


def test_jump_stub_removed_when_gone():
    m = BoardMirror()
    motions = {"moves": [], "jumps": [_jump("wR", (0, 0))], "cooldowns": []}
    m.apply_state_update(_empty_board(), time_ms=0, motions=motions)
    m.apply_state_update(_empty_board(), time_ms=1100, motions=_no_motions())
    assert m.active_jumps() == []


# ── cooldown stubs ────────────────────────────────────────────────────────────

def test_cooldown_stub_created():
    m = BoardMirror()
    board = _board_with({(0, 2): "wR"})
    board[0][2]["s"] = "long_rest"
    motions = {"moves": [], "jumps": [], "cooldowns": [_cd("wR")]}
    m.apply_state_update(board, time_ms=0, motions=motions)
    assert len(m._cd_vms) == 1


def test_cooldown_stub_not_recreated():
    m = BoardMirror()
    board = _board_with({(0, 2): "wR"})
    board[0][2]["s"] = "long_rest"
    cd = _cd("wR", finish=2600)
    motions = {"moves": [], "jumps": [], "cooldowns": [cd]}
    m.apply_state_update(board, time_ms=0, motions=motions)
    stub1 = list(m._cd_vms.values())[0]
    m.apply_state_update(board, time_ms=50, motions=motions)
    stub2 = list(m._cd_vms.values())[0]
    assert stub1 is stub2


def test_cooldown_progress_at_midpoint():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    board[0][0]["s"] = "long_rest"
    half = LONG_REST_DURATION // 2
    motions = {"moves": [], "jumps": [], "cooldowns": [_cd("wR", "long", start=0, finish=LONG_REST_DURATION)]}
    m.apply_state_update(board, time_ms=half, motions=motions)
    piece = m.get_piece_at((0, 0))
    progress, rest_type = m.cooldown_progress(piece)
    assert rest_type == "long"
    assert abs(progress - 0.5) < 0.01


def test_cooldown_progress_short_rest_at_start():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    board[0][0]["s"] = "short_rest"
    motions = {"moves": [], "jumps": [], "cooldowns": [_cd("wR", "short", start=0)]}
    m.apply_state_update(board, time_ms=0, motions=motions)
    piece = m.get_piece_at((0, 0))
    progress, rest_type = m.cooldown_progress(piece)
    assert rest_type == "short"
    assert progress == 0.0


def test_cooldown_progress_none_for_idle_piece():
    m = BoardMirror()
    m.apply_state_update(_board_with({(0, 0): "wR"}), time_ms=0)
    assert m.cooldown_progress(m.get_piece_at((0, 0))) is None


def test_cooldown_progress_clamped_to_one():
    m = BoardMirror()
    board = _board_with({(0, 0): "wR"})
    board[0][0]["s"] = "long_rest"
    motions = {"moves": [], "jumps": [], "cooldowns": [_cd("wR", "long", start=0, finish=100)]}
    m.apply_state_update(board, time_ms=9999, motions=motions)
    progress, _ = m.cooldown_progress(m.get_piece_at((0, 0)))
    assert progress == 1.0


def test_cooldown_stub_removed_when_gone():
    m = BoardMirror()
    board = _board_with({(0, 2): "wR"})
    board[0][2]["s"] = "long_rest"
    motions = {"moves": [], "jumps": [], "cooldowns": [_cd("wR")]}
    m.apply_state_update(board, time_ms=0, motions=motions)
    m.apply_state_update(_board_with({(0, 2): "wR"}), time_ms=3000, motions=_no_motions())
    assert m._cd_vms == {}


# ── apply_game_over ───────────────────────────────────────────────────────────

def test_apply_game_over_white_wins():
    m = BoardMirror()
    m.apply_game_over("w")
    assert m.game_over is True
    assert m.winner_color == "w"


def test_apply_game_over_black_wins():
    m = BoardMirror()
    m.apply_game_over("b")
    assert m.winner_color == "b"
