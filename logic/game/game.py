from moves.move_action import MoveAction
from moves.jump_action import JumpAction
from moves.action_manager import ActionManager
from piece.piece import Piece
from piece.piece_type import MovementStrategyFactory, PieceType
import config


class Game:


    def __init__(self, board):
        self.board = board
        self.selected = None
        self.current_time = 0
        self.action_manager = ActionManager()
        self.game_over = False



    def handle_click(self, row, col):

        if self.game_over:
            return

        if not self.board.is_inside(row, col):
            return

        target = self.board.get_piece(row, col)

        if self.selected is None:
            if target != Piece.EMPTY:
                self.selected = (row, col)
            return

        if self.selected == (row, col):
            self.selected = None
            return

        if target != Piece.EMPTY and self.same_color(
            self.board.get_piece(*self.selected), target
        ):
            self.selected = (row, col)
            return

        piece = self.board.get_piece(*self.selected)

        if not self._is_legal_move(piece, self.selected, (row, col)):
            return

        if self.action_manager.is_any_moving():
            return

        duration = self._move_duration(self.selected, (row, col))
        self.action_manager.add(MoveAction(
            piece,
            self.selected,
            (row, col),
            self.current_time + duration
        ))
        self.selected = None



    def handle_jump(self, row, col):

        if self.game_over:
            return

        if not self.board.is_inside(row, col):
            return

        piece = self.board.get_piece(row, col)

        if piece is None or piece == Piece.EMPTY:
            return

        if self.action_manager.is_any_moving():
            return

        if self.action_manager.is_airborne((row, col)):
            return

        self.action_manager.add(JumpAction(
            piece,
            (row, col),
            self.current_time + config.JUMP_DURATION
        ))



    def advance_time(self, milliseconds):

        if self.game_over:
            return

        self.current_time += milliseconds
        self._tick()



    def _tick(self):

        captured, applied_moves = self.action_manager.update(
            self.current_time,
            self.board
        )

        if any(self._is_king(p) for p in captured):
            self.game_over = True

        for move in applied_moves:
            self._apply_promotion_if_needed(move)



    def _apply_promotion_if_needed(self, move: MoveAction):
        piece = self.board.get_piece(*move.destination)
        if piece is None or piece == Piece.EMPTY or piece.piece_type != PieceType.PAWN:
            return
        promotion_row = 0 if piece.color == "w" else self.board.rows - 1
        if move.destination[0] == promotion_row:
            self.board.set_piece(
                move.destination[0],
                move.destination[1],
                Piece(piece.color, PieceType.QUEEN)
            )



    def _is_king(self, piece) -> bool:
        return piece != Piece.EMPTY and piece.piece_type == PieceType.KING



    def _move_duration(self, start, end) -> int:
        sr, sc = start
        er, ec = end
        return max(abs(er - sr), abs(ec - sc)) * config.MOVE_DURATION_PER_CELL



    def _is_legal_move(self, piece, start, end) -> bool:
        strategy = MovementStrategyFactory.for_piece(piece)
        if strategy is None:
            return False
        return strategy.is_legal(piece, start, end, self.board)



    def update_moves(self):
        self._tick()


    def same_color(self, p1, p2) -> bool:
        if p1 is None or p2 is None or p1 == Piece.EMPTY or p2 == Piece.EMPTY:
            return False
        return p1.is_same_color(p2)
