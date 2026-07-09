import config
from board.piece import Piece


class BoardPrinter:
    """Renders a board snapshot to text. Symmetric counterpart to BoardParser."""

    def render(self, snapshot: list) -> str:
        return "\n".join(
            " ".join(self._cell_token(cell) for cell in row)
            for row in snapshot
        )

    def _cell_token(self, cell) -> str:
        if cell is Piece.EMPTY:
            return config.EMPTY_CELL
        return cell.color + cell.piece_type.value
