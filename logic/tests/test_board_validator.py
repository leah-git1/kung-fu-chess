from board.board import Board
from board.board_validator import BoardValidator
from logic.board.piece import Piece
from logic.board.piece_type import PieceType


def test_valid_board():

    board = Board([
        [Piece("w", PieceType.KING), Piece.EMPTY, Piece("b", PieceType.KING)],
        [Piece.EMPTY, Piece("w", PieceType.PAWN), Piece.EMPTY]
    ])

    validator = BoardValidator()

    assert validator.validate(board)



def test_row_width_mismatch():

    board = Board([
        ["wK",".","bK"],
        [".","wP"]
    ])

    validator = BoardValidator()

    assert not validator.validate(board)



def test_unknown_token():

    board = Board([
        ["wK","XXX","bK"]
    ])

    validator = BoardValidator()

    assert not validator.validate(board)