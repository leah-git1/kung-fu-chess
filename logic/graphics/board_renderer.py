from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.layout import Layout

class BoardRenderer:
    def __init__(self, layout: Layout):
        self._layout = layout
        self._board_image = GameImg.read(gfx_config.BOARD_IMAGE_PATH,
                                          size=(gfx_config.BOARD_PX_W, gfx_config.BOARD_PX_H))
        cell = gfx_config.CELL_PX
        self._select_tile = GameImg.blank(cell, cell, gfx_config.COLOR_SELECTED)
        self._legal_tile = GameImg.blank(cell, cell, gfx_config.COLOR_LEGAL_DOT)
        self._scaled_cache_scale = None

    def _rescale_if_needed(self):
        if self._scaled_cache_scale == self._layout.scale:
            return
        self._scaled_cache_scale = self._layout.scale
        self._scaled_board = self._board_image.resize(self._layout.board_px_w, self._layout.board_px_h)
        cell = max(1, int(gfx_config.CELL_PX * self._layout.scale))
        self._scaled_select = self._select_tile.resize(cell, cell)
        self._scaled_legal = self._legal_tile.resize(cell, cell)

    def render(self, canvas, selected_cell=None, legal_cells=()):
        self._rescale_if_needed()
        self._scaled_board.draw_on(canvas, self._layout.board_origin_x, self._layout.board_origin_y)
        if selected_cell is not None:
            x, y, _, _ = self._layout.cell_to_screen_rect(*selected_cell)
            self._scaled_select.draw_on(canvas, x, y)
        for cell in legal_cells:
            x, y, _, _ = self._layout.cell_to_screen_rect(*cell)
            self._scaled_legal.draw_on(canvas, x, y)