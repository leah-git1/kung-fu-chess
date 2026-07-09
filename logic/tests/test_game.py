from board.board import Board
from game.game import Game
from moves.move_action import MoveAction
from moves.jump_action import JumpAction
from logic.board.piece import Piece
from logic.board.piece_type import PieceType
from board.board_parser import BoardParser
import config


PER_CELL = config.MOVE_DURATION_PER_CELL
JUMP = config.JUMP_DURATION


def P(token: str):
    """Helper: convert a token string like 'wK' into a Piece object."""
    if token == ".":
        return Piece.EMPTY
    return _parser._parse_cell(token)


_parser = BoardParser()


def G(rows):
    """Helper: build a Board from a 2D list of token strings."""
    return Board([[P(t) for t in row] for row in rows])


def cell(game, r, c):
    """Helper: get display string of a cell, or '.' for empty."""
    piece = game.board.get_piece(r, c)
    return repr(piece)


def create_game():
    return Game(G([["wK",".","."],[".",".","bK"],[".",".","."]]))


def _move_actions(game):
    return [a for a in game.action_manager.actions if isinstance(a, MoveAction)]


def _jump_actions(game):
    return [a for a in game.action_manager.actions if isinstance(a, JumpAction)]


# ---------------------------------------------------------------------------
# Selection and basic click
# ---------------------------------------------------------------------------

def test_click_select_piece():
    game = create_game()
    game.handle_click(0, 0)
    assert game.selected == (0, 0)


def test_click_empty_without_selection():
    game = create_game()
    game.handle_click(1, 1)
    assert game.selected is None


def test_move_created_after_second_click():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)  # wK (0,0) → (1,0): one step down, legal
    assert len(_move_actions(game)) == 1


# ---------------------------------------------------------------------------
# Timed movement
# ---------------------------------------------------------------------------

def test_wait_finishes_move():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL)
    assert cell(game, 1, 0) == "wK"
    assert cell(game, 0, 0) == "."


def test_piece_still_at_origin_before_arrival():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL - 1)
    assert cell(game, 0, 0) == "wK"
    assert cell(game, 1, 0) == "."


def test_piece_arrives_exactly_at_finish_time():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL)
    assert cell(game, 1, 0) == "wK"
    assert cell(game, 0, 0) == "."


