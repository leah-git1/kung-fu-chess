from commands.commands import Command
from board.board_printer import BoardPrinter


class PrintBoardCommand(Command):

    def __init__(self, output=print):
        self._printer = BoardPrinter()
        self._output = output

    @classmethod
    def from_parameters(cls, parts: list):
        return cls()

    def execute(self, game, controller=None) -> None:
        self._output(self._printer.render(game.snapshot()))
