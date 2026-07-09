from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType
from rules.movement_strategy import (
    KingMovement, RookMovement, BishopMovement,
    QueenMovement, KnightMovement, PawnMovement,
    MovementStrategyFactory,
)


def _p(token):
    color, pt_char = token[0], token[1]
    return Piece(color, PieceType(pt_char))


def empty_board(rows=8, cols=8):
    return Board([[Piece.EMPTY] * cols for _ in range(rows)])


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Board(grid)


# ---------------------------------------------------------------------------
# King
# ---------------------------------------------------------------------------

class TestKingMovement:

    def setup_method(self):
        self.s = KingMovement()
        self.b = empty_board()

    def test_one_step_horizontal(self):
        assert self.s.is_legal(_p("wK"), (4, 4), (4, 5), self.b)

    def test_one_step_vertical(self):
        assert self.s.is_legal(_p("wK"), (4, 4), (5, 4), self.b)

    def test_one_step_diagonal(self):
        assert self.s.is_legal(_p("wK"), (4, 4), (5, 5), self.b)

    def test_two_steps_illegal(self):
        assert not self.s.is_legal(_p("wK"), (4, 4), (4, 6), self.b)

    def test_no_movement_illegal(self):
        assert not self.s.is_legal(_p("wK"), (4, 4), (4, 4), self.b)

    def test_capture_friendly_illegal(self):
        b = board_with({(4, 4): "wK", (4, 5): "wR"})
        assert not self.s.is_legal(_p("wK"), (4, 4), (4, 5), b)

    def test_capture_enemy_legal(self):
        b = board_with({(4, 4): "wK", (4, 5): "bR"})
        assert self.s.is_legal(_p("wK"), (4, 4), (4, 5), b)


# ---------------------------------------------------------------------------
# Rook
# ---------------------------------------------------------------------------

class TestRookMovement:

    def setup_method(self):
        self.s = RookMovement()

    def test_horizontal(self):
        assert self.s.is_legal(_p("wR"), (4, 0), (4, 7), empty_board())

    def test_vertical(self):
        assert self.s.is_legal(_p("wR"), (0, 3), (7, 3), empty_board())

    def test_diagonal_illegal(self):
        assert not self.s.is_legal(_p("wR"), (0, 0), (3, 3), empty_board())

    def test_blocked_by_friendly(self):
        b = board_with({(4, 0): "wR", (4, 3): "wP"})
        assert not self.s.is_legal(_p("wR"), (4, 0), (4, 7), b)

    def test_blocked_by_enemy(self):
        b = board_with({(4, 0): "wR", (4, 3): "bP"})
        assert not self.s.is_legal(_p("wR"), (4, 0), (4, 7), b)

    def test_capture_enemy_at_destination(self):
        b = board_with({(4, 0): "wR", (4, 7): "bP"})
        assert self.s.is_legal(_p("wR"), (4, 0), (4, 7), b)

    def test_capture_friendly_at_destination_illegal(self):
        b = board_with({(4, 0): "wR", (4, 7): "wP"})
        assert not self.s.is_legal(_p("wR"), (4, 0), (4, 7), b)


# ---------------------------------------------------------------------------
# Bishop
# ---------------------------------------------------------------------------

class TestBishopMovement:

    def setup_method(self):
        self.s = BishopMovement()

    def test_diagonal_down_right(self):
        assert self.s.is_legal(_p("wB"), (0, 0), (4, 4), empty_board())

    def test_diagonal_up_left(self):
        assert self.s.is_legal(_p("wB"), (4, 4), (1, 1), empty_board())

    def test_straight_illegal(self):
        assert not self.s.is_legal(_p("wB"), (0, 0), (0, 4), empty_board())

    def test_blocked_by_friendly(self):
        b = board_with({(0, 0): "wB", (2, 2): "wP"})
        assert not self.s.is_legal(_p("wB"), (0, 0), (4, 4), b)

    def test_capture_enemy_at_destination(self):
        b = board_with({(0, 0): "wB", (4, 4): "bP"})
        assert self.s.is_legal(_p("wB"), (0, 0), (4, 4), b)

    def test_capture_friendly_at_destination_illegal(self):
        b = board_with({(0, 0): "wB", (4, 4): "wP"})
        assert not self.s.is_legal(_p("wB"), (0, 0), (4, 4), b)


# ---------------------------------------------------------------------------
# Queen
# ---------------------------------------------------------------------------

class TestQueenMovement:

    def setup_method(self):
        self.s = QueenMovement()

    def test_horizontal(self):
        assert self.s.is_legal(_p("wQ"), (3, 0), (3, 7), empty_board())

    def test_vertical(self):
        assert self.s.is_legal(_p("wQ"), (0, 3), (7, 3), empty_board())

    def test_diagonal(self):
        assert self.s.is_legal(_p("wQ"), (0, 0), (5, 5), empty_board())

    def test_l_shape_illegal(self):
        assert not self.s.is_legal(_p("wQ"), (0, 0), (2, 1), empty_board())

    def test_blocked_straight(self):
        b = board_with({(3, 0): "wQ", (3, 4): "wP"})
        assert not self.s.is_legal(_p("wQ"), (3, 0), (3, 7), b)

    def test_capture_enemy_at_destination(self):
        b = board_with({(3, 0): "wQ", (3, 7): "bR"})
        assert self.s.is_legal(_p("wQ"), (3, 0), (3, 7), b)


