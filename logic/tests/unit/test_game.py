import config
from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType
from game.game import Game


PER_CELL = config.MOVE_DURATION_PER_CELL
JUMP = config.JUMP_DURATION


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def _board(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Board(grid)


def _cell(game, r, c):
    return game.get_piece_at((r, c))


# ------------------------------------------------------------------
# request_move — validation delegation
# ------------------------------------------------------------------

def test_legal_move_returns_true():
    game = Game(_board({(0, 0): "wR"}))
    assert game.request_move(_p("wR"), (0, 0), (0, 7)) is True


def test_illegal_move_returns_false():
    game = Game(_board({(0, 0): "wR"}))
    assert game.request_move(_p("wR"), (0, 0), (3, 5)) is False


def test_move_rejected_when_piece_already_moving():
    game = Game(_board({(0, 0): "wR"}))
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 7))
    assert game.request_move(rook, (0, 0), (0, 3)) is False


def test_different_piece_can_move_while_another_is_moving():
    game = Game(_board({(0, 0): "wR", (1, 0): "wK"}))
    rook = game.get_piece_at((0, 0))
    king = game.get_piece_at((1, 0))
    game.request_move(rook, (0, 0), (0, 7))
    assert game.request_move(king, (1, 0), (2, 0)) is True


def test_piece_can_move_again_after_arrival_and_cooldown():
    game = Game(_board({(0, 0): "wR"}))
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    game.advance_time(config.COOLDOWN_DURATION)
    assert game.request_move(rook, (0, 2), (0, 4)) is True


def test_piece_cannot_move_during_cooldown():
    game = Game(_board({(0, 0): "wR"}))
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert game.request_move(rook, (0, 2), (0, 4)) is False


def test_move_rejected_when_game_over():
    game = Game(_board({(0, 0): "wR"}))
    game.game_over = True
    assert game.request_move(_p("wR"), (0, 0), (0, 7)) is False


# ------------------------------------------------------------------
# advance_time — piece arrives at destination
# ------------------------------------------------------------------

def test_piece_arrives_after_duration():
    game = Game(_board({(0, 0): "wR"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert _cell(game, 0, 2) == _p("wR")
    assert _cell(game, 0, 0) is Piece.EMPTY


def test_piece_not_arrived_before_duration():
    game = Game(_board({(0, 0): "wR"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL - 1)
    assert _cell(game, 0, 0) == _p("wR")
    assert _cell(game, 0, 2) is Piece.EMPTY


def test_advance_time_ignored_when_game_over():
    game = Game(_board({(0, 0): "wR"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.game_over = True
    game.advance_time(2 * PER_CELL)
    assert _cell(game, 0, 0) == _p("wR")


def test_multi_cell_move_duration():
    game = Game(_board({(0, 0): "wR"}))
    game.request_move(_p("wR"), (0, 0), (0, 3))
    game.advance_time(2 * PER_CELL)
    assert _cell(game, 0, 0) == _p("wR")
    game.advance_time(PER_CELL)
    assert _cell(game, 0, 3) == _p("wR")


# ------------------------------------------------------------------
# advance_time — capture and game-over
# ------------------------------------------------------------------

def test_capturing_enemy_king_ends_game():
    game = Game(_board({(0, 0): "wR", (0, 2): "bK"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert game.game_over is True


def test_capturing_non_king_does_not_end_game():
    game = Game(_board({(0, 0): "wR", (0, 2): "bP"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert game.game_over is False


def test_enemy_at_destination_is_captured():
    game = Game(_board({(0, 0): "wR", (0, 2): "bP"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert _cell(game, 0, 2) == _p("wR")


def test_friendly_at_destination_cancels_move():
    game = Game(_board({(0, 0): "wR", (0, 2): "wP"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert _cell(game, 0, 2) == _p("wP")
    assert _cell(game, 0, 0) == _p("wR")


# ------------------------------------------------------------------
# advance_time — promotion
# ------------------------------------------------------------------

def test_white_pawn_promotes_on_row_0():
    game = Game(_board({(1, 0): "wP"}, rows=8))
    game.request_move(_p("wP"), (1, 0), (0, 0))
    game.advance_time(PER_CELL)
    assert _cell(game, 0, 0) == _p("wQ")


def test_black_pawn_promotes_on_last_row():
    game = Game(_board({(6, 0): "bP"}, rows=8))
    game.request_move(_p("bP"), (6, 0), (7, 0))
    game.advance_time(PER_CELL)
    assert _cell(game, 7, 0) == _p("bQ")


def test_pawn_does_not_promote_mid_board():
    game = Game(_board({(3, 0): "wP"}, rows=8))
    game.request_move(_p("wP"), (3, 0), (2, 0))
    game.advance_time(PER_CELL)
    assert _cell(game, 2, 0) == _p("wP")


# ------------------------------------------------------------------
# request_jump
# ------------------------------------------------------------------

def test_jump_returns_true():
    game = Game(_board({(0, 0): "wR"}))
    assert game.request_jump(_p("wR"), (0, 0)) is True


def test_jump_rejected_on_empty_piece():
    game = Game(_board({}))
    assert game.request_jump(Piece.EMPTY, (0, 0)) is False


def test_jump_rejected_when_game_over():
    game = Game(_board({(0, 0): "wR"}))
    game.game_over = True
    assert game.request_jump(_p("wR"), (0, 0)) is False


def test_jump_rejected_when_already_airborne():
    game = Game(_board({(0, 0): "wR"}))
    game.request_jump(_p("wR"), (0, 0))
    assert game.request_jump(_p("wR"), (0, 0)) is False


def test_jump_rejected_when_move_in_progress():
    game = Game(_board({(0, 0): "wR", (1, 0): "wK"}))
    rook = game.get_piece_at((0, 0))
    game.request_move(rook, (0, 0), (0, 7))
    assert game.request_jump(rook, (0, 0)) is False


def test_jump_rejected_after_piece_captured():
    game = Game(_board({(0, 0): "wR", (0, 2): "bR"}))
    game.request_move(_p("wR"), (0, 0), (0, 2))
    game.advance_time(2 * PER_CELL)
    assert game.request_jump(_p("bR"), (0, 2)) is False


# ------------------------------------------------------------------
# snapshot / get_piece_at / is_inside
# ------------------------------------------------------------------

def test_snapshot_returns_copy():
    game = Game(_board({(0, 0): "wR"}))
    snap = game.snapshot()
    snap[0][0] = Piece.EMPTY
    assert _cell(game, 0, 0) == _p("wR")


def test_get_piece_at_returns_correct_piece():
    game = Game(_board({(2, 3): "bQ"}))
    assert game.get_piece_at((2, 3)) == _p("bQ")


def test_is_inside_true_for_valid_cell():
    game = Game(_board({}, rows=8, cols=8))
    assert game.is_inside((0, 0)) is True
    assert game.is_inside((7, 7)) is True


def test_is_inside_false_for_out_of_bounds():
    game = Game(_board({}, rows=8, cols=8))
    assert game.is_inside((8, 0)) is False
    assert game.is_inside((0, 8)) is False
