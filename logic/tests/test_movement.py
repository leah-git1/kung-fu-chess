"""
Tests for Phase 1, Steps 2 & 3 — movement shape, blockers, and capture rules.

Scope:
- Shape legality (step 2)
- Sliding pieces blocked by intermediate pieces (step 3)
- Knight jumps over blockers (step 3)
- Friendly-piece capture rejected at destination (step 3)
- Enemy-piece capture accepted at destination (step 3)

Not in scope: check/checkmate, turn order, Kung-Fu timing.
"""

from board.board import Board
from board.board_parser import BoardParser
from logic.board.piece import Piece
from logic.board.movement_strategy import (
    KingMovement,
    RookMovement,
    BishopMovement,
    QueenMovement,
    KnightMovement,
    PawnMovement,
    MovementStrategyFactory,
)


_parser = BoardParser()


def _P(token):
    return _parser._parse_cell(token)


def empty_board(rows=8, cols=8):
    return Board([[Piece.EMPTY for _ in range(cols)] for _ in range(rows)])


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY for _ in range(cols)] for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _P(token)
    return Board(grid)


# ---------------------------------------------------------------------------
# King
# ---------------------------------------------------------------------------

class TestKingMovement:

    def setup_method(self):
        self.strategy = KingMovement()
        self.board = empty_board()

    def test_legal_one_step_horizontal(self):
        assert self.strategy.is_legal(_P("wK"), (4, 4), (4, 5), self.board)

    def test_legal_one_step_vertical(self):
        assert self.strategy.is_legal(_P("wK"), (4, 4), (5, 4), self.board)

    def test_legal_one_step_diagonal(self):
        assert self.strategy.is_legal(_P("wK"), (4, 4), (5, 5), self.board)

    def test_illegal_two_steps(self):
        assert not self.strategy.is_legal(_P("wK"), (4, 4), (4, 6), self.board)

    def test_illegal_knight_like_jump(self):
        assert not self.strategy.is_legal(_P("wK"), (4, 4), (6, 5), self.board)

    def test_illegal_no_movement(self):
        assert not self.strategy.is_legal(_P("wK"), (4, 4), (4, 4), self.board)

    def test_illegal_capture_friendly(self):
        board = board_with({(4, 4): "wK", (4, 5): "wR"})
        assert not self.strategy.is_legal(_P("wK"), (4, 4), (4, 5), board)

    def test_legal_capture_enemy(self):
        board = board_with({(4, 4): "wK", (4, 5): "bR"})
        assert self.strategy.is_legal(_P("wK"), (4, 4), (4, 5), board)


# ---------------------------------------------------------------------------
# Rook
# ---------------------------------------------------------------------------

class TestRookMovement:

    def setup_method(self):
        self.strategy = RookMovement()

    def test_legal_horizontal(self):
        assert self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), empty_board())

    def test_legal_vertical(self):
        assert self.strategy.is_legal(_P("wR"), (0, 3), (7, 3), empty_board())

    def test_illegal_diagonal(self):
        assert not self.strategy.is_legal(_P("wR"), (0, 0), (3, 3), empty_board())

    def test_illegal_l_shape(self):
        assert not self.strategy.is_legal(_P("wR"), (0, 0), (2, 1), empty_board())

    def test_illegal_blocked_by_friendly(self):
        board = board_with({(4, 0): "wR", (4, 3): "wP"})
        assert not self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), board)

    def test_illegal_blocked_by_enemy(self):
        board = board_with({(4, 0): "wR", (4, 3): "bP"})
        assert not self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), board)

    def test_legal_unblocked_path(self):
        board = board_with({(4, 0): "wR"})
        assert self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), board)

    def test_illegal_capture_friendly_at_destination(self):
        board = board_with({(4, 0): "wR", (4, 7): "wP"})
        assert not self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), board)

    def test_legal_capture_enemy_at_destination(self):
        board = board_with({(4, 0): "wR", (4, 7): "bP"})
        assert self.strategy.is_legal(_P("wR"), (4, 0), (4, 7), board)


# ---------------------------------------------------------------------------
# Bishop
# ---------------------------------------------------------------------------

class TestBishopMovement:

    def setup_method(self):
        self.strategy = BishopMovement()

    def test_legal_diagonal_down_right(self):
        assert self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), empty_board())

    def test_legal_diagonal_up_left(self):
        assert self.strategy.is_legal(_P("wB"), (4, 4), (1, 1), empty_board())

    def test_illegal_straight_horizontal(self):
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (0, 4), empty_board())

    def test_illegal_straight_vertical(self):
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (4, 0), empty_board())

    def test_illegal_off_diagonal(self):
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (3, 4), empty_board())

    def test_illegal_blocked_by_friendly(self):
        board = board_with({(0, 0): "wB", (2, 2): "wP"})
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), board)

    def test_illegal_blocked_by_enemy(self):
        board = board_with({(0, 0): "wB", (2, 2): "bP"})
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), board)

    def test_legal_unblocked_diagonal(self):
        board = board_with({(0, 0): "wB"})
        assert self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), board)

    def test_illegal_capture_friendly_at_destination(self):
        board = board_with({(0, 0): "wB", (4, 4): "wP"})
        assert not self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), board)

    def test_legal_capture_enemy_at_destination(self):
        board = board_with({(0, 0): "wB", (4, 4): "bP"})
        assert self.strategy.is_legal(_P("wB"), (0, 0), (4, 4), board)


