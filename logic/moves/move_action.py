from moves.action import Action


class MoveAction(Action):

    def __init__(self, piece: str, origin, destination, finish_time: int):
        super().__init__(piece, origin, finish_time)
        self.origin = origin
        self.destination = destination

    def resolve(self, board, captured: list, applied: list):
        destination_piece = board.get_piece(*self.destination)

        if destination_piece != "." and destination_piece.is_same_color(self.piece):
            # Friendly at destination — cancel silently, piece stays at origin
            return

        if destination_piece != ".":
            captured.append(destination_piece)

        board.move(self.origin, self.destination)
        applied.append(self)
