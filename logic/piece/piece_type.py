from enum import Enum

from piece.movement_strategy import (
    KingMovement,
    RookMovement,
    BishopMovement,
    QueenMovement,
    KnightMovement,
)


class PieceType(Enum):
    KING   = "K"
    QUEEN  = "Q"
    ROOK   = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN   = "P"


_STRATEGY_MAP = {
    PieceType.KING:   KingMovement,
    PieceType.QUEEN:  QueenMovement,
    PieceType.ROOK:   RookMovement,
    PieceType.BISHOP: BishopMovement,
    PieceType.KNIGHT: KnightMovement,
}


class MovementStrategyFactory:

    @staticmethod
    def for_token(token: str):
        """
        Returns the MovementStrategy for a piece token (e.g. 'wK', 'bR').
        Returns None for tokens without a registered strategy (e.g. pawn, empty).
        """
        if len(token) < 2:
            return None
        type_char = token[1]
        try:
            piece_type = PieceType(type_char)
        except ValueError:
            return None
        strategy_cls = _STRATEGY_MAP.get(piece_type)
        return strategy_cls() if strategy_cls else None
