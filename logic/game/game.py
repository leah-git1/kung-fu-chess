from board.piece import Piece
from rules.rule_engine import RuleEngine
from realtime.real_time_arbiter import RealTimeArbiter
import config


class Game:
    """Coordinates board state, move validation, real-time motion, and game-over detection."""

    def __init__(self, board):
        self._board = board
        self.current_time = 0
        self._game_over = False
        self._arbiter = RealTimeArbiter()
        self._rules = RuleEngine()

    @property
    def game_over(self) -> bool:
        return self._game_over

    @game_over.setter
    def game_over(self, value: bool) -> None:
        self._game_over = value

    # ------------------------------------------------------------------
    # Public API — intent-based, no input interpretation
    # ------------------------------------------------------------------

    def request_move(self, piece, start, end) -> bool:
        if self._game_over:
            return False
        if not self._rules.is_legal_move(piece, start, end, self._board):
            return False
        if not self._arbiter.is_piece_available(piece):
            return False
        duration = self._move_duration(start, end)
        self._arbiter.add_move(piece, start, end, self.current_time + duration)
        return True

    def request_jump(self, piece, cell) -> bool:
        if self._game_over:
            return False
        if piece is Piece.EMPTY:
            return False
        if self._arbiter.is_any_moving():
            return False
        if self._arbiter.is_airborne(cell):
            return False
        if self._board.get_piece(*cell) != piece:
            return False
        self._arbiter.add_jump(piece, cell, self.current_time + config.JUMP_DURATION)
        return True

    def advance_time(self, milliseconds) -> None:
        if self._game_over:
            return
        self.current_time += milliseconds
        self._tick()

    def snapshot(self) -> list:
        return list(self._board.rows_iter())

    def active_moves(self) -> list:
        return self._arbiter.active_moves()

    def active_jumps(self) -> list:
        return self._arbiter.active_jumps()
        
    def get_piece_at(self, cell: tuple):
        return self._board.get_piece(*cell)

    def is_inside(self, cell: tuple) -> bool:
        return self._board.is_inside(*cell)

    # ------------------------------------------------------------------
    # Internal coordination
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        captured, applied_moves = self._arbiter.advance(self.current_time, self._board)
        self._process_captures(captured)
        self._process_arrivals(applied_moves)

    def _process_captures(self, captured) -> None:
        if any(self._is_royal(p) for p in captured):
            self._game_over = True

    def _process_arrivals(self, applied_moves) -> None:
        for move in applied_moves:
            self._apply_on_arrival(move)

    def _apply_on_arrival(self, move) -> None:
        piece = self._board.get_piece(*move.destination)
        if piece is Piece.EMPTY:
            return
        strategy = self._rules.strategy_for(piece)
        if strategy is None:
            return
        result = strategy.on_arrival(piece, move.destination, self._board)
        if result is not piece:
            self._board.set_piece(move.destination[0], move.destination[1], result)

    def _is_royal(self, piece) -> bool:
        return piece is not Piece.EMPTY and piece.piece_type.value in config.ROYAL_PIECE_TYPES

    def _move_duration(self, start, end) -> int:
        return max(abs(end[0] - start[0]), abs(end[1] - start[1])) * config.MOVE_DURATION_PER_CELL
