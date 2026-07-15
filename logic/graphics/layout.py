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
        gap = gfx_config.BOARD_SIDE_GAP
        available_w = max(1, self.window_px_w - 2 * gfx_config.SIDEBAR_PX_W - 2 * gap)
        available_h = max(1, self.window_px_h - gfx_config.TOP_BAR_H)
        self.scale = min(available_w / gfx_config.BOARD_PX_W, available_h / gfx_config.BOARD_PX_H)
        self.board_px_w = int(gfx_config.BOARD_PX_W * self.scale)
        self.board_px_h = int(gfx_config.BOARD_PX_H * self.scale)
        self.board_origin_x = gfx_config.SIDEBAR_PX_W + gap + (available_w - self.board_px_w) // 2
        self.board_origin_y = gfx_config.TOP_BAR_H + (available_h - self.board_px_h) // 2
        self.left_sidebar_x = 0
        self.right_sidebar_x = self.board_origin_x + self.board_px_w + gap
        # legacy alias
        self.sidebar_origin_x = self.right_sidebar_x

    def screen_to_board_pixel(self, screen_x, screen_y):
        bx = screen_x - self.board_origin_x
        by = screen_y - self.board_origin_y
        if bx < 0 or by < 0 or bx >= self.board_px_w or by >= self.board_px_h:
            return None
        return int(bx / self.scale), int(by / self.scale)

    def cell_to_screen_rect(self, row, col):
        x = self.board_origin_x + int(col * gfx_config.CELL_PX * self.scale)
        y = self.board_origin_y + int(row * gfx_config.CELL_PX * self.scale)
        size = int(gfx_config.CELL_PX * self.scale)
        return x, y, size, size