import config

from board.board_parser import BoardParser
from board.board_validator import BoardValidator
from commands.command_parser import CommandParser
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from errors.board_error import BoardError
from errors.command_error import CommandError
from errors.parse_error import ParseError
from game.game import Game


class ScriptRunner:
    """Runs a parsed script through the real system and writes output via the provided print function.

    Flow: BoardParser -> Board -> Game -> Commands -> Command.execute() -> BoardPrinter
    Never bypasses Controller, Game, RuleEngine, or RealTimeArbiter."""

    def run(self, board_lines: list, command_lines: list, output=print) -> None:
        try:
            board = BoardParser().parse(board_lines)
            BoardValidator().validate(board)
        except (BoardError, ParseError) as e:
            output(str(e))
            return

        game = Game(board)
        controller = InputController(BoardMapper(config.CELL_SIZE))

        try:
            commands = CommandParser(output).parse(command_lines)
        except CommandError as e:
            output(str(e))
            return

        for command in commands:
            command.execute(game, controller)