# ---------------------------------------------------------------------------
# Knight
# ---------------------------------------------------------------------------

class TestKnightMovement:

    def setup_method(self):
        self.s = KnightMovement()
        self.b = empty_board()

    def test_all_eight_offsets(self):
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            assert self.s.is_legal(_p("wN"), (4, 4), (4+dr, 4+dc), self.b)

    def test_straight_illegal(self):
        assert not self.s.is_legal(_p("wN"), (4, 4), (4, 6), self.b)

    def test_jumps_over_blockers(self):
        b = board_with({(4, 4): "wN", (4, 5): "wP", (5, 4): "wP"})
        assert self.s.is_legal(_p("wN"), (4, 4), (6, 5), b)

    def test_capture_friendly_illegal(self):
        b = board_with({(4, 4): "wN", (6, 5): "wP"})
        assert not self.s.is_legal(_p("wN"), (4, 4), (6, 5), b)

    def test_capture_enemy_legal(self):
        b = board_with({(4, 4): "wN", (6, 5): "bP"})
        assert self.s.is_legal(_p("wN"), (4, 4), (6, 5), b)


# ---------------------------------------------------------------------------
# Pawn
# ---------------------------------------------------------------------------

class TestPawnMovement:

    def setup_method(self):
        self.s = PawnMovement()

    def test_white_forward_one(self):
        b = board_with({(4, 3): "wP"})
        assert self.s.is_legal(_p("wP"), (4, 3), (3, 3), b)

    def test_white_forward_one_blocked(self):
        b = board_with({(4, 3): "wP", (3, 3): "bP"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (3, 3), b)

    def test_white_two_step_from_start(self):
        b = board_with({(7, 3): "wP"}, rows=8)
        assert self.s.is_legal(_p("wP"), (7, 3), (5, 3), b)

    def test_white_two_step_not_from_start_illegal(self):
        b = board_with({(4, 3): "wP"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (2, 3), b)

    def test_white_two_step_blocked_at_intermediate(self):
        b = board_with({(7, 3): "wP", (6, 3): "bP"}, rows=8)
        assert not self.s.is_legal(_p("wP"), (7, 3), (5, 3), b)

    def test_white_diagonal_capture(self):
        b = board_with({(4, 3): "wP", (3, 4): "bR"})
        assert self.s.is_legal(_p("wP"), (4, 3), (3, 4), b)

    def test_white_diagonal_empty_illegal(self):
        b = board_with({(4, 3): "wP"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (3, 4), b)

    def test_white_diagonal_friendly_illegal(self):
        b = board_with({(4, 3): "wP", (3, 4): "wR"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (3, 4), b)

    def test_white_backward_illegal(self):
        b = board_with({(4, 3): "wP"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (5, 3), b)

    def test_black_forward_one(self):
        b = board_with({(3, 3): "bP"})
        assert self.s.is_legal(_p("bP"), (3, 3), (4, 3), b)

    def test_black_two_step_from_start(self):
        b = board_with({(0, 3): "bP"}, rows=8)
        assert self.s.is_legal(_p("bP"), (0, 3), (2, 3), b)

    def test_black_two_step_blocked_at_intermediate(self):
        b = board_with({(0, 3): "bP", (1, 3): "wP"}, rows=8)
        assert not self.s.is_legal(_p("bP"), (0, 3), (2, 3), b)

    def test_black_diagonal_capture(self):
        b = board_with({(3, 3): "bP", (4, 4): "wR"})
        assert self.s.is_legal(_p("bP"), (3, 3), (4, 4), b)

    def test_black_diagonal_empty_illegal(self):
        b = board_with({(3, 3): "bP"})
        assert not self.s.is_legal(_p("bP"), (3, 3), (4, 4), b)

    def test_white_forward_capture_illegal(self):
        b = board_with({(4, 3): "wP", (3, 3): "bP"})
        assert not self.s.is_legal(_p("wP"), (4, 3), (3, 3), b)

    def test_black_forward_one_blocked(self):
        b = board_with({(3, 3): "bP", (4, 3): "wP"})
        assert not self.s.is_legal(_p("bP"), (3, 3), (4, 3), b)

    def test_black_forward_capture_illegal(self):
        b = board_with({(3, 3): "bP", (4, 3): "wP"})
        assert not self.s.is_legal(_p("bP"), (3, 3), (4, 3), b)

    def test_black_two_step_not_from_start_illegal(self):
        b = board_with({(3, 3): "bP"})
        assert not self.s.is_legal(_p("bP"), (3, 3), (5, 3), b)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestMovementStrategyFactory:

    def test_king(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("wK")), KingMovement)

    def test_rook(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("bR")), RookMovement)

    def test_bishop(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("wB")), BishopMovement)

    def test_queen(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("wQ")), QueenMovement)

    def test_knight(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("bN")), KnightMovement)

    def test_pawn(self):
        assert isinstance(MovementStrategyFactory.for_piece(_p("wP")), PawnMovement)

    def test_empty_returns_none(self):
        assert MovementStrategyFactory.for_piece(Piece.EMPTY) is None
