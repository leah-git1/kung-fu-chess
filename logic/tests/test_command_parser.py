from commands.command_parser import CommandParser
from commands.commands import CommandType



def test_parse_commands():

    lines = [
        "Commands:",
        "jump 50 150",
        "wait 1000"
    ]


    parser = CommandParser()

    commands = parser.parse(lines)


    assert len(commands) == 2


    assert commands[0].command_type == CommandType.JUMP

    assert commands[0].parameters == [
        50,
        150
    ]


    assert commands[1].command_type == CommandType.WAIT