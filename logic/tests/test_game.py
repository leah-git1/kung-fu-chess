from board.board import Board
from game.game import Game



def create_game():

    board = Board(
        [
            ["wK",".","bK"],
            [".",".","."],
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

    game.handle_click(1,1)


    assert len(
        game.move_manager.moves
    ) == 1



def test_wait_finishes_move():

    game=create_game()


    game.handle_click(0,0)

    game.handle_click(1,1)


    game.advance_time(1000)


    assert game.board.get_piece(1,1)=="wK"

    assert game.board.get_piece(0,0)=="."