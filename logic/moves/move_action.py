from moves.action import Action
from logic.board.piece import Piece


class MoveAction(Action):

    def __init__(self, piece: str, origin, destination, finish_time: int):
        super().__init__(piece, origin, finish_time)
        self.origin = origin
        self.destination = destination

    def resolve(self, board, captured: list, applied: list):
        destination_piece = board.get_piece(*self.destination)

        if destination_piece is not Piece.EMPTY and destination_piece.is_same_color(self.piece):
            return

        if destination_piece is not Piece.EMPTY:
            captured.append(destination_piece)

        board.move(self.origin, self.destination)
        applied.append(self)
