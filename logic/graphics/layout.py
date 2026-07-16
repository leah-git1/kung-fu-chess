from graphics import gfx_config

class Layout:
    def __init__(self, window_px_w=gfx_config.WINDOW_PX_W, window_px_h=gfx_config.WINDOW_PX_H):
        self.window_px_w = window_px_w
        self.window_px_h = window_px_h
        self._recompute()

    def on_resize(self, new_w, new_h):
        self.window_px_w, self.window_px_h = new_w, new_h
        self._recompute()

    def _recompute(self):
        sm = gfx_config.SIDEBAR_MARGIN
        sw = gfx_config.SIDEBAR_PX_W
        gap = gfx_config.BOARD_SIDE_GAP
        lm = gfx_config.BOARD_LABEL_MARGIN
        ds = gfx_config.BOARD_DISPLAY_SCALE
        W, H = self.window_px_w, self.window_px_h

        # sidebars pinned to window edges with a margin
        self.left_sidebar_x  = sm
        self.right_sidebar_x = W - sm - sw

        # board+label block lives in the middle column
        mid_x0 = sm + sw + gap          # left edge of middle column
        mid_x1 = W - sm - sw - gap      # right edge of middle column
        mid_w  = max(1, mid_x1 - mid_x0)
        mid_h  = max(1, H - gfx_config.TOP_BAR_H)

        # fit board into middle column, then apply display scale
        fit_scale = min((mid_w - 2 * lm) / gfx_config.BOARD_PX_W,
                        (mid_h - 2 * lm) / gfx_config.BOARD_PX_H)
        self.scale = fit_scale * ds
        # snap board size to exact multiple of BOARD_COLS/ROWS so cell_size * 8 == board size
        cell_size = max(1, int(gfx_config.CELL_PX * self.scale))
        self.cell_size = cell_size
        self.board_px_w = cell_size * gfx_config.BOARD_COLS
        self.board_px_h = cell_size * gfx_config.BOARD_ROWS

        # center the board+label block inside the middle column
        block_w = self.board_px_w + 2 * lm
        block_h = self.board_px_h + 2 * lm
        block_x = mid_x0 + (mid_w - block_w) // 2
        block_y = gfx_config.TOP_BAR_H + (mid_h - block_h) // 2

        # board origin is inset by lm (labels live in the margin)
        self.board_origin_x = block_x + lm
        self.board_origin_y = block_y + lm
        self.label_origin_x = block_x
        self.label_origin_y = block_y

        # legacy alias
        self.sidebar_origin_x = self.right_sidebar_x

    def screen_to_board_pixel(self, screen_x, screen_y):
        bx = screen_x - self.board_origin_x
        by = screen_y - self.board_origin_y
        if bx < 0 or by < 0 or bx >= self.board_px_w or by >= self.board_px_h:
            return None
        # scale back to unscaled board pixels using actual rendered board size
        ux = int(bx * gfx_config.BOARD_PX_W / self.board_px_w)
        uy = int(by * gfx_config.BOARD_PX_H / self.board_px_h)
        return ux, uy

    def cell_to_screen_rect(self, row, col):
        x = self.board_origin_x + col * self.cell_size
        y = self.board_origin_y + row * self.cell_size
        return x, y, self.cell_size, self.cell_size