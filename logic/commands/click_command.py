from commands.commands import Command, CommandType


class ClickCommand(Command):

    def __init__(self, x: int, y: int):
        super().__init__(CommandType.CLICK, [x, y])
        self.x = x
        self.y = y

    def execute(self, game, controller) -> None:
        controller.on_click(self.x, self.y, game)
