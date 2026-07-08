from board.board import Board
from board.board_validator import BoardValidator



def test_valid_board():

    board = Board([
        ["wK",".","bK"],
        [".","wP","."]
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