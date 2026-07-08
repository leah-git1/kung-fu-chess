from enum import Enum

from piece.movement_strategy import (
    KingMovement,
    RookMovement,
    BishopMovement,
    QueenMovement,
    KnightMovement,
    PawnMovement,
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
    PieceType.PAWN:   PawnMovement,
}


class MovementStrategyFactory:

    @staticmethod
    def for_piece(piece):
        """
        Returns the MovementStrategy for a Piece object.
        Returns None if no strategy is registered for the piece type.
        """
        if piece is None or piece.piece_type is None:
            return None
        strategy_cls = _STRATEGY_MAP.get(piece.piece_type)
        return strategy_cls() if strategy_cls else None

    @staticmethod
    def for_token(token: str):
        """
        Returns the MovementStrategy for a token string like 'wK'.
        Returns None for empty cells or unknown tokens.
        """
        if token == ".":
            return None
        piece = _parse_token(token)
        return MovementStrategyFactory.for_piece(piece) if piece else None


def _parse_token(token: str):
    """Helper to convert a token string to a Piece object for factory lookup."""
    if token == "." or not token or len(token) != 2:
        return None
    try:
        from piece.piece import Piece
        color = token[0]
        piece_type_char = token[1]
        piece_type = None
        for pt in PieceType:
            if pt.value == piece_type_char:
                piece_type = pt
                break
        if piece_type is None:
            return None
        return Piece(color=color, piece_type=piece_type)
    except:
        return None
