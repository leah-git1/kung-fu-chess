"""
PieceVM — the client's own view model for a chess piece.

Contains only what the renderer needs:
  sprite_key  : str   e.g. "wR", "bK"
  state_name  : str   e.g. "idle", "moving", "long_rest"

No dependency on logic/board/piece.py or any other logic-layer module.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PieceVM:
    sprite_key: str   
    state_name: str   
