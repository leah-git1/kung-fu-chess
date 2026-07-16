from abc import ABC
from dataclasses import dataclass, field

@dataclass(frozen=True)
class PieceMovedEvent:
    color: str; origin: tuple; destination: tuple; elapsed_ms: int = 0
    piece_name: str = ""

@dataclass(frozen=True)
class PieceCapturedEvent:
    at_cell: tuple; elapsed_ms: int = 0
    piece_value: int = 0
    by_color: str | None = None
    captured_color: str = ""
    captured_type: str = ""

class GameObserver(ABC):
    def on_piece_moved(self, event): pass
    def on_piece_captured(self, event): pass

class GameSubject:
    def __init__(self):
        self._observers = []
    def add_observer(self, obs):
        self._observers.append(obs)
    def notify_piece_moved(self, event):
        for o in self._observers: o.on_piece_moved(event)
    def notify_piece_captured(self, event):
        for o in self._observers: o.on_piece_captured(event)