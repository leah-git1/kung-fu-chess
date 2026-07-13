from abc import ABC, abstractmethod


class BaseScriptParser(ABC):
    """Defines the contract for parsing a game script from any source."""

    @abstractmethod
    def parse(self, source) -> tuple:
        """Returns (board_lines, command_lines, expected_output)."""
        pass
