class BoardPrinter:
    """Renders a board snapshot to text. Symmetric counterpart to BoardParser."""

    def render(self, snapshot: list) -> str:
        return "\n".join(
            " ".join(self._cell_token(cell) for cell in row)
            for row in snapshot
        )

    def _cell_token(self, cell) -> str:
        return repr(cell)
