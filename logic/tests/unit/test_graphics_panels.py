import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
from events.event_bus import EventBus
from graphics.observers.moves_log import MovesLog, _fmt_time, _cell_name
from graphics.observers.score_board import ScoreBoard
from events.game_events import PieceMovedEvent, PieceCapturedEvent
from graphics.panels.player_names_panel import PlayerNamesPanel
from graphics.img_provider import GameImg
import graphics.gfx_config as gfx_config


# ── _fmt_time ─────────────────────────────────────────────────────────────────

class TestFmtTime:
    def test_zero(self):
        assert _fmt_time(0) == "00:00.000"

    def test_seconds(self):
        assert _fmt_time(15_006) == "00:15.000"

    def test_minutes(self):
        assert _fmt_time(75_000) == "01:15.000"

    def test_fractional_part_is_centiseconds(self):
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
    def _log(self, color):
        return MovesLog(color, EventBus())

    def test_move_for_own_color_recorded(self):
        bus = EventBus()
        log = MovesLog("w", bus)
        bus.publish(PieceMovedEvent("w", (7, 0), (5, 0), 15_006, piece_name="R"))
        assert len(log._entries) == 1
        t, m = log._entries[0]
        assert t == "00:15.000"
        assert "a1" in m and "a3" in m

    def test_move_for_other_color_ignored(self):
        bus = EventBus()
        log = MovesLog("w", bus)
        bus.publish(PieceMovedEvent("b", (1, 0), (2, 0), 1000, piece_name="P"))
        assert log._entries == []

    def test_capture_for_own_color_recorded(self):
        bus = EventBus()
        log = MovesLog("b", bus)
        bus.publish(PieceCapturedEvent((6, 3), 31_027, by_color="b", captured_type="P"))
        assert len(log._entries) == 1
        t, m = log._entries[0]
        assert t == "00:31.002"
        assert "xP" in m and "d2" in m

    def test_capture_by_other_color_ignored(self):
        bus = EventBus()
        log = MovesLog("b", bus)
        bus.publish(PieceCapturedEvent((1, 0), 1000, by_color="w", captured_type="P"))
        assert log._entries == []

    def test_multiple_entries_accumulate(self):
        bus = EventBus()
        log = MovesLog("w", bus)
        bus.publish(PieceMovedEvent("w", (7, 1), (5, 2), 1000, piece_name="N"))
        bus.publish(PieceMovedEvent("w", (5, 2), (3, 3), 2000, piece_name="N"))
        assert len(log._entries) == 2

    def test_render_does_not_raise(self):
        bus = EventBus()
        log = MovesLog("w", bus)
        bus.publish(PieceMovedEvent("w", (7, 0), (5, 0), 5000, piece_name="R"))
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
        assert not np.all(canvas.img == 0), "canvas should be modified by render"


# ── ScoreBoard render ─────────────────────────────────────────────────────────

class TestScoreBoardRender:
    def _make(self):
        bus = EventBus()
        return ScoreBoard(bus), bus

    def _canvas(self):
        return GameImg.blank(800, 30, color=(0, 0, 0, 255))

    def test_render_does_not_raise(self):
        sb, _ = self._make()
        sb.render_for(self._canvas(), "w", 0, 0, 800, 30)

    def test_render_modifies_canvas(self):
        sb, _ = self._make()
        canvas = self._canvas()
        sb.render_for(canvas, "w", 0, 0, 800, 30)
        assert not np.all(canvas.img == 0)

    def test_even_score_label(self):
        sb, _ = self._make()
        assert sb._score["w"] == 0 and sb._score["b"] == 0

    def test_positive_score_label(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((0, 0), piece_value=5, by_color="w"))
        assert sb._score["w"] - sb._score["b"] > 0

    def test_capture_accumulates(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((0, 0), piece_value=1, by_color="w"))
        bus.publish(PieceCapturedEvent((1, 0), piece_value=5, by_color="w"))
        assert sb._score["w"] == 6
