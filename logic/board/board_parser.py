from board.board import Board
from piece.piece import Piece
from piece.piece_type import PieceType
import config

class BoardParser:


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


        return Board(grid)


    def _parse_cell(self, token: str):
        if token == config.EMPTY_CELL:
            return Piece.EMPTY
        color = token[0]
        piece_type = PieceType(token[1])
        return Piece(color, piece_type)