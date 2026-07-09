from enum import Enum
from abc import ABC, abstractmethod

class CommandType(Enum):
    MOVE = "move"
    JUMP = "jump"
    SHORT_BREAK = "short_break"
    WAIT = "wait"
    CLICK = "click"
    PRINT_BOARD = "print_board"


class Command(ABC):

    def __init__(self, command_type, parameters=None):
        self._command_type = command_type
        self._parameters = parameters or []

    @property
    def command_type(self):
        return self._command_type

    @property
    def parameters(self):
        return self._parameters.copy()

    def __repr__(self):
        return f"Command(type={self._command_type}, parameters={self._parameters})"

    @abstractmethod
    def execute(self, game, controller=None):
        pass