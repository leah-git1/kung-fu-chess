class MoveManager:

    def __init__(self):
        self.moves = []


    def add_move(self, move):
        self.moves.append(move)


    def is_piece_in_motion(self, position) -> bool:
        return any(m.start == position for m in self.moves)


    def update(self, current_time, board):

        for move in self.moves:
            if move.is_finished(current_time):
                board.move(
                    move.start,
                    move.end
                )
                move.completed = True


        self.moves = [
            m for m in self.moves
            if not m.completed
        ]