from board.piece import Piece
from board.piece_type import PieceType
from rules.rule_engine import RuleEngine
from rules.real_time_arbiter import RealTimeArbiter
import config


class Game:

    def __init__(self, board):
        self.board = board
        self.current_time = 0
        self.game_over = False
        self._arbiter = RealTimeArbiter()
        self._rules = RuleEngine()

    # ------------------------------------------------------------------
    # Public API — intent-based, no input interpretation
    # ------------------------------------------------------------------

    def request_move(self, piece, start, end) -> bool:
        if self.game_over:
            return False
        if not self._rules.is_legal_move(piece, start, end, self.board):
            return False
        if self._arbiter.is_any_moving():
            return False
        duration = self._move_duration(start, end)
        self._arbiter.add_move(piece, start, end, self.current_time + duration)
        return True

    def request_jump(self, piece, cell) -> bool:
        if self.game_over:
            return False
        if piece is Piece.EMPTY:
            return False
        if self._arbiter.is_any_moving():
            return False
        if self._arbiter.is_airborne(cell):
            return False
        if self.board.get_piece(*cell) != piece:
            return False
        self._arbiter.add_jump(piece, cell, self.current_time + config.JUMP_DURATION)
        return True

    def advance_time(self, milliseconds) -> None:
        if self.game_over:
            return
        self.current_time += milliseconds
        self._tick()

    def snapshot(self) -> list:
        return [row[:] for row in self.board.grid]

    def get_piece_at(self, cell: tuple):
        return self.board.get_piece(*cell)

    def is_inside(self, cell: tuple) -> bool:
        return self.board.is_inside(*cell)

    # ------------------------------------------------------------------
    # Internal coordination
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        captured, applied_moves = self._arbiter.advance(self.current_time, self.board)
        if any(self._is_king(p) for p in captured):
            self.game_over = True
        for move in applied_moves:
            self._apply_on_arrival(move)

    def _apply_on_arrival(self, move) -> None:
        piece = self.board.get_piece(*move.destination)
        if piece is Piece.EMPTY:
            return
        strategy = self._rules.strategy_for(piece)
        if strategy is None:
            return
        result = strategy.on_arrival(piece, move.destination, self.board)
        if result is not piece:
            self.board.set_piece(move.destination[0], move.destination[1], result)

    def _is_king(self, piece) -> bool:
        return piece is not Piece.EMPTY and piece.piece_type == PieceType.KING

    def _move_duration(self, start, end) -> int:
        return max(abs(end[0] - start[0]), abs(end[1] - start[1])) * config.MOVE_DURATION_PER_CELL
