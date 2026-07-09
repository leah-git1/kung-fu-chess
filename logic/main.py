import sys
import config

from board.board_parser import BoardParser
from board.board_validator import BoardValidator
from errors.board_error import BoardError
from errors.parse_error import ParseError
from errors.command_error import CommandError
from commands.command_parser import CommandParser
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from game.game import Game


def main():
    lines = sys.stdin.readlines()

    try:
        board = BoardParser().parse(lines)
        BoardValidator().validate(board)
    except (BoardError, ParseError) as e:
        print(e, file=sys.stderr)
        return

    game = Game(board)
    controller = InputController(BoardMapper(config.CELL_SIZE))

    try:
        commands = CommandParser().parse(lines)
    except CommandError as e:
        print(e, file=sys.stderr)
        return

    for command in commands:
        command.execute(game, controller)


if __name__ == "__main__":
    main()
