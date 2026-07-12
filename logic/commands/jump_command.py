from commands.commands import Command, CommandType


class JumpCommand(Command):

    def __init__(self, x: int, y: int):
        super().__init__(CommandType.JUMP, [x, y])
        self.x = x
        self.y = y

    @classmethod
    def from_parameters(cls, parts: list):
        return cls(int(parts[0]), int(parts[1]))

    def execute(self, game, controller) -> None:
        controller.on_jump(self.x, self.y, game)
