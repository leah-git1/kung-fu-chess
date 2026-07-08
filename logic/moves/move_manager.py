class MoveManager:

    def __init__(self):
        self.moves = []


    def add_move(self, move):
        self.moves.append(move)


    def is_any_piece_in_motion(self) -> bool:
        return len(self.moves) > 0


    def update(self, current_time, board):

        for move in self.moves:
            if move.is_finished(current_time):
                move.completed = True
                destination = board.get_piece(*move.end)
                if destination == "." or destination[0] != move.piece[0]:
                    board.move(move.start, move.end)


        self.moves = [
            m for m in self.moves
            if not m.completed
        ]