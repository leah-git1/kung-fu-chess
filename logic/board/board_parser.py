from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType
from errors.parse_error import ParseError
import config

class BoardParser:
    """Parses a text script into a Board by reading lines between Board: and Commands: headers."""


    def parse(self, lines):

        grid = []

        reading_board = False


        for line in lines:

            line = line.strip()


            if line == config.BOARD_HEADER:
                reading_board = True
                continue


            if line == config.COMMANDS_HEADER:
                break


            if not reading_board:
                continue


            if line == "":
                continue


            grid.append([self._parse_cell(token) for token in line.split()])


        return Board.from_grid(grid)
    

    def _parse_cell(self, token: str):
        if token == config.EMPTY_CELL:
            return Piece.EMPTY
        try:
            color = token[0]
            piece_type = PieceType(token[1])
            return Piece(color, piece_type)
        except (ValueError, IndexError):
            raise ParseError(f"ERROR UNKNOWN_TOKEN")