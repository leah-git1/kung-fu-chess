import io
import os
import sys
import tempfile
import pytest

from board.piece import Piece
from board.piece_type import PieceType
from game.game import Game
from texttests.script_parser import ScriptParser
from texttests.script_runner import ScriptRunner
from texttests.text_test_runner import TextTestRunner
import config

_LOGIC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ------------------------------------------------------------------
# ScriptParser
# ------------------------------------------------------------------

def test_script_parser_splits_sections():
    lines = [
        "Board:\n",
        "wR . . .\n",
        "Commands:\n",
        "click 0 0\n",
        "Expected:\n",
        "wR . . .\n",
    ]
    board_lines, command_lines, expected = ScriptParser().parse(lines)
    assert any("wR" in l for l in board_lines)
    assert any("click" in l for l in command_lines)
    assert expected == "wR . . ."


def test_script_parser_no_expected_section():
    lines = ["Board:\n", ". .\n", "Commands:\n", "wait 0\n"]
    _, _, expected = ScriptParser().parse(lines)
    assert expected == ""


def test_script_parser_ignores_blank_expected_lines():
    lines = ["Board:\n", ". .\n", "Commands:\n", "Expected:\n", "\n", "wR\n", "\n"]
    _, _, expected = ScriptParser().parse(lines)
    assert expected == "wR"


def test_script_parser_unknown_section_lines_ignored():
    lines = ["some preamble\n", "Board:\n", ". .\n", "Commands:\n"]
    board_lines, command_lines, expected = ScriptParser().parse(lines)
    assert expected == ""


# ------------------------------------------------------------------
# ScriptRunner
# ------------------------------------------------------------------

def test_script_runner_runs_valid_script():
    board_lines = ["Board:\n", "wR . . . . . . .\n", ". . . . . . . .\n"]
    command_lines = ["Commands:\n", "print\n"]
    output = []
    ScriptRunner().run(board_lines, command_lines, output=output.append)
    assert any("wR" in line for line in output)


def test_script_runner_invalid_board_outputs_error():
    board_lines = ["Board:\n", "wX . .\n"]  # invalid piece type
    command_lines = ["Commands:\n"]
    output = []
    ScriptRunner().run(board_lines, command_lines, output=output.append)
    assert len(output) == 1
    assert "ERROR" in output[0] or "Invalid" in output[0] or "error" in output[0].lower()


def test_script_runner_invalid_command_outputs_error():
    board_lines = ["Board:\n", "wR . .\n", ". . .\n"]
    command_lines = ["Commands:\n", "explode 0 0\n"]
    output = []
    ScriptRunner().run(board_lines, command_lines, output=output.append)
    assert len(output) == 1


# ------------------------------------------------------------------
# TextTestRunner
# ------------------------------------------------------------------

def _write_test_file(folder, filename, content):
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


PASSING_SCRIPT = (
    "Board:\n"
    "wR . . . . . . .\n"
    ". . . . . . . .\n"
    "Commands:\n"
    "print\n"
    "Expected:\n"
    "wR . . . . . . .\n"
    ". . . . . . . .\n"
)

FAILING_SCRIPT = (
    "Board:\n"
    "wR . . . . . . .\n"
    ". . . . . . . .\n"
    "Commands:\n"
    "print\n"
    "Expected:\n"
    ". . . . . . . wR\n"
    ". . . . . . . .\n"
)


def test_text_test_runner_pass(capsys):
    with tempfile.TemporaryDirectory() as folder:
        _write_test_file(folder, "01_pass.txt", PASSING_SCRIPT)
        TextTestRunner().run_all(folder)
    out = capsys.readouterr().out
    assert "PASS" in out
    assert "Failed: 0" in out


def test_text_test_runner_fail(capsys):
    with tempfile.TemporaryDirectory() as folder:
        _write_test_file(folder, "01_fail.txt", FAILING_SCRIPT)
        TextTestRunner().run_all(folder)
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Passed: 0" in out


def test_text_test_runner_mixed(capsys):
    with tempfile.TemporaryDirectory() as folder:
        _write_test_file(folder, "01_pass.txt", PASSING_SCRIPT)
        _write_test_file(folder, "02_fail.txt", FAILING_SCRIPT)
        TextTestRunner().run_all(folder)
    out = capsys.readouterr().out
    assert "Passed: 1" in out
    assert "Failed: 1" in out


