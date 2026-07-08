class Move:
    def __init__(self, piece, start, end, finish_time):
        self.piece = piece
        self.start = start
        self.end = end
        self.finish_time = finish_time
        self.completed = False

    def is_finished(self, current_time):
        return current_time >= self.finish_time