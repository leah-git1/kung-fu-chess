from moves.action import Action


class JumpAction(Action):

    def __init__(self, piece: str, cell, finish_time: int):
        super().__init__(piece, cell, finish_time)

    def resolve(self, board, captured: list, applied: list):
        # Piece stays in its cell — no board mutation needed on landing
        pass
