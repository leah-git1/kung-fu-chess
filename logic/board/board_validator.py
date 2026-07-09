from board.piece import Piece


class BoardValidator:

    def validate(self, board):
        return self._validate_row_width(board) and self._validate_tokens(board)

    def _validate_row_width(self, board):
        if not board.grid:
            return True
        expected_width = len(board.grid[0])
        return all(len(row) == expected_width for row in board.grid)

    def _validate_tokens(self, board):
        return all(
            isinstance(cell, Piece)
            for row in board.grid
            for cell in row
        )