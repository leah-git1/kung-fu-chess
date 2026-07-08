from abc import ABC, abstractmethod


class MovementStrategy(ABC):

    @abstractmethod
    def is_legal(self, moving_piece, start, end, board) -> bool:
        pass


# ---------------------------------------------------------------------------
# Shared helpers (DRY: used by all strategies)
# ---------------------------------------------------------------------------

def _color(piece: str) -> str:
    return piece[0]


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
        if board.get_piece(r, c) != ".":
            return False
        r += dr
        c += dc
    return True


def _destination_is_capturable(moving_piece: str, end, board) -> bool:
    """Returns True if the destination is empty or occupied by an enemy."""
    target = board.get_piece(*end)
    return target == "." or _color(target) != _color(moving_piece)


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------

class KingMovement(MovementStrategy):

    MAX_DISTANCE = 1

    def is_legal(self, moving_piece, start, end, board) -> bool:
        sr, sc = start
        er, ec = end
        return (
            max(abs(er - sr), abs(ec - sc)) == self.MAX_DISTANCE
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
