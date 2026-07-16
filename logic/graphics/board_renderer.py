import cv2
import numpy as np
from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.layout import Layout


def _recolor_board(src_img: GameImg, light_bgra, dark_bgra) -> GameImg:
    """Replace white squares with light color and black squares with dark color."""
    bgr = src_img.img[:, :, :3]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # white pixels (>128) -> light square color, dark pixels (<=128) -> dark square color
    lb, lg, lr, _ = light_bgra
    db, dg, dr, _ = dark_bgra
    out_bgr = np.zeros_like(bgr)
    mask = gray > 128
    out_bgr[mask]  = (lb, lg, lr)
    out_bgr[~mask] = (db, dg, dr)
    result = GameImg()
    result.img = cv2.cvtColor(out_bgr, cv2.COLOR_BGR2BGRA)
    return result


class BoardRenderer:
    def __init__(self, layout: Layout):
        self._layout = layout
        self._raw_board = GameImg.read(gfx_config.BOARD_IMAGE_PATH,
                                       size=(gfx_config.BOARD_PX_W, gfx_config.BOARD_PX_H))
        cell = gfx_config.CELL_PX
        self._select_tile = GameImg.blank(cell, cell, gfx_config.COLOR_SELECTED)
        self._legal_tile  = GameImg.blank(cell, cell, gfx_config.COLOR_LEGAL_DOT)
        self._scaled_cache_scale = None

    def _rescale_if_needed(self):
        if self._scaled_cache_scale == self._layout.scale:
            return
        self._scaled_cache_scale = self._layout.scale
        resized = self._raw_board.resize(self._layout.board_px_w, self._layout.board_px_h)
        light = gfx_config.COLOR_LIGHT_SQUARE
        dark  = gfx_config.COLOR_DARK_SQUARE
        self._scaled_board = _recolor_board(resized,
                                            (light[2], light[1], light[0], light[3]),
                                            (dark[2],  dark[1],  dark[0],  dark[3]))
        # cell size derived from actual rendered board width — single source of truth
        cell = max(1, self._layout.board_px_w // gfx_config.BOARD_COLS)
        self._scaled_select = self._select_tile.resize(cell, cell)
        self._scaled_legal  = self._legal_tile.resize(cell, cell)

    def render(self, canvas, selected_cell=None, legal_cells=()):
        self._rescale_if_needed()
        self._scaled_board.draw_on(canvas, self._layout.board_origin_x, self._layout.board_origin_y)
        if selected_cell is not None:
            x, y, _, _ = self._layout.cell_to_screen_rect(*selected_cell)
            self._scaled_select.draw_on(canvas, x, y)
        for cell in legal_cells:
            x, y, _, _ = self._layout.cell_to_screen_rect(*cell)
            self._scaled_legal.draw_on(canvas, x, y)
        self._draw_coordinates(canvas)

    def _draw_coordinates(self, canvas):
        lm = gfx_config.BOARD_LABEL_MARGIN
        ox = self._layout.board_origin_x
        oy = self._layout.board_origin_y
        lox = self._layout.label_origin_x
        loy = self._layout.label_origin_y
        # use same cell size as everything else
        cell = self._layout.board_px_w // gfx_config.BOARD_COLS
        bw = self._layout.board_px_w
        bh = self._layout.board_px_h
        color = (220, 220, 220)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fscale = 0.40
        thickness = 1

        for i in range(8):
            rank = str(8 - i)
            cy = oy + i * cell + cell // 2
            (tw, th), _ = cv2.getTextSize(rank, font, fscale, thickness)
            ty = cy + th // 2
            cv2.putText(canvas.img, rank, (lox + (lm - tw) // 2, ty),
                        font, fscale, color, thickness, cv2.LINE_AA)
            cv2.putText(canvas.img, rank, (ox + bw + (lm - tw) // 2, ty),
                        font, fscale, color, thickness, cv2.LINE_AA)

            letter = chr(ord('a') + i)
            cx = ox + i * cell + cell // 2
            (tw, th), _ = cv2.getTextSize(letter, font, fscale, thickness)
            tx = cx - tw // 2
            cv2.putText(canvas.img, letter, (tx, loy + (lm + th) // 2),
                        font, fscale, color, thickness, cv2.LINE_AA)
            cv2.putText(canvas.img, letter, (tx, oy + bh + (lm + th) // 2),
                        font, fscale, color, thickness, cv2.LINE_AA)