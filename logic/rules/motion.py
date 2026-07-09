class Motion:

    def __init__(self, piece, finish_time: int):
        self.piece = piece
        self.finish_time = finish_time

    def is_finished(self, current_time: int) -> bool:
        return current_time >= self.finish_time


class MoveMotion(Motion):

    def __init__(self, piece, origin, destination, finish_time: int):
        super().__init__(piece, finish_time)
        self.origin = origin
        self.destination = destination


class JumpMotion(Motion):

    def __init__(self, piece, cell, finish_time: int):
        super().__init__(piece, finish_time)
        self.cell = cell
