from commands.commands import Command, CommandType


class ClickCommand(Command):

    def __init__(self, x: int, y: int):
        super().__init__(CommandType.CLICK, [x, y])
        self.x = x
        self.y = y

    @classmethod
    def from_parameters(cls, parts: list):
        return cls(int(parts[0]), int(parts[1]))

    def execute(self, game, controller) -> None:
        controller.on_click(self.x, self.y, game)
