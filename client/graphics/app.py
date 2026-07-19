import os, sys, time

_CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGIC_DIR  = os.path.join(os.path.dirname(_CLIENT_DIR), "logic")
sys.path.insert(0, _CLIENT_DIR)
sys.path.insert(0, _LOGIC_DIR)

from board.board_parser import BoardParser
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from game.game import Game

from graphics import gfx_config
from graphics.img_provider import GameImg, WindowManager
from graphics.input_adapter import InputAdapter
from graphics.game_renderer import GameRenderer
from events.game_event_source import GameEventSource
from events.game_events import GameStartedEvent
from graphics.panels.start_game_panel import StartGamePanel
from graphics.panels.panel_action import PanelAction

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
        self._renderer = GameRenderer(white_name, black_name)

        mapper = BoardMapper(gfx_config.CELL_PX)
        self.input_controller = InputController(mapper)
        self.input_adapter = InputAdapter(self.input_controller, self._renderer.layout, None)

        self._window = WindowManager(gfx_config.WINDOW_TITLE,
                                     self._renderer.layout.window_px_w,
                                     self._renderer.layout.window_px_h)
        self._last_tick_ms = None
        self._init_game_state()

    def _init_game_state(self):
        board = BoardParser().parse(_STARTING_POSITION.strip().splitlines())
        self.game = Game(board)
        self._renderer = GameRenderer(self._white_name, self._black_name)
        self.start_game_panel = StartGamePanel(self._renderer.bus)
        self.event_source = GameEventSource(self._renderer.bus)
        self.input_controller.reset()
        self.input_adapter = InputAdapter(self.input_controller, self._renderer.layout, self.game)

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
                self._renderer.bus.publish(GameStartedEvent())
            return
        if self._renderer.game_over_panel.active:
            action = self._renderer.game_over_panel.on_click(x, y)
            if action == PanelAction.NEW_GAME:
                self._init_game_state()
            elif action == PanelAction.CLOSE:
                return "close"
            return
        self.input_adapter.on_mouse_event(kind, x, y)

    def _render_frame(self, now_ms):
        layout = self._renderer.layout
        canvas = GameImg.blank(layout.window_px_w, layout.window_px_h, (15, 15, 15, 255))
        self._renderer.render_frame(canvas, self.game, now_ms,
                                    selected_cell=self.input_controller.selected,
                                    overlay=self.start_game_panel)
        canvas.show(window_name=gfx_config.WINDOW_TITLE)

    @staticmethod
    def _now_ms():
        return int(time.monotonic() * 1000)


if __name__ == "__main__":
    GraphicsApp().run()
