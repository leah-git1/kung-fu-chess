import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board.board_parser import BoardParser
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from game.game import Game

from graphics import gfx_config
from graphics.board_renderer import BoardRenderer
from graphics.img_provider import GameImg, WindowManager
from graphics.input_adapter import InputAdapter
from graphics.layout import Layout
from graphics.observers.game_event_source import GameEventSource
from graphics.observers.game_events import GameObserver
from graphics.observers.moves_log import MovesLog
from graphics.observers.score_board import ScoreBoard
from graphics.panels.player_names_panel import PlayerNamesPanel
from graphics.panels.game_over_panel import GameOverPanel
from graphics.piece_renderer import PieceRenderer

_STARTING_POSITION = """
Board:
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
Commands:
"""


class GraphicsApp(GameObserver):
    def __init__(self, white_name="White", black_name="Black"):
        board = BoardParser().parse(_STARTING_POSITION.strip().splitlines())
        self.game = Game(board)
        self.layout = Layout()
        self.board_renderer = BoardRenderer(self.layout)
        self.piece_renderer = PieceRenderer(self.layout)

        self.event_source = GameEventSource()
        self.moves_log_black = MovesLog("b")
        self.moves_log_white = MovesLog("w")
        self.score_board = ScoreBoard()
        self.event_source.add_observer(self.moves_log_black)
        self.event_source.add_observer(self.moves_log_white)
        self.event_source.add_observer(self.score_board)
        self.event_source.add_observer(self)   # GraphicsApp itself listens for royal captures

        self.player_names_panel = PlayerNamesPanel(white_name, black_name)
        self.game_over_panel = GameOverPanel()
        self._winner_name = None

        mapper = BoardMapper(gfx_config.CELL_PX)
        self.input_controller = InputController(mapper)
        self.input_adapter = InputAdapter(self.input_controller, self.layout, self.game)

        self._window = WindowManager(gfx_config.WINDOW_TITLE, self.layout.window_px_w, self.layout.window_px_h)
        self._last_tick_ms = None

    def run(self):
        self._last_tick_ms = self._now_ms()
        while self._window.is_open():
            now = self._now_ms()
            elapsed = now - self._last_tick_ms
            self._last_tick_ms = now

            for event in self._window.poll_events():
                self._handle_input_event(event)

            self.game.advance_time(elapsed)
            self.event_source.poll(self.game)
            self._render_frame(self.game.current_time)

            remaining = gfx_config.FRAME_TIME_MS - elapsed
            if remaining > 0:
                time.sleep(remaining / 1000)

    def on_piece_captured(self, event):
        """Detect royal capture to determine the winner."""
        p = event.captured_piece
        if p and p.piece_type and p.piece_type.value in ("K",):
            if p.color == "w":
                self._winner_name = self.player_names_panel.black_name
            else:
                self._winner_name = self.player_names_panel.white_name

    def on_piece_moved(self, event):
        pass

    def _handle_input_event(self, event):
        kind = event["type"]
        if kind == "resize":
            self.input_adapter.on_window_resized(event["width"], event["height"])
        elif kind in ("left_click", "right_click"):
            self.input_adapter.on_mouse_event(kind, event["x"], event["y"])

    def _render_frame(self, now_ms):
        W = self.layout.window_px_w
        H = self.layout.window_px_h
        sw = gfx_config.SIDEBAR_PX_W
        top_h = gfx_config.TOP_BAR_H
        log_h = gfx_config.MOVES_LOG_H

        canvas = GameImg.blank(W, H, (15, 15, 15, 255))

        # top bar: "Black vs White" title, then score below it
        name_h  = gfx_config.TOP_NAME_H
        score_h = gfx_config.TOP_SCORE_H
        self.player_names_panel.render(canvas, 0, 0, W, name_h)
        self.score_board.render(canvas, 0, name_h, W, score_h)

        # board
        self.board_renderer.render(canvas, selected_cell=self.input_controller.selected)
        self.piece_renderer.render(canvas, self.game, now_ms)

        # black panel (left) — header label + moves log
        self._render_side_label(canvas, self.player_names_panel.black_name, 0, top_h, sw)
        self.moves_log_black.render(canvas, 0, top_h, sw, log_h)

        # white panel (right) — header label + moves log
        rx = self.layout.right_sidebar_x
        self._render_side_label(canvas, self.player_names_panel.white_name, rx, top_h, sw)
        self.moves_log_white.render(canvas, rx, top_h, sw, log_h)

        canvas.show(window_name=gfx_config.WINDOW_TITLE)

        if self.game.game_over and self._winner_name:
            self.game_over_panel.render(canvas, self._winner_name)
            canvas.show(window_name=gfx_config.WINDOW_TITLE)

    def _render_side_label(self, canvas, label, x, y, width):
        """Draw a gold-bordered dark label ('Black' / 'White') above the moves table."""
        import cv2
        box_w, box_h = 130, 34
        bx = x + (width - box_w) // 2
        by = y - box_h - 6
        if by < 0:
            return
        cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (30, 190, 210, 255), 2)
        text_x = bx + (box_w - len(label) * 11) // 2
        cv2.putText(canvas.img, label, (text_x, by + box_h - 9),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220, 255), 1, cv2.LINE_AA)

    def _now_ms(self):
        return int(time.monotonic() * 1000)


if __name__ == "__main__":
    GraphicsApp().run()