def test_piece_not_at_origin_after_arrival():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL // 2)
    assert cell(game, 0, 0) == "wK"
    game.advance_time(PER_CELL // 2)
    assert cell(game, 0, 0) == "."


def test_piece_in_transit_after_half_duration():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL // 2)
    assert cell(game, 0, 0) == "wK"
    assert cell(game, 1, 0) == "."


def test_two_cell_move_takes_two_units():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(PER_CELL)
    assert cell(game, 0, 0) == "wR"
    game.advance_time(PER_CELL)
    assert cell(game, 0, 2) == "wR"


# ---------------------------------------------------------------------------
# Motion lock
# ---------------------------------------------------------------------------

def test_cannot_redirect_piece_in_motion():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL // 2)
    game.handle_click(0, 0)
    game.handle_click(0, 1)
    moves = _move_actions(game)
    assert len(moves) == 1
    assert moves[0].destination == (1, 0)


def test_second_color_blocked_while_first_in_motion():
    game = Game(G([["wR",".","."],[".",".","."],[".","bR","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.handle_click(2, 1)
    game.handle_click(2, 2)
    moves = _move_actions(game)
    assert len(moves) == 1
    assert moves[0].piece == P("wR")


def test_piece_can_move_again_after_arrival():
    game = create_game()
    game.handle_click(0, 0)
    game.handle_click(1, 0)
    game.advance_time(PER_CELL)
    game.handle_click(1, 0)
    game.handle_click(2, 0)
    game.advance_time(PER_CELL)
    assert cell(game, 2, 0) == "wK"
    assert cell(game, 1, 0) == "."


# ---------------------------------------------------------------------------
# Advanced real-time interaction cases
# ---------------------------------------------------------------------------

def test_enemy_at_destination_is_captured_on_arrival():
    game = Game(G([["wR",".","bP"],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    assert cell(game, 0, 2) == "wR"
    assert cell(game, 0, 0) == "."


def test_friendly_at_destination_cancels_move_on_arrival():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.board.set_piece(0, 2, P("wP"))
    game.advance_time(2 * PER_CELL)
    assert cell(game, 0, 2) == "wP"


def test_invalid_premove_shape_rejected_at_click_time():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(1, 1)
    assert len(_move_actions(game)) == 0


def test_move_to_empty_destination_applies_normally():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    assert cell(game, 0, 2) == "wR"
    assert cell(game, 0, 0) == "."


def test_origin_not_cleared_when_arrival_cancelled():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.board.set_piece(0, 2, P("wP"))
    game.advance_time(2 * PER_CELL)
    assert cell(game, 0, 0) == "wR"
    assert cell(game, 0, 2) == "wP"


# ---------------------------------------------------------------------------
# Game-over
# ---------------------------------------------------------------------------

def test_game_not_over_initially():
    assert not create_game().game_over


def test_capturing_enemy_king_ends_game():
    game = Game(G([["wR",".","bK"],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    assert game.game_over


def test_capturing_non_king_does_not_end_game():
    game = Game(G([["wR",".","bP"],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    assert not game.game_over


def test_moves_ignored_after_game_over():
    game = Game(G([["wR",".","bK"],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    assert game.game_over
    game.handle_click(0, 2)
    game.handle_click(0, 0)
    assert len(_move_actions(game)) == 0


def test_advance_time_ignored_after_game_over():
    game = Game(G([["wR",".","bK"],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.advance_time(2 * PER_CELL)
    t = game.current_time
    game.advance_time(PER_CELL)
    assert game.current_time == t


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

def test_white_pawn_promotes_on_reaching_row_0():
    game = Game(G([[".",".","."],[".","wP","."],[".",".","."]]))
    game.handle_click(1, 1)
    game.handle_click(0, 1)
    game.advance_time(PER_CELL)
    assert cell(game, 0, 1) == "wQ"


def test_black_pawn_promotes_on_reaching_last_row():
    game = Game(G([[".",".","."],[".","bP","."],[".",".","."]]))
    game.handle_click(1, 1)
    game.handle_click(2, 1)
    game.advance_time(PER_CELL)
    assert cell(game, 2, 1) == "bQ"


def test_pawn_does_not_promote_mid_board():
    game = Game(G([[".",".","."],[".",".","."],[".","wP","."],[".",".","."]]))
    game.handle_click(2, 1)
    game.handle_click(1, 1)
    game.advance_time(PER_CELL)
    assert cell(game, 1, 1) == "wP"


def test_white_pawn_two_step_from_start_row():
    grid = [["."] * 4 for _ in range(8)]
    grid[7][1] = "wP"
    game = Game(G(grid))
    game.handle_click(7, 1)
    game.handle_click(5, 1)
    game.advance_time(2 * PER_CELL)
    assert cell(game, 5, 1) == "wP"
    assert cell(game, 7, 1) == "."


# ---------------------------------------------------------------------------
# Jump
# ---------------------------------------------------------------------------

def test_jump_registers_airborne_state():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    assert game.action_manager.is_airborne((0, 0))


def test_piece_still_on_board_while_airborne():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    game.advance_time(JUMP // 2)
    assert cell(game, 0, 0) == "wR"


def test_jump_clears_after_land_time():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    game.advance_time(JUMP)
    assert not game.action_manager.is_airborne((0, 0))
    assert cell(game, 0, 0) == "wR"


def test_moving_piece_cannot_jump():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_click(0, 0)
    game.handle_click(0, 2)
    game.handle_jump(0, 0)
    assert not game.action_manager.is_airborne((0, 0))


def test_airborne_piece_cannot_jump_again():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    game.handle_jump(0, 0)
    assert len(_jump_actions(game)) == 1


def test_airborne_piece_captures_arriving_enemy():
    game = Game(G([["wR",".","bR"],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    game.action_manager.add(MoveAction(P("bR"), (0, 2), (0, 0), game.current_time + PER_CELL))
    game.advance_time(PER_CELL)
    assert cell(game, 0, 0) == "wR"
    assert cell(game, 0, 2) == "."


def test_no_enemy_arrives_piece_lands_normally():
    game = Game(G([["wR",".","."],[".",".","."],[".",".","."]]))
    game.handle_jump(0, 0)
    game.advance_time(JUMP)
    assert cell(game, 0, 0) == "wR"
    assert not game.action_manager.is_airborne((0, 0))
