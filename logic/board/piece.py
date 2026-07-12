from __future__ import annotations
import config

class Piece:
    """Represents a single chess piece with a color and type. The singleton EMPTY represents an empty cell."""

    def __init__(
        self,
        color: str,
        piece_type,
        is_royal: bool = False,
        promotion_type=None,
        forward_direction: int = 0,
    ):
        self.color = color
        self.piece_type = piece_type
        self.is_royal = is_royal
        self.promotion_type = promotion_type
        self.forward_direction = forward_direction

    def is_same_color(self, other: Piece) -> bool:
        if self is Piece.EMPTY or other is Piece.EMPTY:
            return False
        return self.color == other.color

    def __repr__(self):
        if self is Piece.EMPTY:
            return config.EMPTY_CELL
        return self.color + self.piece_type.value

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self is other or (self.color == other.color and self.piece_type == other.piece_type)
        return NotImplemented

    def __hash__(self):
        if self is Piece.EMPTY:
            return hash("__EMPTY__")
        return hash((self.color, self.piece_type))


Piece.EMPTY = Piece(color=config.EMPTY_CELL, piece_type=None)