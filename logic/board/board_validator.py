from board.piece import Piece
from errors.board_error import BoardError


class BoardValidator:
    """Validates that a Board has consistent row widths and only contains Piece objects."""

    def validate(self, board):
        self._validate_row_width(board)
        self._validate_tokens(board)

    def _validate_row_width(self, board):
        rows = list(board.rows_iter())
        if not rows:
            return
        expected_width = len(rows[0])
        if not all(len(row) == expected_width for row in rows):
            raise BoardError("ERROR ROW_WIDTH_MISMATCH")

    def _validate_tokens(self, board):
        if not all(isinstance(cell, Piece) for row in board.rows_iter() for cell in row):
            raise BoardError("Invalid token in board")