import pytest
from board.board import Board
from board.board_validator import BoardValidator
from board.piece import Piece
from board.piece_type import PieceType
from errors.board_error import BoardError


_v = BoardValidator()


def _piece(color, pt):
    return Piece(color, pt)


def test_valid_board_passes():
    board = Board([
        [_piece("w", PieceType.KING), Piece.EMPTY, _piece("b", PieceType.KING)],
        [Piece.EMPTY, _piece("w", PieceType.PAWN), Piece.EMPTY],
    ])
    _v.validate(board)  # should not raise


def test_row_width_mismatch_fails():
    board = Board([
        [_piece("w", PieceType.KING), Piece.EMPTY],
        [Piece.EMPTY],
    ])
    with pytest.raises(BoardError):
        _v.validate(board)


def test_raw_string_in_cell_fails():
    board = Board([["wK", Piece.EMPTY]])
    with pytest.raises(BoardError):
        _v.validate(board)


def test_empty_board_passes():
    board = Board([[Piece.EMPTY] * 3 for _ in range(3)])
    _v.validate(board)  # should not raise


def test_single_cell_board_passes():
    board = Board([[_piece("w", PieceType.KING)]])
    _v.validate(board)  # should not raise
