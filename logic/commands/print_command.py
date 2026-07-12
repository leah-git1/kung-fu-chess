from commands.commands import Command, CommandType
from board.board_printer import BoardPrinter


class PrintBoardCommand(Command):
    """Prints the current board state using the provided output function."""

    def __init__(self, output=print):
        super().__init__(CommandType.PRINT_BOARD)
        self._printer = BoardPrinter()
        self._output = output

    @classmethod
    def from_parameters(cls, parts: list):
        return cls()

    def execute(self, game, controller=None) -> None:
        self._output(self._printer.render(game.snapshot()))
