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
