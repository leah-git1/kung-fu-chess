from board.board_parser import BoardParser
from board.piece import Piece
from board.piece_type import PieceType


_parser = BoardParser()


def test_parses_correct_dimensions():
    lines = ["Board:", "wK . bK", ". wP .", "Commands:"]
    board = _parser.parse(lines)
    assert board.rows == 2
    assert board.cols == 3


def test_parses_piece_correctly():
    lines = ["Board:", "wK . .", "Commands:"]
    board = _parser.parse(lines)
    assert board.get_piece(0, 0) == Piece("w", PieceType.KING)


def test_parses_empty_cell():
    lines = ["Board:", ". . .", "Commands:"]
    board = _parser.parse(lines)
    assert board.get_piece(0, 1) is Piece.EMPTY


def test_ignores_lines_before_board_header():
    lines = ["some preamble", "Board:", "wR .", "Commands:"]
    board = _parser.parse(lines)
    assert board.rows == 1


def test_stops_at_commands_header():
    lines = ["Board:", "wK .", "Commands:", "wQ ."]
    board = _parser.parse(lines)
    assert board.rows == 1


def test_skips_blank_lines_in_board_section():
    lines = ["Board:", "", "wK .", "", "Commands:"]
    board = _parser.parse(lines)
    assert board.rows == 1


def test_parses_all_piece_types():
    lines = ["Board:", "wK wQ wR wB wN wP", "Commands:"]
    board = _parser.parse(lines)
    expected = [PieceType.KING, PieceType.QUEEN, PieceType.ROOK,
                PieceType.BISHOP, PieceType.KNIGHT, PieceType.PAWN]
    for col, pt in enumerate(expected):
        assert board.get_piece(0, col) == Piece("w", pt)


def test_parses_black_pieces():
    lines = ["Board:", "bK bR", "Commands:"]
    board = _parser.parse(lines)
    assert board.get_piece(0, 0) == Piece("b", PieceType.KING)
    assert board.get_piece(0, 1) == Piece("b", PieceType.ROOK)
