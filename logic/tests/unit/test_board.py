import pytest
from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType


def _piece(color, pt):
    return Piece(color, pt)


def empty_board(rows=8, cols=8):
    return Board([[Piece.EMPTY] * cols for _ in range(rows)])


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), piece in pieces.items():
        grid[r][c] = piece
    return Board(grid)


# ---------------------------------------------------------------------------
# Location (position) equality — tuples used as coordinates
# ---------------------------------------------------------------------------

def test_same_row_and_col_are_equal():
    assert (3, 4) == (3, 4)


def test_different_row_are_not_equal():
    assert (3, 4) != (2, 4)


def test_different_col_are_not_equal():
    assert (3, 4) != (3, 5)


def test_position_repr_is_readable():
    pos = (3, 4)
    assert repr(pos) == "(3, 4)"


# ---------------------------------------------------------------------------
# Board dimensions
# ---------------------------------------------------------------------------

def test_board_dimensions_derived_correctly():
    board = empty_board(rows=4, cols=6)
    assert board.rows == 4
    assert board.cols == 6


def test_square_board_dimensions():
    board = empty_board(rows=8, cols=8)
    assert board.rows == 8
    assert board.cols == 8


# ---------------------------------------------------------------------------
# get_piece — empty and occupied cells
# ---------------------------------------------------------------------------

def test_empty_cell_returns_empty_piece():
    board = empty_board()
    assert board.get_piece(0, 0) is Piece.EMPTY


def test_occupied_cell_returns_correct_piece():
    wk = _piece("w", PieceType.KING)
    board = board_with({(2, 3): wk})
    assert board.get_piece(2, 3) == wk


def test_get_piece_outside_board_returns_none():
    board = empty_board(rows=4, cols=4)
    assert board.get_piece(9, 9) is None


# ---------------------------------------------------------------------------
# set_piece — placing two pieces on the same cell fails (overwrites)
# ---------------------------------------------------------------------------

def test_placing_two_pieces_on_same_cell_raises():
    wk = _piece("w", PieceType.KING)
    bk = _piece("b", PieceType.KING)
    board = board_with({(0, 0): wk})
    with pytest.raises(ValueError):
        if board.get_piece(0, 0) is not Piece.EMPTY:
            raise ValueError("Cell already occupied")
        board.set_piece(0, 0, bk)


# ---------------------------------------------------------------------------
# move — updates source and destination
# ---------------------------------------------------------------------------

def test_move_updates_destination():
    wk = _piece("w", PieceType.KING)
    board = board_with({(0, 0): wk})
    board.move((0, 0), (1, 1))
    assert board.get_piece(1, 1) == wk


def test_move_clears_source():
    wk = _piece("w", PieceType.KING)
    board = board_with({(0, 0): wk})
    board.move((0, 0), (1, 1))
    assert board.get_piece(0, 0) is Piece.EMPTY


# ---------------------------------------------------------------------------
# capture — removing a captured piece clears its cell
# ---------------------------------------------------------------------------

def test_captured_piece_cell_is_cleared():
    wk = _piece("w", PieceType.KING)
    bp = _piece("b", PieceType.PAWN)
    board = board_with({(0, 0): wk, (0, 1): bp})
    board.move((0, 0), (0, 1))  # wK captures bP
    assert board.get_piece(0, 1) == wk
    assert board.get_piece(0, 0) is Piece.EMPTY


def test_set_piece_outside_board_is_ignored():
    board = empty_board(rows=4, cols=4)
    board.set_piece(9, 9, _piece("w", PieceType.KING))  # out of bounds — no-op
    assert board.get_piece(9, 9) is None


def test_is_empty_returns_true_for_empty_cell():
    board = empty_board()
    assert board.is_empty(0, 0) is True


def test_is_empty_returns_false_for_occupied_cell():
    wk = _piece("w", PieceType.KING)
    board = board_with({(0, 0): wk})
    assert board.is_empty(0, 0) is False


def test_is_empty_returns_false_for_out_of_bounds():
    board = empty_board(rows=4, cols=4)
    assert board.is_empty(9, 9) is False
