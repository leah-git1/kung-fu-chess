from board.piece_registry import PieceRegistry


def test_existing_piece_is_valid():

    assert PieceRegistry.is_valid("wK")
    assert PieceRegistry.is_valid("bQ")
    assert PieceRegistry.is_valid(".")



def test_unknown_piece_is_invalid():

    assert not PieceRegistry.is_valid("XXX")



def test_register_new_piece():

    PieceRegistry.register_piece("wD")

    assert PieceRegistry.is_valid("wD")