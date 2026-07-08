from board.board import Board
from game.game import Game


DURATION = Game.MOVE_DURATION


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

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(DURATION)

    assert game.board.get_piece(1,0)=="wK"
    assert game.board.get_piece(0,0)=="."



def test_piece_still_at_origin_before_arrival():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(DURATION - 1)

    assert game.board.get_piece(0,0)=="wK"
    assert game.board.get_piece(1,0)=="."



def test_piece_arrives_exactly_at_finish_time():

    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(DURATION)

    assert game.board.get_piece(1,0)=="wK"
    assert game.board.get_piece(0,0)=="."



def test_piece_not_at_origin_after_arrival():
    # Confirms the origin is cleared once the move completes
    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(DURATION // 2)
    assert game.board.get_piece(0,0)=="wK"

    game.advance_time(DURATION // 2)
    assert game.board.get_piece(0,0)=="."



def test_piece_in_transit_after_half_duration():
    # Explicit mid-flight check: board unchanged at the halfway point
    game=create_game()

    game.handle_click(0,0)
    game.handle_click(1,0)

    game.advance_time(DURATION // 2)

    assert game.board.get_piece(0,0)=="wK"
    assert game.board.get_piece(1,0)=="."
