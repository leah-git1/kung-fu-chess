from board.piece_registry import PieceRegistry
from piece.piece import Piece
from piece.piece_type import PieceType


def test_existing_piece_is_valid():
    wk = Piece(color="w", piece_type=PieceType.KING)
    bq = Piece(color="b", piece_type=PieceType.QUEEN)
    empty = Piece.EMPTY

    assert PieceRegistry.is_valid(wk)
    assert PieceRegistry.is_valid(bq)
    assert PieceRegistry.is_valid(empty)


def test_unknown_piece_is_invalid():
    # Invalid color
    invalid = Piece(color="x", piece_type=PieceType.KING)
    assert not PieceRegistry.is_valid(invalid)
    
    # String token is invalid (must be Piece object)
    assert not PieceRegistry.is_valid("wK")


def test_register_new_color():
    PieceRegistry.register_color("r")
    red_king = Piece(color="r", piece_type=PieceType.KING)
    assert PieceRegistry.is_valid(red_king)