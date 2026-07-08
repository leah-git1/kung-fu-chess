from commands.commands import Command, CommandType


class PrintBoardCommand(Command):


    def __init__(self):

        super().__init__(
            CommandType.PRINT_BOARD
        )



    def execute(self, game):

        game.update_moves()

        game.board.display()