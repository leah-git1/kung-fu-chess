from board.piece import Piece
from board.piece_type import PieceType


def _p(color, pt):
    return Piece(color, pt)


def test_same_piece_type_and_color_are_equal():
    assert _p("w", PieceType.KING) == _p("w", PieceType.KING)


def test_different_color_are_not_equal():
    assert _p("w", PieceType.KING) != _p("b", PieceType.KING)


def test_different_type_are_not_equal():
    assert _p("w", PieceType.KING) != _p("w", PieceType.ROOK)


def test_empty_equals_empty():
    assert Piece.EMPTY == Piece.EMPTY


def test_empty_not_equal_to_piece():
    assert Piece.EMPTY != _p("w", PieceType.KING)


def test_repr_piece():
    assert repr(_p("w", PieceType.KING)) == "wK"


def test_repr_empty():
    assert repr(Piece.EMPTY) == "."


def test_same_color_true():
    assert _p("w", PieceType.KING).is_same_color(_p("w", PieceType.ROOK))


def test_same_color_false_different_color():
    assert not _p("w", PieceType.KING).is_same_color(_p("b", PieceType.KING))


def test_same_color_false_with_empty():
    assert not _p("w", PieceType.KING).is_same_color(Piece.EMPTY)


def test_piece_is_hashable():
    s = {_p("w", PieceType.KING), _p("w", PieceType.KING)}
    assert len(s) == 1


def test_empty_is_hashable():
    s = {Piece.EMPTY, Piece.EMPTY}
    assert len(s) == 1
