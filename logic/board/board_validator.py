from board.piece import Piece
from errors.board_error import BoardError


class BoardValidator:

    def validate(self, board):
        self._validate_row_width(board)
        self._validate_tokens(board)

    def _validate_row_width(self, board):
        if not board.grid:
            return
        expected_width = len(board.grid[0])
        if not all(len(row) == expected_width for row in board.grid):
            raise BoardError("ERROR ROW_WIDTH_MISMATCH")

    def _validate_tokens(self, board):
        if not all(isinstance(cell, Piece) for row in board.grid for cell in row):
            raise BoardError("Invalid token in board")