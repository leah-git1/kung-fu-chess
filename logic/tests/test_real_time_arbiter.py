from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType
from rules.real_time_arbiter import RealTimeArbiter


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Board(grid)


# ------------------------------------------------------------------
# is_any_moving
# ------------------------------------------------------------------

def test_no_motions_not_moving():
    arbiter = RealTimeArbiter()
    assert not arbiter.is_any_moving()


def test_move_added_is_moving():
    arbiter = RealTimeArbiter()
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    assert arbiter.is_any_moving()


def test_jump_only_not_moving():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert not arbiter.is_any_moving()


# ------------------------------------------------------------------
# is_airborne
# ------------------------------------------------------------------

def test_cell_not_airborne_initially():
    arbiter = RealTimeArbiter()
    assert not arbiter.is_airborne((0, 0))


def test_cell_airborne_after_jump():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert arbiter.is_airborne((0, 0))


def test_different_cell_not_airborne():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert not arbiter.is_airborne((0, 1))


# ------------------------------------------------------------------
# advance — move arrival
# ------------------------------------------------------------------

def test_move_applies_to_board_on_arrival():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(1000, board)
    assert board.get_piece(0, 7) == _p("wR")
    assert board.get_piece(0, 0) is Piece.EMPTY


def test_move_not_applied_before_finish_time():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(999, board)
    assert board.get_piece(0, 0) == _p("wR")
    assert board.get_piece(0, 7) is Piece.EMPTY


def test_move_cleared_from_active_after_arrival():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(1000, board)
    assert not arbiter.is_any_moving()


# ------------------------------------------------------------------
# advance — capture events
# ------------------------------------------------------------------

def test_enemy_at_destination_is_captured():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "bP"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, _ = arbiter.advance(1000, board)
    assert _p("bP") in captured


def test_friendly_at_destination_cancels_move():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "wP"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 0
    assert board.get_piece(0, 7) == _p("wP")


# ------------------------------------------------------------------
# advance — airborne interception
# ------------------------------------------------------------------

def test_airborne_enemy_intercepts_arriving_piece():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 2): "bR"})
    arbiter.add_jump(_p("bR"), (0, 0), finish_time=2000)
    arbiter.add_move(_p("wR"), (0, 2), (0, 0), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert _p("wR") in captured
    assert len(applied) == 0


def test_no_interception_same_color():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wP"), (0, 7), finish_time=2000)
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0


# ------------------------------------------------------------------
# advance — jump clears after finish
# ------------------------------------------------------------------

def test_jump_clears_after_finish():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    arbiter.advance(1000, board)
    assert not arbiter.is_airborne((0, 0))
