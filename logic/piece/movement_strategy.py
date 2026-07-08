from abc import ABC, abstractmethod
import config
from piece.piece import Piece


class MovementStrategy(ABC):

    @abstractmethod
    def is_legal(self, moving_piece, start, end, board) -> bool:
        pass


# ---------------------------------------------------------------------------
# Shared helpers (DRY: used by all strategies)
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
    """Returns True if every square strictly between start and end is empty."""
    sr, sc = start
    er, ec = end
    dr = 0 if er == sr else (1 if er > sr else -1)
    dc = 0 if ec == sc else (1 if ec > sc else -1)
    r, c = sr + dr, sc + dc
    while (r, c) != (er, ec):
        if board.get_piece(r, c) != Piece.EMPTY:
            return False
        r += dr
        c += dc
    return True


def _destination_is_capturable(moving_piece, end, board) -> bool:
    """Returns True if the destination is empty or occupied by an enemy."""
    target = board.get_piece(*end)
    return target == Piece.EMPTY or not moving_piece.is_same_color(target)


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
    """Queen = Rook logic OR Bishop logic (composition, not duplication)."""

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
    """Single class for both colors — direction is derived from the piece's color."""

    FORWARD_BY_COLOR = {"w": -1, "b": 1}

    def is_legal(self, moving_piece, start, end, board) -> bool:
        color = moving_piece.color
        forward = self.FORWARD_BY_COLOR[color]
        sr, sc = start
        er, ec = end
        dr, dc = er - sr, ec - sc

        is_forward_step  = dr == forward and dc == 0
        is_two_step      = dr == 2 * forward and dc == 0
        is_diagonal_step = dr == forward and abs(dc) == 1

        if is_forward_step:
            return board.get_piece(*end) == "."

        if is_two_step:
            start_row = self._start_row(color, board.rows)
            mid = (sr + forward, sc)
            return (
                sr == start_row
                and board.get_piece(*mid) == "."
                and board.get_piece(*end) == "."
            )

        if is_diagonal_step:
            target = board.get_piece(*end)
            return target != "." and not moving_piece.is_same_color(target)

        return False

    def _start_row(self, color: str, board_rows: int) -> int:
        return board_rows - 1 if color == "w" else 0
