from commands.commands import Command, CommandType


class WaitCommand(Command):


    def __init__(self, milliseconds):

        super().__init__(
            CommandType.WAIT,
            [milliseconds]
        )

        self.milliseconds = milliseconds



    def execute(self, game, controller=None) -> None:
        game.advance_time(self.milliseconds)