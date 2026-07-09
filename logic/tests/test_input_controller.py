from unittest.mock import MagicMock, call
from board.piece import Piece
from board.piece_type import PieceType
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController


CELL = 100


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def _make_controller():
    return InputController(BoardMapper(CELL))


def _make_game(grid: dict, rows=8, cols=8):
    """Build a mock game with a simple piece layout."""
    game = MagicMock()
    game.is_inside.side_effect = lambda cell: (
        0 <= cell[0] < rows and 0 <= cell[1] < cols
    )
    game.get_piece_at.side_effect = lambda cell: grid.get(cell, Piece.EMPTY)
    return game


def _px(row, col):
    return col * CELL, row * CELL


# ------------------------------------------------------------------
# First click — selection
# ------------------------------------------------------------------

def test_first_click_on_piece_selects_it():
    ctrl = _make_controller()
    game = _make_game({(0, 0): _p("wK")})
    ctrl.on_click(*_px(0, 0), game)
    assert ctrl.selected == (0, 0)


def test_first_click_on_empty_cell_ignored():
    ctrl = _make_controller()
    game = _make_game({})
    ctrl.on_click(*_px(0, 0), game)
    assert ctrl.selected is None


def test_first_click_outside_board_ignored():
    ctrl = _make_controller()
    game = _make_game({})
    ctrl.on_click(9999, 9999, game)
    assert ctrl.selected is None


# ------------------------------------------------------------------
# Second click — move request
# ------------------------------------------------------------------

def test_second_click_calls_request_move():
    ctrl = _make_controller()
    wk = _p("wK")
    game = _make_game({(0, 0): wk})
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(*_px(1, 0), game)
    game.request_move.assert_called_once_with(wk, (0, 0), (1, 0))


def test_selection_cleared_after_second_click():
    ctrl = _make_controller()
    wk = _p("wK")
    game = _make_game({(0, 0): wk})
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(*_px(1, 0), game)
    assert ctrl.selected is None


def test_selection_cleared_even_if_move_illegal():
    ctrl = _make_controller()
    wk = _p("wK")
    game = _make_game({(0, 0): wk})
    game.request_move.return_value = False
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(*_px(5, 5), game)
    assert ctrl.selected is None


# ------------------------------------------------------------------
# Same cell — deselect
# ------------------------------------------------------------------

def test_click_same_cell_deselects():
    ctrl = _make_controller()
    game = _make_game({(0, 0): _p("wK")})
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(*_px(0, 0), game)
    assert ctrl.selected is None


# ------------------------------------------------------------------
# Friendly piece — redirect selection
# ------------------------------------------------------------------

def test_second_click_on_friendly_redirects_selection():
    ctrl = _make_controller()
    wk = _p("wK")
    wr = _p("wR")
    game = _make_game({(0, 0): wk, (0, 1): wr})
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(*_px(0, 1), game)
    assert ctrl.selected == (0, 1)
    game.request_move.assert_not_called()


# ------------------------------------------------------------------
# Outside board with selection — cancel
# ------------------------------------------------------------------

def test_click_outside_board_with_selection_cancels():
    ctrl = _make_controller()
    game = _make_game({(0, 0): _p("wK")})
    ctrl.on_click(*_px(0, 0), game)
    ctrl.on_click(9999, 9999, game)
    assert ctrl.selected is None
    game.request_move.assert_not_called()


# ------------------------------------------------------------------
# on_jump
# ------------------------------------------------------------------

def test_jump_calls_request_jump():
    ctrl = _make_controller()
    wr = _p("wR")
    game = _make_game({(0, 0): wr})
    ctrl.on_jump(*_px(0, 0), game)
    game.request_jump.assert_called_once_with(wr, (0, 0))


def test_jump_on_empty_cell_ignored():
    ctrl = _make_controller()
    game = _make_game({})
    ctrl.on_jump(*_px(0, 0), game)
    game.request_jump.assert_not_called()


def test_jump_outside_board_ignored():
    ctrl = _make_controller()
    game = _make_game({})
    ctrl.on_jump(9999, 9999, game)
    game.request_jump.assert_not_called()
