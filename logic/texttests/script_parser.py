import config
from texttests.base_script_parser import BaseScriptParser

EXPECTED_HEADER = "Expected:"


class ScriptParser(BaseScriptParser):
    """Parses a game script from a list of text lines."""

    def parse(self, lines: list) -> tuple:
        board_lines = []
        command_lines = []
        expected_lines = []

        section = None

        for line in lines:
            stripped = line.strip()

            if stripped == config.BOARD_HEADER:
                section = "board"
                board_lines.append(line)
                continue

            if stripped == config.COMMANDS_HEADER:
                section = "commands"
                command_lines.append(line)
                continue

            if stripped == EXPECTED_HEADER:
                section = "expected"
                continue

            if section == "board":
                board_lines.append(line)
            elif section == "commands":
                command_lines.append(line)
            elif section == "expected":
                expected_lines.append(stripped)

        expected_output = "\n".join(
            line for line in expected_lines if line
        )

        return board_lines, command_lines, expected_output
