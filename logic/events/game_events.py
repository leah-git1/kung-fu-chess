from dataclasses import dataclass


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

@dataclass(frozen=True)
class GameStartedEvent:
    pass

@dataclass(frozen=True)
class GameOverEvent:
    winner_color: str
