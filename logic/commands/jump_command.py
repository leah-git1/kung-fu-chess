from commands.commands import Command, CommandType


class JumpCommand(Command):

    CELL_SIZE = 100

    def __init__(self, x, y):
        super().__init__(CommandType.JUMP, [x, y])
        self.x = x
        self.y = y

    def execute(self, game):
        row = self.y // self.CELL_SIZE
        col = self.x // self.CELL_SIZE
        game.handle_jump(row, col)
