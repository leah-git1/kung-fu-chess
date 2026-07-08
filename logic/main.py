import sys

from board.board_parser import BoardParser
from board.board_validator import BoardValidator

from commands.command_parser import CommandParser

from game.game import Game



def main():

    lines = sys.stdin.readlines()


    # Parse board

    board_parser = BoardParser()

    board = board_parser.parse(lines)



    # Validate board

    validator = BoardValidator()

    if not validator.validate(board):
        return



    # Create game

    game = Game(board)



    # Parse commands

    command_parser = CommandParser()

    commands = command_parser.parse(lines)



    # Execute commands

    for command in commands:

        command.execute(game)



if __name__ == "__main__":

    main()