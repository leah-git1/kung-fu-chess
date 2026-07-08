from abc import ABC, abstractmethod


class Action(ABC):

    def __init__(self, piece: str, cell, finish_time: int):
        self.piece = piece
        self.cell = cell
        self.finish_time = finish_time
        self.completed = False

    def is_finished(self, current_time: int) -> bool:
        return current_time >= self.finish_time

    @abstractmethod
    def resolve(self, board, captured: list, applied: list):
        """Apply this action's effect when it finishes."""
        pass
