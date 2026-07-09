from commands.commands import Command, CommandType


class PrintBoardCommand(Command):

    def __init__(self):
        super().__init__(CommandType.PRINT_BOARD)

    def execute(self, game, controller=None) -> None:
        for row in game.snapshot():
            print(" ".join(repr(cell) for cell in row))