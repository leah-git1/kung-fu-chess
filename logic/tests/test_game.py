from board.board import Board
from game.game import Game


PER_CELL = Game.MOVE_DURATION_PER_CELL


def create_game():

    board = Board(
        [
            ["wK",".","."],
            [".",".","bK"],
            [".",".","."]
        ]
    )

    return Game(board)



def test_click_select_piece():

    game=create_game()

    game.handle_click(0,0)

    assert game.selected==(0,0)



def test_click_empty_without_selection():

    game=create_game()

    game.handle_click(1,1)

    assert game.selected is None



def test_move_created_after_second_click():

    game=create_game()

    game.handle_click(0,0)

    # wK at (0,0) → (1,0): one step down, legal
    game.handle_click(1,0)

    assert len(game.move_manager.moves) == 1



def test_wait_finishes_move():
    # 1-cell move takes exactly PER_CELL ms
    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(1,0)=="wK"
    assert game.board.get_piece(0,0)=="."



def test_piece_still_at_origin_before_arrival():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL - 1)

    assert game.board.get_piece(0,0)=="wK"
    assert game.board.get_piece(1,0)=="."



def test_piece_arrives_exactly_at_finish_time():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(1,0)=="wK"
    assert game.board.get_piece(0,0)=="."



def test_piece_not_at_origin_after_arrival():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL // 2)
    assert game.board.get_piece(0,0)=="wK"

    game.advance_time(PER_CELL // 2)
    assert game.board.get_piece(0,0)=="."



def test_piece_in_transit_after_half_duration():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL // 2)

    assert game.board.get_piece(0,0)=="wK"
    assert game.board.get_piece(1,0)=="."



def test_two_cell_move_takes_two_units():
    # wR (0,0) → (0,2) is 2 cells; must still be in transit after PER_CELL
    board = Board([["wR",".","."],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)

    game.advance_time(PER_CELL)
    assert game.board.get_piece(0,0)=="wR"  # still in transit

    game.advance_time(PER_CELL)
    assert game.board.get_piece(0,2)=="wR"  # arrived



def test_cannot_redirect_piece_in_motion():
    # While any piece is in flight no new move may be issued
    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL // 2)  # still in transit

    game.handle_click(0,0)
    game.handle_click(0,1)  # attempt redirect — must be ignored

    assert len(game.move_manager.moves) == 1
    assert game.move_manager.moves[0].end == (1, 0)



def test_second_color_blocked_while_first_in_motion():
    # Global lock: black cannot move while white is in flight
    board = Board([["wR",".","."],[".",".","."],[".","bR","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)  # white rook starts moving

    game.handle_click(2,1)
    game.handle_click(2,2)  # black rook attempt — must be rejected

    assert len(game.move_manager.moves) == 1
    assert game.move_manager.moves[0].piece == "wR"



def test_piece_can_move_again_after_arrival():
    # No cooldown: immediately after arriving the piece may move again
    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(PER_CELL)  # piece arrives at (1,0)

    game.handle_click(1,0)
    game.handle_click(2,0)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(2,0)=="wK"
    assert game.board.get_piece(1,0)=="."



# ---------------------------------------------------------------------------
# Advanced real-time interaction cases
# ---------------------------------------------------------------------------

def test_enemy_at_destination_is_captured_on_arrival():
    # Enemy collision: arriving piece captures enemy occupying the destination
    board = Board([["wR",".","bP"],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)  # wR moves toward (0,2) where bP sits

    game.advance_time(2 * PER_CELL)

    assert game.board.get_piece(0,2)=="wR"
    assert game.board.get_piece(0,0)=="."



def test_friendly_at_destination_cancels_move_on_arrival():
    # Friendly-piece landing: if a friendly now occupies the destination,
    # the arriving piece must NOT overwrite it — move is cancelled.
    board = Board([["wR",".","."],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)  # wR queued to (0,2)

    # Simulate a friendly piece arriving at (0,2) before wR does
    game.board.grid[0][2] = "wP"

    game.advance_time(2 * PER_CELL)

    # wP must survive; wR must be lost (cancelled, not applied)
    assert game.board.get_piece(0,2)=="wP"



def test_invalid_premove_shape_rejected_at_click_time():
    # Invalid premove: a move whose shape is illegal is rejected immediately,
    # not queued and silently dropped later.
    board = Board([["wR",".","."],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(1,1)  # diagonal — illegal for rook

    assert len(game.move_manager.moves) == 0



def test_move_to_empty_destination_applies_normally():
    # Baseline: move to an empty square applies and clears origin
    board = Board([["wR",".","."],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)

    game.advance_time(2 * PER_CELL)

    assert game.board.get_piece(0,2)=="wR"
    assert game.board.get_piece(0,0)=="."



def test_origin_not_cleared_when_arrival_cancelled():
    # When a move is cancelled at arrival (friendly at destination),
    # the piece stays at its origin — the move simply did not happen.
    board = Board([["wR",".","."],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)

    game.board.grid[0][2] = "wP"  # friendly blocks destination

    game.advance_time(2 * PER_CELL)

    assert game.board.get_piece(0,0)=="wR"  # piece stays at origin
    assert game.board.get_piece(0,2)=="wP"  # friendly untouched



# ---------------------------------------------------------------------------
# Game-over
# ---------------------------------------------------------------------------

def test_game_not_over_initially():
    game = create_game()
    assert not game.game_over



def test_capturing_enemy_king_ends_game():
    # wR captures bK on arrival → game_over becomes True
    board = Board([["wR",".","bK"],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)

    game.advance_time(2 * PER_CELL)

    assert game.game_over



def test_capturing_non_king_does_not_end_game():
    board = Board([["wR",".","bP"],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)

    game.advance_time(2 * PER_CELL)

    assert not game.game_over



def test_moves_ignored_after_game_over():
    # After game_over, handle_click must be a no-op
    board = Board([["wR",".","bK"],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)
    game.advance_time(2 * PER_CELL)  # bK captured, game over

    assert game.game_over

    game.handle_click(0,2)
    game.handle_click(0,0)  # attempt to move wR back

    assert len(game.move_manager.moves) == 0



def test_advance_time_ignored_after_game_over():
    # After game_over, advance_time must not change current_time
    board = Board([["wR",".","bK"],[".",".","."],[".",".","."]])
    game = Game(board)

    game.handle_click(0,0)
    game.handle_click(0,2)
    game.advance_time(2 * PER_CELL)  # game over

    time_at_game_over = game.current_time

    game.advance_time(PER_CELL)

    assert game.current_time == time_at_game_over



# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

def test_white_pawn_promotes_on_reaching_row_0():
    # wP at row 1 moves one step to row 0 and becomes wQ
    board = Board([[".",".","."],[".","wP","."],[".",".","."]])
    game = Game(board)

    game.handle_click(1,1)
    game.handle_click(0,1)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(0,1) == "wQ"



def test_black_pawn_promotes_on_reaching_last_row():
    # bP at second-to-last row moves one step to last row and becomes bQ
    board = Board([[".",".","."],[".","bP","."],[".",".","."]])
    game = Game(board)

    game.handle_click(1,1)
    game.handle_click(2,1)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(2,1) == "bQ"



def test_pawn_does_not_promote_mid_board():
    # wP moves one step but does not reach row 0 — stays a pawn
    board = Board([[".",".","."],[".",".","."],[".","wP","."],[".",".","."]])
    game = Game(board)

    game.handle_click(2,1)
    game.handle_click(1,1)

    game.advance_time(PER_CELL)

    assert game.board.get_piece(1,1) == "wP"



def test_white_pawn_two_step_from_start_row():
    # On an 8-row board white start row is 7; two-step advance must be accepted
    grid = [["."]*4 for _ in range(8)]
    grid[7][1] = "wP"
    board = Board(grid)
    game = Game(board)

    game.handle_click(7,1)
    game.handle_click(5,1)

    game.advance_time(2 * PER_CELL)

    assert game.board.get_piece(5,1) == "wP"
    assert game.board.get_piece(7,1) == "."
