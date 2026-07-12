import sys
from texttests.script_parser import ScriptParser
from texttests.script_runner import ScriptRunner


def main(stream=sys.stdin):
    lines = stream.readlines()
    board_lines, command_lines, _ = ScriptParser().parse(lines)
    ScriptRunner().run(board_lines, command_lines)


if __name__ == "__main__":
    main()
