from board.board_parser import BoardParser
from logic.board.piece import Piece
from logic.board.piece_type import PieceType


def test_parse_board():

    lines = [
        "Board:",
        "wK . bK",
        ". wP .",
        "Commands:",
        "wait 1000"
    ]


    parser = BoardParser()

    board = parser.parse(lines)


    assert board.rows == 2
    assert board.cols == 3


    assert board.grid[0] == [
        Piece("w", PieceType.KING),
        Piece.EMPTY,
        Piece("b", PieceType.KING)
    ]