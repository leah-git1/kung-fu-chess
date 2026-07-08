from commands.commands import Command, CommandType
from commands.click_command import ClickCommand
from commands.jump_command import JumpCommand
from commands.wait_command import WaitCommand
from commands.print_command import PrintBoardCommand

class CommandParser:


    COMMAND_MAP = {
        "move": CommandType.MOVE,
        "jump": CommandType.JUMP,
        "shortbreak": CommandType.SHORT_BREAK,
        "wait": CommandType.WAIT,
        "click": CommandType.CLICK,
        "print": CommandType.PRINT_BOARD
    }



    def parse(self, lines):

        commands = []

        reading_commands = False


        for line in lines:

            line = line.strip()


            if line == "Commands:":
                reading_commands = True
                continue


            if not reading_commands:
                continue


            if not line:
                continue


            command = self._parse_command(line)

            if command:
                commands.append(command)


        return commands



    def _parse_command(self, line):
        parts = line.split()
        command_name = parts[0].lower()

        if command_name not in self.COMMAND_MAP:
            return None

        command_type = self.COMMAND_MAP[command_name]

        parameters = []
        for value in parts[1:]:
            try:
                parameters.append(int(value))
            except ValueError:
                parameters.append(value)

        if command_type == CommandType.CLICK:
            return ClickCommand(parameters[0], parameters[1])
        elif command_type == CommandType.JUMP:
            return JumpCommand(parameters[0], parameters[1])
        elif command_type == CommandType.WAIT:
            return WaitCommand(parameters[0])
        elif command_type == CommandType.PRINT_BOARD:
            return PrintBoardCommand()
        
        return Command(command_type, parameters)