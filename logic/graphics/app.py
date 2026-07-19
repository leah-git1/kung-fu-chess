import os, sys, time
import cv2
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
from graphics.observers.event_bus import EventBus
from graphics.observers.game_event_source import GameEventSource
from graphics.observers.game_events import GameStartedEvent
from graphics.observers.moves_log import MovesLog
from graphics.observers.score_board import ScoreBoard
from graphics.panels.player_names_panel import PlayerNamesPanel
from graphics.panels.game_over_panel import GameOverPanel
from graphics.panels.start_game_panel import StartGamePanel
from graphics.panels.panel_action import PanelAction
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


class GraphicsApp:
    def __init__(self, white_name="White", black_name="Black"):
        self._white_name = white_name
        self._black_name = black_name
        self.layout = Layout()
        self.board_renderer = BoardRenderer(self.layout)
        self.player_names_panel = PlayerNamesPanel(white_name, black_name)

        mapper = BoardMapper(gfx_config.CELL_PX)
        self.input_controller = InputController(mapper)
        self.input_adapter = InputAdapter(self.input_controller, self.layout, None)

        self._window = WindowManager(gfx_config.WINDOW_TITLE, self.layout.window_px_w, self.layout.window_px_h)
        self._last_tick_ms = None
        self._init_game_state()

    def _init_game_state(self):
        board = BoardParser().parse(_STARTING_POSITION.strip().splitlines())
        self.game = Game(board)
        self.piece_renderer = PieceRenderer(self.layout)

        self.bus = EventBus()
        self.moves_log_black = MovesLog("b", self.bus)
        self.moves_log_white = MovesLog("w", self.bus)
        self.score_board = ScoreBoard(self.bus)
        self.start_game_panel = StartGamePanel(self.bus)
        self.game_over_panel = GameOverPanel(self.bus, self._white_name, self._black_name)
        self.event_source = GameEventSource(self.bus)

        self.input_controller.reset()
        self.input_adapter._game = self.game

    def run(self):
        self._last_tick_ms = self._now_ms()
        while self._window.is_open():
            now = self._now_ms()
            elapsed = now - self._last_tick_ms
            self._last_tick_ms = now

            for event in self._window.poll_events():
                if self._handle_input_event(event) == "close":
                    self._window.close()
                    return

            if not self.start_game_panel.active:
                self.game.advance_time(elapsed)
                self.event_source.poll(self.game)
            self._render_frame(self.game.current_time)

            remaining = gfx_config.FRAME_TIME_MS - elapsed
            if remaining > 0:
                time.sleep(remaining / 1000)

    def _handle_input_event(self, event):
        kind = event["type"]
        if kind == "resize":
            self.input_adapter.on_window_resized(event["width"], event["height"])
        elif kind in ("left_click", "right_click"):
            return self._handle_click(event["x"], event["y"], kind)

    def _handle_click(self, x, y, kind):
        if self.start_game_panel.active:
            if self.start_game_panel.on_click(x, y) == PanelAction.START:
                self.bus.publish(GameStartedEvent())
            return
        if self.game_over_panel.active:
            action = self.game_over_panel.on_click(x, y)
            if action == PanelAction.NEW_GAME:
                self._init_game_state()
            elif action == PanelAction.CLOSE:
                return "close"
            return
        self.input_adapter.on_mouse_event(kind, x, y)

    def _render_frame(self, now_ms):
        W, H = self.layout.window_px_w, self.layout.window_px_h
        canvas = GameImg.blank(W, H, (15, 15, 15, 255))

        self.player_names_panel.render(canvas, 0, 0, W, gfx_config.TOP_BAR_H)
        self.board_renderer.render(canvas, selected_cell=self.input_controller.selected)
        self.piece_renderer.render(canvas, self.game, now_ms)
        self._render_sidebar(canvas, "b", self.layout.left_sidebar_x, self.moves_log_black)
        self._render_sidebar(canvas, "w", self.layout.right_sidebar_x, self.moves_log_white)

        if self.start_game_panel.active:
            self.start_game_panel.render(canvas)
        elif self.game_over_panel.active:
            self.game_over_panel.render(canvas)

        canvas.show(window_name=gfx_config.WINDOW_TITLE)

    def _render_sidebar(self, canvas, color, x, log):
        sw = gfx_config.SIDEBAR_PX_W
        top_h = gfx_config.TOP_BAR_H
        log_h = gfx_config.MOVES_LOG_H
        name = self.player_names_panel.black_name if color == "b" else self.player_names_panel.white_name

        box_w, box_h = 130, 34
        bx = x + (sw - box_w) // 2
        by = top_h - box_h - 6
        if by >= 0:
            cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
            cv2.rectangle(canvas.img, (bx, by), (bx + box_w, by + box_h), (30, 190, 210, 255), 2)
            tx = bx + (box_w - len(name) * 11) // 2
            cv2.putText(canvas.img, name, (tx, by + box_h - 9),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220, 255), 1, cv2.LINE_AA)

        self.score_board.render_for(canvas, color, x, top_h, sw, 30)

        log.render(canvas, x, top_h + 30, sw, log_h - 30)

    @staticmethod
    def _now_ms():
        return int(time.monotonic() * 1000)


if __name__ == "__main__":
    GraphicsApp().run()
