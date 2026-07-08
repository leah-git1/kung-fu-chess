from moves.move import Move
from moves.move_manager import MoveManager
from piece.piece_type import MovementStrategyFactory


class Game:


    MOVE_DURATION_PER_CELL = 1000


    def __init__(self, board):

        self.board = board

        self.selected = None

        self.current_time = 0

        self.move_manager = MoveManager()



    def handle_click(self, row, col):

        if not self.board.is_inside(row,col):
            return


        target = self.board.get_piece(row,col)



        if self.selected is None:


            if target != ".":
                self.selected = (row,col)


            return



        if self.selected == (row,col):

            self.selected = None
            return



        if target != "." and self.same_color(
            self.board.get_piece(*self.selected),
            target
        ):

            self.selected = (row,col)
            return



        piece = self.board.get_piece(
            *self.selected
        )

        if not self._is_legal_move(piece, self.selected, (row, col)):
            return

        if self.move_manager.is_any_piece_in_motion():
            return

        duration = self._move_duration(self.selected, (row, col))
        move = Move(
            piece,
            self.selected,
            (row,col),
            self.current_time + duration
        )


        self.move_manager.add_move(move)

        self.selected = None



    def _move_duration(self, start, end) -> int:
        sr, sc = start
        er, ec = end
        cells = max(abs(er - sr), abs(ec - sc))
        return cells * self.MOVE_DURATION_PER_CELL


    def _is_legal_move(self, piece, start, end):
        strategy = MovementStrategyFactory.for_token(piece)
        if strategy is None:
            return False
        return strategy.is_legal(piece, start, end, self.board)


    def same_color(self, p1, p2):

        if p1 is None or p2 is None:
            return False

        return p1[0] == p2[0]



    def advance_time(self, milliseconds):

        self.current_time += milliseconds

        self.update_moves()



    def update_moves(self):

        self.move_manager.update(
            self.current_time,
            self.board
        )