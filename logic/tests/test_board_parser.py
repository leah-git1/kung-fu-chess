from board.board_parser import BoardParser


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
        "wK",
        ".",
        "bK"
    ]