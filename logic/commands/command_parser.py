from commands.click_command import ClickCommand
from commands.jump_command import JumpCommand
from commands.wait_command import WaitCommand
from commands.print_command import PrintBoardCommand
from errors.command_error import CommandError
import config


class CommandParser:

    COMMAND_MAP = {
        "click":  ClickCommand,
        "jump":   JumpCommand,
        "wait":   WaitCommand,
        "print":  PrintBoardCommand,
    }

    def __init__(self, output=print):
        self._output = output

    def parse(self, lines):
        commands = []
        reading_commands = False

        for line in lines:
            line = line.strip()
            if line == config.COMMANDS_HEADER:
                reading_commands = True
                continue
            if not reading_commands or not line:
                continue
            commands.append(self._parse_command(line))

        return commands

    def _parse_command(self, line):
        parts = line.split()
        command_cls = self.COMMAND_MAP.get(parts[0].lower())
        if command_cls is None:
            raise CommandError(f"Unknown command: '{parts[0]}'")
        if command_cls is PrintBoardCommand:
            return PrintBoardCommand(self._output)
        return command_cls.from_parameters(parts[1:])
