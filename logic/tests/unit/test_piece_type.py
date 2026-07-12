from board.piece_type import PieceType


def test_all_piece_types_exist():
    assert {pt.value for pt in PieceType} == {"K", "Q", "R", "B", "N", "P"}


def test_lookup_by_value():
    assert PieceType("K") == PieceType.KING
    assert PieceType("Q") == PieceType.QUEEN
    assert PieceType("R") == PieceType.ROOK
    assert PieceType("B") == PieceType.BISHOP
    assert PieceType("N") == PieceType.KNIGHT
    assert PieceType("P") == PieceType.PAWN


def test_piece_types_are_distinct():
    values = [pt.value for pt in PieceType]
    assert len(values) == len(set(values))
