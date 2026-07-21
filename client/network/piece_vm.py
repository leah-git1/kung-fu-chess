"""
PieceVM — the client's own view model for a chess piece.

Contains only what the renderer needs:
  sprite_key  : str   e.g. "wR", "bK"
  state_name  : str   e.g. "idle", "moving", "long_rest"

color, value, and piece_type are derived from sprite_key so that
GameEventSource can diff BoardMirror snapshots (same interface as logic Piece).
No dependency on logic/board/piece.py or any other logic-layer module.
"""
from __future__ import annotations
from dataclasses import dataclass

# Standard piece values — mirrors logic/config.py without importing it
_PIECE_VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}


class _PieceType:
    """Minimal stand-in for logic PieceType — only .value is used by GameEventSource."""
    __slots__ = ("value",)

    def __init__(self, value: str):
        self.value = value


@dataclass
class PieceVM:
    sprite_key: str   # e.g. "wR"
    state_name: str   # e.g. "idle"

    @property
    def color(self) -> str:
        return self.sprite_key[0]

    @property
    def value(self) -> int:
        return _PIECE_VALUES.get(self.sprite_key[1], 0)

    @property
    def piece_type(self) -> _PieceType:
        return _PieceType(self.sprite_key[1])