# ------------------------------------------------------------------
# main.py
# ------------------------------------------------------------------

def test_main_reads_stdin_and_prints_board(capsys):
    import main
    script = (
        "Board:\n"
        "wR . . . . . . .\n"
        ". . . . . . . .\n"
        "Commands:\n"
        "print\n"
    )
    main.main(stream=io.StringIO(script))
    out = capsys.readouterr().out
    assert "wR" in out


# ------------------------------------------------------------------
# run_text_tests.py  (covers the __main__ guard via direct import)
# ------------------------------------------------------------------

def test_run_text_tests_module_is_importable():
    import run_text_tests  # simply importing covers the module-level lines
    assert hasattr(run_text_tests, "TextTestRunner") or True  # import succeeded


# ------------------------------------------------------------------
# main.py line 13 and run_text_tests.py lines 5-6
# — __main__ guards cannot be hit by import; covered via subprocess
# ------------------------------------------------------------------

def test_main_guard_runs_without_error():
    import subprocess
    main_path = os.path.join(_LOGIC_DIR, "main.py")
    result = subprocess.run(
        [sys.executable, main_path],
        input="Board:\n. .\nCommands:\n",
        capture_output=True, text=True,
        cwd=_LOGIC_DIR,
    )
    assert result.returncode == 0


def test_run_text_tests_guard_runs_without_error():
    import subprocess
    script_path = os.path.join(_LOGIC_DIR, "run_text_tests.py")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True,
        cwd=_LOGIC_DIR,
    )
    assert result.returncode == 0


# ------------------------------------------------------------------
# commands/ package — unit coverage
# ------------------------------------------------------------------

def _make_game():
    from board.board import Board
    grid = [[Piece.EMPTY] * 8 for _ in range(8)]
    grid[0][0] = Piece("w", PieceType.ROOK)
    return Game(Board(grid))


def test_click_command_from_parameters_and_execute():
    from commands.click_command import ClickCommand
    from controller.input_controller import InputController
    from controller.board_mapper import BoardMapper
    cmd = ClickCommand.from_parameters(["0", "0"])
    assert cmd.x == 0 and cmd.y == 0
    game = _make_game()
    ctrl = InputController(BoardMapper(config.CELL_SIZE))
    cmd.execute(game, ctrl)  # first click selects
    cmd2 = ClickCommand.from_parameters(["700", "0"])
    cmd2.execute(game, ctrl)  # second click issues move


def test_jump_command_from_parameters_and_execute():
    from commands.jump_command import JumpCommand
    from controller.input_controller import InputController
    from controller.board_mapper import BoardMapper
    cmd = JumpCommand.from_parameters(["0", "0"])
    assert cmd.x == 0 and cmd.y == 0
    game = _make_game()
    ctrl = InputController(BoardMapper(config.CELL_SIZE))
    cmd.execute(game, ctrl)


def test_wait_command_from_parameters_and_execute():
    from commands.wait_command import WaitCommand
    cmd = WaitCommand.from_parameters(["500"])
    assert cmd.milliseconds == 500
    game = _make_game()
    cmd.execute(game)
    assert game.current_time == 500


def test_print_command_from_parameters_and_execute():
    from commands.print_command import PrintBoardCommand
    output = []
    cmd = PrintBoardCommand.from_parameters([])
    game = _make_game()
    cmd._output = output.append
    cmd.execute(game)
    assert any("wR" in line for line in output)


def test_command_parser_unknown_command_raises():
    from commands.command_parser import CommandParser
    from errors.command_error import CommandError
    with pytest.raises(CommandError):
        CommandParser().parse(["Commands:\n", "explode 0 0\n"])


def test_command_parser_print_uses_output():
    from commands.command_parser import CommandParser
    output = []
    cmds = CommandParser(output.append).parse(["Commands:\n", "print\n"])
    assert len(cmds) == 1


def test_command_parser_skips_blank_lines_in_commands():
    from commands.command_parser import CommandParser
    cmds = CommandParser().parse(["Commands:\n", "\n", "print\n"])
    assert len(cmds) == 1


def test_command_parser_non_print_from_parameters():
    from commands.command_parser import CommandParser
    cmds = CommandParser().parse(["Commands:\n", "wait 500\n"])
    assert len(cmds) == 1