# ---------------------------------------------------------------------------
# Queen
# ---------------------------------------------------------------------------

class TestQueenMovement:

    def setup_method(self):
        self.strategy = QueenMovement()

    def test_legal_horizontal(self):
        assert self.strategy.is_legal(_P("wQ"), (3, 0), (3, 7), empty_board())

    def test_legal_vertical(self):
        assert self.strategy.is_legal(_P("wQ"), (0, 3), (7, 3), empty_board())

    def test_legal_diagonal(self):
        assert self.strategy.is_legal(_P("wQ"), (0, 0), (5, 5), empty_board())

    def test_illegal_l_shape(self):
        assert not self.strategy.is_legal(_P("wQ"), (0, 0), (2, 1), empty_board())

    def test_illegal_off_axis(self):
        assert not self.strategy.is_legal(_P("wQ"), (0, 0), (3, 5), empty_board())

    def test_illegal_blocked_straight(self):
        board = board_with({(3, 0): "wQ", (3, 4): "wP"})
        assert not self.strategy.is_legal(_P("wQ"), (3, 0), (3, 7), board)

    def test_illegal_blocked_diagonal(self):
        board = board_with({(0, 0): "wQ", (2, 2): "wP"})
        assert not self.strategy.is_legal(_P("wQ"), (0, 0), (4, 4), board)

    def test_illegal_capture_friendly_at_destination(self):
        board = board_with({(3, 0): "wQ", (3, 7): "wR"})
        assert not self.strategy.is_legal(_P("wQ"), (3, 0), (3, 7), board)

    def test_legal_capture_enemy_at_destination(self):
        board = board_with({(3, 0): "wQ", (3, 7): "bR"})
        assert self.strategy.is_legal(_P("wQ"), (3, 0), (3, 7), board)


# ---------------------------------------------------------------------------
# Knight
# ---------------------------------------------------------------------------

class TestKnightMovement:

    def setup_method(self):
        self.strategy = KnightMovement()
        self.board = empty_board()

    def test_legal_2_1(self):
        assert self.strategy.is_legal(_P("wN"), (4, 4), (6, 5), self.board)

    def test_legal_1_2(self):
        assert self.strategy.is_legal(_P("wN"), (4, 4), (5, 6), self.board)

    def test_legal_all_eight_offsets(self):
        offsets = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr, dc in offsets:
            assert self.strategy.is_legal(_P("wN"), (4, 4), (4+dr, 4+dc), self.board), \
                f"Expected legal for offset ({dr},{dc})"

    def test_illegal_straight(self):
        assert not self.strategy.is_legal(_P("wN"), (4, 4), (4, 6), self.board)

    def test_illegal_diagonal(self):
        assert not self.strategy.is_legal(_P("wN"), (4, 4), (6, 6), self.board)

    def test_illegal_close_but_not_l_shape(self):
        assert not self.strategy.is_legal(_P("wN"), (4, 4), (5, 5), self.board)

    def test_illegal_2_2_not_l_shape(self):
        assert not self.strategy.is_legal(_P("wN"), (4, 4), (6, 6), self.board)

    def test_knight_jumps_over_blocking_pieces(self):
        # Knight is not impeded by pieces on intermediate squares
        board = board_with({(4, 4): "wN", (4, 5): "wP", (5, 4): "wP"})
        assert self.strategy.is_legal(_P("wN"), (4, 4), (6, 5), board)

    def test_illegal_capture_friendly_at_destination(self):
        board = board_with({(4, 4): "wN", (6, 5): "wP"})
        assert not self.strategy.is_legal(_P("wN"), (4, 4), (6, 5), board)

    def test_legal_capture_enemy_at_destination(self):
        board = board_with({(4, 4): "wN", (6, 5): "bP"})
        assert self.strategy.is_legal(_P("wN"), (4, 4), (6, 5), board)


# ---------------------------------------------------------------------------
# Pawn
# ---------------------------------------------------------------------------

