from moves.move_action import MoveAction
from moves.jump_action import JumpAction
from moves.action_manager import ActionManager
from piece.piece_type import MovementStrategyFactory, PieceType


class Game:

    MOVE_DURATION_PER_CELL = 1000
    JUMP_DURATION = 1000
    _KING_TYPE_CHAR = PieceType.KING.value
    _PAWN_TYPE_CHAR = PieceType.PAWN.value
    _QUEEN_TYPE_CHAR = PieceType.QUEEN.value


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
            if target != ".":
                self.selected = (row, col)
            return

        if self.selected == (row, col):
            self.selected = None
            return

        if target != "." and self.same_color(
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

        if piece is None or piece == ".":
            return

        if self.action_manager.is_any_moving():
            return

        if self.action_manager.is_airborne((row, col)):
            return

        self.action_manager.add(JumpAction(
            piece,
            (row, col),
            self.current_time + self.JUMP_DURATION
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
        if piece is None or piece[1] != self._PAWN_TYPE_CHAR:
            return
        color = piece[0]
        promotion_row = 0 if color == "w" else self.board.rows - 1
        if move.destination[0] == promotion_row:
            self.board.grid[move.destination[0]][move.destination[1]] = (
                color + self._QUEEN_TYPE_CHAR
            )



    def _is_king(self, token: str) -> bool:
        return len(token) == 2 and token[1] == self._KING_TYPE_CHAR



    def _move_duration(self, start, end) -> int:
        sr, sc = start
        er, ec = end
        return max(abs(er - sr), abs(ec - sc)) * self.MOVE_DURATION_PER_CELL



    def _is_legal_move(self, piece, start, end) -> bool:
        strategy = MovementStrategyFactory.for_token(piece)
        if strategy is None:
            return False
        return strategy.is_legal(piece, start, end, self.board)



    def update_moves(self):
        self._tick()


    def same_color(self, p1, p2) -> bool:
        if p1 is None or p2 is None:
            return False
        return p1[0] == p2[0]
