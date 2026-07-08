from board.piece_registry import PieceRegistry


class BoardValidator:

    """
    Responsible only for validating board state.

    Does not parse input.
    Does not create boards.
    Does not know how pieces move.
    """

    ROW_WIDTH_ERROR = "ERROR ROW_WIDTH_MISMATCH"
    UNKNOWN_TOKEN_ERROR = "ERROR UNKNOWN_TOKEN"


    def validate(self, board):

        if not self._validate_row_width(board):
            print(self.ROW_WIDTH_ERROR)
            return False


        if not self._validate_tokens(board):
            print(self.UNKNOWN_TOKEN_ERROR)
            return False


        return True



    def _validate_row_width(self, board):
        """
        Checks that all rows have identical size.
        """

        if not board.grid:
            return True


        expected_width = len(board.grid[0])


        for row in board.grid:

            if len(row) != expected_width:
                return False


        return True



    def _validate_tokens(self, board):
        """
        Checks that every cell contains a valid token.
        """

        for row in board.grid:

            for token in row:

                if not PieceRegistry.is_valid(token):
                    return False


        return True