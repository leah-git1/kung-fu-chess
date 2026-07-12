from board.board_printer import BoardPrinter
from board.piece import Piece
from board.piece_type import PieceType


_printer = BoardPrinter()


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def test_empty_cell_renders_as_dot():
    snapshot = [[Piece.EMPTY]]
    assert _printer.render(snapshot) == "."


def test_piece_renders_as_token():
    snapshot = [[_p("wK")]]
    assert _printer.render(snapshot) == "wK"


def test_row_cells_separated_by_space():
    snapshot = [[_p("wK"), Piece.EMPTY, _p("bK")]]
    assert _printer.render(snapshot) == "wK . bK"


def test_multiple_rows_separated_by_newline():
    snapshot = [
        [_p("wK"), Piece.EMPTY],
        [Piece.EMPTY, _p("bK")],
    ]
    assert _printer.render(snapshot) == "wK .\n. bK"


def test_all_piece_types_render_correctly():
    pieces = [_p(t) for t in ["wK", "wQ", "wR", "wB", "wN", "wP"]]
    snapshot = [pieces]
    assert _printer.render(snapshot) == "wK wQ wR wB wN wP"


def test_parser_printer_roundtrip():
    from board.board_parser import BoardParser
    lines = ["Board:", "wK . bK", ". wP .", "Commands:"]
    board = BoardParser().parse(lines)
    output = _printer.render([row[:] for row in board.grid])
    assert output == "wK . bK\n. wP ."
