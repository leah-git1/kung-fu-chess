from board.piece import Piece
from controller.board_mapper import BoardMapper


class InputController:
    """
    Translates user input into game commands.

    Responsibilities:
    - Receive pixel coordinates
    - Convert pixels to board cells via BoardMapper
    - Maintain selected-cell state
    - On first click: select a piece (ignore empty cells)
    - On second click: call game.request_move(piece, source, destination)
    - Clear selection after every second click, legal or not
    - Click outside board with no selection: ignore
    - Click outside board with selection: cancel selection, no game command

    No knowledge of: chess legality, board mutation, rendering, timing.
    """

    def __init__(self, mapper: BoardMapper):
        self._mapper = mapper
        self._selected = None

    @property
    def selected(self):
        return self._selected

    def on_click(self, x: int, y: int, game) -> None:
        cell = self._mapper.to_cell(x, y)

        if not game.is_inside(cell):
            if self._selected is not None:
                self._selected = None
            return

        piece = game.get_piece_at(cell)

        if self._selected is None:
            if piece is not Piece.EMPTY:
                self._selected = cell
            return

        if self._selected == cell:
            self._selected = None
            return

        source_piece = game.get_piece_at(self._selected)
        if piece is not Piece.EMPTY and source_piece.is_same_color(piece):
            self._selected = cell
            return

        game.request_move(source_piece, self._selected, cell)
        self._selected = None

    def on_jump(self, x: int, y: int, game) -> None:
        cell = self._mapper.to_cell(x, y)
        if not game.is_inside(cell):
            return
        piece = game.get_piece_at(cell)
        if piece is not Piece.EMPTY:
            game.request_jump(piece, cell)
