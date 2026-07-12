class Motion:
    """Base class for a timed in-flight action."""

    def __init__(self, piece, finish_time: int):
        self.piece = piece
        self.finish_time = finish_time

    def is_finished(self, current_time: int) -> bool:
        return current_time >= self.finish_time


class MoveMotion(Motion):
    """Represents a piece moving from one cell to another over time."""

    def __init__(self, piece, origin, destination, finish_time: int):
        super().__init__(piece, finish_time)
        self.origin = origin
        self.destination = destination


class JumpMotion(Motion):
    """Represents a piece jumping in place, making it airborne for a duration."""

    def __init__(self, piece, cell, finish_time: int):
        super().__init__(piece, finish_time)
        self.cell = cell


class CooldownMotion(Motion):
    """Represents a piece in cooldown after arriving — cannot move until resolved."""
    pass
