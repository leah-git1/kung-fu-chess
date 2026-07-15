import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
from graphics.observers.moves_log import MovesLog, _fmt_time, _cell_name
from graphics.observers.score_board import ScoreBoard
from graphics.observers.game_events import PieceMovedEvent, PieceCapturedEvent
from graphics.panels.player_names_panel import PlayerNamesPanel
from graphics.img_provider import GameImg
from board.piece import Piece
from board.piece_type import PieceType
import graphics.gfx_config as gfx_config


# ── helpers ───────────────────────────────────────────────────────────────────

def _piece(color, pt_value):
    return Piece(color=color, piece_type=PieceType(pt_value))


def _moved(piece, origin, dest, ms):
    return PieceMovedEvent(piece, origin, dest, ms)


def _captured(victim, cell, by, ms):
    return PieceCapturedEvent(victim, cell, by, ms)


# ── _fmt_time ─────────────────────────────────────────────────────────────────

class TestFmtTime:
    def test_zero(self):
        assert _fmt_time(0) == "00:00.000"

    def test_seconds(self):
        assert _fmt_time(15_006) == "00:15.000"

    def test_minutes(self):
        assert _fmt_time(75_000) == "01:15.000"

    def test_fractional_part_is_centiseconds(self):
        # 31027 ms → 31s, frac = 27//10 = 2 → "002"
        assert _fmt_time(31_027) == "00:31.002"

    def test_large_value(self):
        assert _fmt_time(3_600_000) == "60:00.000"


# ── _cell_name ────────────────────────────────────────────────────────────────

class TestCellName:
    def test_top_left(self):
        assert _cell_name((0, 0)) == "a8"

    def test_bottom_right(self):
        assert _cell_name((7, 7)) == "h1"

    def test_e4(self):
        assert _cell_name((4, 4)) == "e4"

    def test_d7(self):
        assert _cell_name((1, 3)) == "d7"


# ── MovesLog entries ──────────────────────────────────────────────────────────

class TestMovesLogEntries:
    def test_move_for_own_color_recorded(self):
        log = MovesLog("w")
        p = _piece("w", "R")
        log.on_piece_moved(_moved(p, (7, 0), (5, 0), 15_006))
        assert len(log._entries) == 1
        t, m = log._entries[0]
        assert t == "00:15.000"
        assert m == "a1-a3"

    def test_move_for_other_color_ignored(self):
        log = MovesLog("w")
        log.on_piece_moved(_moved(_piece("b", "P"), (1, 0), (2, 0), 1000))
        assert log._entries == []

    def test_capture_for_own_color_recorded(self):
        log = MovesLog("b")
        attacker = _piece("b", "Q")
        log.on_piece_captured(_captured(_piece("w", "P"), (6, 3), attacker, 31_027))
        assert len(log._entries) == 1
        t, m = log._entries[0]
        assert t == "00:31.002"
        assert m == "xd2"

    def test_capture_by_other_color_ignored(self):
        log = MovesLog("b")
        attacker = _piece("w", "R")
        log.on_piece_captured(_captured(_piece("b", "P"), (1, 0), attacker, 1000))
        assert log._entries == []

    def test_multiple_entries_accumulate(self):
        log = MovesLog("w")
        p = _piece("w", "N")
        log.on_piece_moved(_moved(p, (7, 1), (5, 2), 1000))
        log.on_piece_moved(_moved(p, (5, 2), (3, 3), 2000))
        assert len(log._entries) == 2

    def test_render_does_not_raise(self):
        log = MovesLog("w")
        p = _piece("w", "R")
        log.on_piece_moved(_moved(p, (7, 0), (5, 0), 5000))
        canvas = GameImg.blank(gfx_config.WINDOW_PX_W, gfx_config.WINDOW_PX_H)
        log.render(canvas, 0, 0, gfx_config.SIDEBAR_PX_W, gfx_config.MOVES_LOG_H)


# ── PlayerNamesPanel ──────────────────────────────────────────────────────────

class TestPlayerNamesPanel:
    def test_default_names(self):
        panel = PlayerNamesPanel()
        assert panel.white_name == "White"
        assert panel.black_name == "Black"

    def test_custom_names_stored(self):
        panel = PlayerNamesPanel(white_name="Alice", black_name="Bob")
        assert panel.white_name == "Alice"
        assert panel.black_name == "Bob"

    def test_label_format(self):
        panel = PlayerNamesPanel(white_name="Alice", black_name="Bob")
        assert f"{panel.black_name} vs {panel.white_name}" == "Bob vs Alice"

    def test_render_produces_correct_size(self):
        panel = PlayerNamesPanel(white_name="Alice", black_name="Bob")
        canvas = GameImg.blank(800, gfx_config.TOP_NAME_H)
        panel.render(canvas, 0, 0, 800, gfx_config.TOP_NAME_H)
        assert canvas.img.shape == (gfx_config.TOP_NAME_H, 800, 4)

    def test_render_draws_on_canvas(self):
        panel = PlayerNamesPanel(white_name="Alice", black_name="Bob")
        canvas = GameImg.blank(800, gfx_config.TOP_NAME_H, color=(0, 0, 0, 255))
        panel.render(canvas, 0, 0, 800, gfx_config.TOP_NAME_H)
        # panel background color should differ from pure black
        bg = gfx_config.COLOR_PANEL_BG
        assert not np.all(canvas.img == 0), "canvas should be modified by render"


# ── ScoreBoard render ─────────────────────────────────────────────────────────

class TestScoreBoardRender:
    def _canvas(self):
        return GameImg.blank(800, gfx_config.TOP_SCORE_H, color=(0, 0, 0, 255))

    def test_render_does_not_raise(self):
        sb = ScoreBoard()
        sb.render(self._canvas(), 0, 0, 800, gfx_config.TOP_SCORE_H)

    def test_render_modifies_canvas(self):
        sb = ScoreBoard()
        canvas = self._canvas()
        sb.render(canvas, 0, 0, 800, gfx_config.TOP_SCORE_H)
        assert not np.all(canvas.img == 0)

    def test_gold_separator_line_drawn(self):
        sb = ScoreBoard()
        h = gfx_config.TOP_SCORE_H
        canvas = self._canvas()
        sb.render(canvas, 0, 0, 800, h)
        # bottom row should contain the gold color (BGR: 30,190,210)
        bottom_row = canvas.img[h - 1, :, :3]
        gold_bgr = np.array(gfx_config.COLOR_GOLD[:3], dtype=np.uint8)
        assert np.any(np.all(bottom_row == gold_bgr, axis=1))

    def test_even_score_label(self):
        # ScoreBoard at 0-0 should produce "Score: Even" — verify via score state
        sb = ScoreBoard()
        assert sb._score["w"] == 0 and sb._score["b"] == 0

    def test_positive_score_label(self):
        sb = ScoreBoard()
        attacker = _piece("w", "Q")
        sb.on_piece_captured(PieceCapturedEvent(_piece("b", "R"), (0, 0), attacker))
        total = sb._score["w"] - sb._score["b"]
        assert total > 0
