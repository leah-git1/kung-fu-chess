from board.board import Board
from board.piece import Piece
from board.piece_type import PieceType
from rules.rule_engine import RuleEngine


_engine = RuleEngine()


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def empty_board(rows=8, cols=8):
    return Board([[Piece.EMPTY] * cols for _ in range(rows)])


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Board(grid)


def test_legal_move_returns_true():
    b = empty_board()
    assert _engine.is_legal_move(_p("wR"), (0, 0), (0, 7), b)


def test_illegal_move_returns_false():
    b = empty_board()
    assert not _engine.is_legal_move(_p("wR"), (0, 0), (3, 5), b)


def test_empty_piece_returns_false():
    b = empty_board()
    assert not _engine.is_legal_move(Piece.EMPTY, (0, 0), (0, 1), b)


def test_does_not_mutate_board():
    b = board_with({(0, 0): "wR"})
    _engine.is_legal_move(_p("wR"), (0, 0), (0, 7), b)
    assert b.get_piece(0, 0) == _p("wR")
    assert b.get_piece(0, 7) is Piece.EMPTY


def test_blocked_path_returns_false():
    b = board_with({(0, 0): "wR", (0, 3): "wP"})
    assert not _engine.is_legal_move(_p("wR"), (0, 0), (0, 7), b)


def test_capture_enemy_returns_true():
    b = board_with({(0, 0): "wR", (0, 7): "bP"})
    assert _engine.is_legal_move(_p("wR"), (0, 0), (0, 7), b)


def test_capture_friendly_returns_false():
    b = board_with({(0, 0): "wR", (0, 7): "wP"})
    assert not _engine.is_legal_move(_p("wR"), (0, 0), (0, 7), b)
