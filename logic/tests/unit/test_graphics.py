import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pytest
from graphics.img_provider import GameImg
from graphics.layout import Layout
import graphics.gfx_config as gfx_config


# ── GameImg ──────────────────────────────────────────────────────────────────

class TestGameImgBlank:
    def test_shape_is_4_channel(self):
        img = GameImg.blank(10, 20)
        assert img.img.shape == (20, 10, 4)

    def test_default_color_is_transparent_black(self):
        img = GameImg.blank(5, 5)
        assert np.all(img.img == 0)

    def test_custom_color_stored_as_bgra(self):
        img = GameImg.blank(1, 1, color=(255, 0, 0, 255))   # red RGBA
        b, g, r, a = img.img[0, 0]
        assert (r, g, b, a) == (255, 0, 0, 255)

    def test_dimensions_respected(self):
        img = GameImg.blank(30, 40)
        h, w = img.img.shape[:2]
        assert w == 30 and h == 40


class TestGameImgResize:
    def _make(self, w, h):
        return GameImg.blank(w, h, color=(100, 150, 200, 255))

    def test_resize_changes_dimensions(self):
        out = self._make(50, 50).resize(20, 30)
        assert out.img.shape[:2] == (30, 20)

    def test_resize_clamps_to_minimum_1(self):
        out = self._make(10, 10).resize(0, 0)
        assert out.img.shape[0] >= 1 and out.img.shape[1] >= 1

    def test_resize_returns_new_instance(self):
        src = self._make(10, 10)
        out = src.resize(5, 5)
        assert out is not src


class TestGameImgWithAlphaScale:
    def test_full_scale_preserves_alpha(self):
        img = GameImg.blank(4, 4, color=(0, 0, 0, 200))
        out = img.with_alpha_scale(1.0)
        assert np.all(out.img[:, :, 3] == 200)

    def test_zero_scale_makes_transparent(self):
        img = GameImg.blank(4, 4, color=(0, 0, 0, 200))
        out = img.with_alpha_scale(0.0)
        assert np.all(out.img[:, :, 3] == 0)

    def test_half_scale_halves_alpha(self):
        img = GameImg.blank(4, 4, color=(0, 0, 0, 200))
        out = img.with_alpha_scale(0.5)
        assert np.all(out.img[:, :, 3] == 100)

    def test_does_not_mutate_original(self):
        img = GameImg.blank(4, 4, color=(0, 0, 0, 200))
        img.with_alpha_scale(0.0)
        assert np.all(img.img[:, :, 3] == 200)

    def test_returns_new_instance(self):
        img = GameImg.blank(4, 4)
        assert img.with_alpha_scale(1.0) is not img


# ── Layout ───────────────────────────────────────────────────────────────────

class TestLayout:
    def _layout(self, w=None, h=None):
        w = w or gfx_config.WINDOW_PX_W
        h = h or gfx_config.WINDOW_PX_H
        return Layout(w, h)

    def test_scale_is_positive(self):
        assert self._layout().scale > 0

    def test_board_fits_within_available_area(self):
        lay = self._layout()
        available_w = lay.window_px_w - gfx_config.SIDEBAR_PX_W
        assert lay.board_px_w <= available_w
        assert lay.board_px_h <= lay.window_px_h

    def test_on_resize_updates_scale(self):
        lay = self._layout()
        old_scale = lay.scale
        lay.on_resize(lay.window_px_w * 2, lay.window_px_h * 2)
        assert lay.scale != old_scale

    def test_screen_to_board_pixel_inside(self):
        lay = self._layout()
        cx = lay.board_origin_x + lay.board_px_w // 2
        cy = lay.board_origin_y + lay.board_px_h // 2
        result = lay.screen_to_board_pixel(cx, cy)
        assert result is not None

    def test_screen_to_board_pixel_outside_returns_none(self):
        lay = self._layout()
        assert lay.screen_to_board_pixel(-1, -1) is None

    def test_screen_to_board_pixel_sidebar_returns_none(self):
        lay = self._layout()
        # click in the sidebar area (right of board)
        result = lay.screen_to_board_pixel(lay.window_px_w - 1, lay.window_px_h // 2)
        assert result is None

    def test_cell_to_screen_rect_origin_cell(self):
        lay = self._layout()
        x, y, w, h = lay.cell_to_screen_rect(0, 0)
        assert x == lay.board_origin_x
        assert y == lay.board_origin_y
        assert w > 0 and h > 0

    def test_cell_to_screen_rect_size_consistent(self):
        lay = self._layout()
        _, _, w0, h0 = lay.cell_to_screen_rect(0, 0)
        _, _, w1, h1 = lay.cell_to_screen_rect(3, 5)
        assert w0 == w1 and h0 == h1

    def test_tiny_window_does_not_crash(self):
        lay = Layout(gfx_config.SIDEBAR_PX_W + 1, 1)
        assert lay.scale > 0
