class BoardMapper:
    """Converts pixel coordinates to board cell coordinates."""

    def __init__(self, cell_size: int):
        self._cell_size = cell_size

    def to_cell(self, x: int, y: int) -> tuple:
        return (y // self._cell_size, x // self._cell_size)
