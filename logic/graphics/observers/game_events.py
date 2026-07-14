from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class PieceMovedEvent:
    piece: object; origin: tuple; destination: tuple

@dataclass(frozen=True)
class PieceCapturedEvent:
    captured_piece: object; at_cell: tuple; by_piece: object = None

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