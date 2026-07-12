from commands.commands import Command


class WaitCommand(Command):

    def __init__(self, milliseconds):
        self.milliseconds = milliseconds

    @classmethod
    def from_parameters(cls, parts: list):
        return cls(int(parts[0]))

    def execute(self, game, controller=None) -> None:
        game.advance_time(self.milliseconds)
