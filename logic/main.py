import sys
import config

from board.board_parser import BoardParser
from board.board_validator import BoardValidator
from commands.command_parser import CommandParser
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from game.game import Game


def main():
    lines = sys.stdin.readlines()

    board = BoardParser().parse(lines)
    if not BoardValidator().validate(board):
        return

    game = Game(board)
    controller = InputController(BoardMapper(config.CELL_SIZE))
    commands = CommandParser().parse(lines)

    for command in commands:
        command.execute(game, controller)


if __name__ == "__main__":
    main()
