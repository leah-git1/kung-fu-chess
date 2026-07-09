from abc import ABC, abstractmethod
import config
from board.piece import Piece
from board.piece_type import PieceType


class MovementStrategy(ABC):

    @abstractmethod
    def is_legal(self, moving_piece, start, end, board) -> bool:
        pass

    def on_arrival(self, piece, destination, board):
        return piece


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _is_straight(start, end) -> bool:
    sr, sc = start
    er, ec = end
    return sr == er or sc == ec


def _is_diagonal(start, end) -> bool:
    sr, sc = start
    er, ec = end
    return abs(er - sr) == abs(ec - sc)


def _path_is_clear(start, end, board) -> bool:
    sr, sc = start
    er, ec = end
    dr = 0 if er == sr else (1 if er > sr else -1)
    dc = 0 if ec == sc else (1 if ec > sc else -1)
    r, c = sr + dr, sc + dc
    while (r, c) != (er, ec):
        if board.get_piece(r, c) is not Piece.EMPTY:
            return False
        r += dr
        c += dc
    return True


def _destination_is_capturable(moving_piece, end, board) -> bool:
    target = board.get_piece(*end)
    return target is Piece.EMPTY or not moving_piece.is_same_color(target)


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------

class KingMovement(MovementStrategy):

    def is_legal(self, moving_piece, start, end, board) -> bool:
        sr, sc = start
        er, ec = end
        return (
            max(abs(er - sr), abs(ec - sc)) == config.KING_MAX_DISTANCE
            and _destination_is_capturable(moving_piece, end, board)
        )


class RookMovement(MovementStrategy):

    def is_legal(self, moving_piece, start, end, board) -> bool:
        return (
            _is_straight(start, end)
            and _path_is_clear(start, end, board)
            and _destination_is_capturable(moving_piece, end, board)
        )


class BishopMovement(MovementStrategy):

    def is_legal(self, moving_piece, start, end, board) -> bool:
        return (
            _is_diagonal(start, end)
            and _path_is_clear(start, end, board)
            and _destination_is_capturable(moving_piece, end, board)
        )


class QueenMovement(MovementStrategy):

    def __init__(self):
        self._rook = RookMovement()
        self._bishop = BishopMovement()

    def is_legal(self, moving_piece, start, end, board) -> bool:
        return (
            self._rook.is_legal(moving_piece, start, end, board)
            or self._bishop.is_legal(moving_piece, start, end, board)
        )


class KnightMovement(MovementStrategy):

    OFFSETS = frozenset({(2, 1), (2, -1), (-2, 1), (-2, -1),
                         (1, 2), (1, -2), (-1, 2), (-1, -2)})

    def is_legal(self, moving_piece, start, end, board) -> bool:
        sr, sc = start
        er, ec = end
        return (
            (er - sr, ec - sc) in self.OFFSETS
            and _destination_is_capturable(moving_piece, end, board)
        )


class PawnMovement(MovementStrategy):


    def is_legal(self, moving_piece, start, end, board) -> bool:
        color = moving_piece.color
        forward = config.FORWARD_DIRECTION[color]
        sr, sc = start
        er, ec = end
        dr, dc = er - sr, ec - sc

        is_forward_step  = dr == forward and dc == 0
        is_two_step      = dr == 2 * forward and dc == 0
        is_diagonal_step = dr == forward and abs(dc) == 1

        if is_forward_step:
            return board.get_piece(*end) is Piece.EMPTY

        if is_two_step:
            start_row = self._start_row(color, board.rows)
            mid = (sr + forward, sc)
            return (
                sr == start_row
                and board.get_piece(*mid) is Piece.EMPTY
                and board.get_piece(*end) is Piece.EMPTY
            )

        if is_diagonal_step:
            target = board.get_piece(*end)
            return target is not Piece.EMPTY and not moving_piece.is_same_color(target)

        return False

    def on_arrival(self, piece, destination, board):
        promotion_row = board.rows - 1 if config.FORWARD_DIRECTION[piece.color] > 0 else 0
        if destination[0] == promotion_row:
            return Piece(piece.color, PieceType.QUEEN)
        return piece

    def _start_row(self, color: str, board_rows: int) -> int:
        return board_rows - 1 if config.FORWARD_DIRECTION[color] < 0 else 0


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

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
        if piece is None or piece.piece_type is None:
            return None
        strategy_cls = _STRATEGY_MAP.get(piece.piece_type)
        return strategy_cls() if strategy_cls else None
