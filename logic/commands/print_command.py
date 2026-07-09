from commands.commands import Command, CommandType
from board.board_printer import BoardPrinter


class PrintBoardCommand(Command):

    def __init__(self):
        super().__init__(CommandType.PRINT_BOARD)
        self._printer = BoardPrinter()

    def execute(self, game, controller=None) -> None:
        print(self._printer.render(game.snapshot()))