class TestPawnMovement:

    def setup_method(self):
        self.strategy = PawnMovement()

    # --- White pawn (moves up = decreasing row) ---

    def test_white_legal_forward_one(self):
        board = board_with({(4, 3): "wP"})
        assert self.strategy.is_legal(_P("wP"), (4, 3), (3, 3), board)

    def test_white_illegal_forward_two_not_from_start(self):
        # Row 4 is not the start row on an 8-row board (start = row 7)
        board = board_with({(4, 3): "wP"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (2, 3), board)

    def test_white_legal_two_step_from_start_row(self):
        board = board_with({(7, 3): "wP"}, rows=8)
        assert self.strategy.is_legal(_P("wP"), (7, 3), (5, 3), board)

    def test_white_illegal_two_step_blocked_at_intermediate(self):
        board = board_with({(7, 3): "wP", (6, 3): "bP"}, rows=8)
        assert not self.strategy.is_legal(_P("wP"), (7, 3), (5, 3), board)

    def test_white_illegal_two_step_blocked_at_destination(self):
        board = board_with({(7, 3): "wP", (5, 3): "bP"}, rows=8)
        assert not self.strategy.is_legal(_P("wP"), (7, 3), (5, 3), board)

    def test_white_illegal_move_backward(self):
        board = board_with({(4, 3): "wP"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (5, 3), board)

    def test_white_illegal_forward_blocked(self):
        board = board_with({(4, 3): "wP", (3, 3): "bP"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (3, 3), board)

    def test_white_illegal_capture_forward(self):
        # Enemy directly ahead — still illegal, pawns don't capture forward
        board = board_with({(4, 3): "wP", (3, 3): "bR"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (3, 3), board)

    def test_white_legal_diagonal_capture(self):
        board = board_with({(4, 3): "wP", (3, 4): "bR"})
        assert self.strategy.is_legal(_P("wP"), (4, 3), (3, 4), board)

    def test_white_illegal_diagonal_empty(self):
        # Diagonal move only legal when capturing — empty square is illegal
        board = board_with({(4, 3): "wP"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (3, 4), board)

    def test_white_illegal_diagonal_capture_friendly(self):
        board = board_with({(4, 3): "wP", (3, 4): "wR"})
        assert not self.strategy.is_legal(_P("wP"), (4, 3), (3, 4), board)

    # --- Black pawn (moves down = increasing row) ---

    def test_black_legal_forward_one(self):
        board = board_with({(3, 3): "bP"})
        assert self.strategy.is_legal(_P("bP"), (3, 3), (4, 3), board)

    def test_black_illegal_forward_two_not_from_start(self):
        # Row 3 is not the start row on an 8-row board (start = row 0)
        board = board_with({(3, 3): "bP"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (5, 3), board)

    def test_black_legal_two_step_from_start_row(self):
        board = board_with({(0, 3): "bP"}, rows=8)
        assert self.strategy.is_legal(_P("bP"), (0, 3), (2, 3), board)

    def test_black_illegal_two_step_blocked_at_intermediate(self):
        board = board_with({(0, 3): "bP", (1, 3): "wP"}, rows=8)
        assert not self.strategy.is_legal(_P("bP"), (0, 3), (2, 3), board)

    def test_black_illegal_two_step_blocked_at_destination(self):
        board = board_with({(0, 3): "bP", (2, 3): "wP"}, rows=8)
        assert not self.strategy.is_legal(_P("bP"), (0, 3), (2, 3), board)

    def test_black_illegal_move_backward(self):
        board = board_with({(3, 3): "bP"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (2, 3), board)

    def test_black_illegal_forward_blocked(self):
        board = board_with({(3, 3): "bP", (4, 3): "wP"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (4, 3), board)

    def test_black_illegal_capture_forward(self):
        board = board_with({(3, 3): "bP", (4, 3): "wR"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (4, 3), board)

    def test_black_legal_diagonal_capture(self):
        board = board_with({(3, 3): "bP", (4, 4): "wR"})
        assert self.strategy.is_legal(_P("bP"), (3, 3), (4, 4), board)

    def test_black_illegal_diagonal_empty(self):
        board = board_with({(3, 3): "bP"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (4, 4), board)

    def test_black_illegal_diagonal_capture_friendly(self):
        board = board_with({(3, 3): "bP", (4, 4): "bR"})
        assert not self.strategy.is_legal(_P("bP"), (3, 3), (4, 4), board)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestMovementStrategyFactory:

    def test_king_token(self):
        assert isinstance(MovementStrategyFactory.for_token("wK"), KingMovement)

    def test_black_rook_token(self):
        assert isinstance(MovementStrategyFactory.for_token("bR"), RookMovement)

    def test_bishop_token(self):
        assert isinstance(MovementStrategyFactory.for_token("wB"), BishopMovement)

    def test_queen_token(self):
        assert isinstance(MovementStrategyFactory.for_token("wQ"), QueenMovement)

    def test_knight_token(self):
        assert isinstance(MovementStrategyFactory.for_token("bN"), KnightMovement)

    def test_empty_square_returns_none(self):
        assert MovementStrategyFactory.for_token(".") is None

    def test_pawn_token(self):
        assert isinstance(MovementStrategyFactory.for_token("wP"), PawnMovement)

    def test_black_pawn_token(self):
        assert isinstance(MovementStrategyFactory.for_token("bP"), PawnMovement)
