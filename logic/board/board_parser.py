from board.board import Board


class BoardParser:

    BOARD_HEADER = "Board:"
    COMMANDS_HEADER = "Commands:"


    def parse(self, lines):

        grid = []

        reading_board = False


        for line in lines:

            line = line.strip()


            if line == self.BOARD_HEADER:
                reading_board = True
                continue


            if line == self.COMMANDS_HEADER:
                break


            if not reading_board:
                continue


            if line == "":
                continue


            grid.append(line.split())


        return Board(grid)