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
from graphics.observers.moves_log import MovesLog
from graphics.observers.score_board import ScoreBoard
from graphics.panels.player_names_panel import PlayerNamesPanel
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
        board = BoardParser().parse(_STARTING_POSITION.strip().splitlines())
        self.game = Game(board)
        self.layout = Layout()
        self.board_renderer = BoardRenderer(self.layout)
        self.piece_renderer = PieceRenderer(self.layout)

        self.event_source = GameEventSource()
        self.moves_log = MovesLog()
        self.score_board = ScoreBoard()
        self.event_source.add_observer(self.moves_log)
        self.event_source.add_observer(self.score_board)
        self.player_names_panel = PlayerNamesPanel(white_name, black_name)

        mapper = BoardMapper(gfx_config.CELL_PX)
        self.input_controller = InputController(mapper)
        self.input_adapter = InputAdapter(self.input_controller, self.layout, self.game)

        self._window = WindowManager("Kung-Fu Chess", self.layout.window_px_w, self.layout.window_px_h)
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
            self._render_frame(now)

            remaining = gfx_config.FRAME_TIME_MS - elapsed
            if remaining > 0:
                time.sleep(remaining / 1000)

    def _handle_input_event(self, event):
        kind = event["type"]
        if kind == "resize":
            self.input_adapter.on_window_resized(event["width"], event["height"])
        elif kind in ("left_click", "right_click"):
            self.input_adapter.on_mouse_event(kind, event["x"], event["y"])

    def _render_frame(self, now_ms):
        canvas = GameImg.blank(self.layout.window_px_w, self.layout.window_px_h, (18, 18, 18, 255))
        self.board_renderer.render(canvas, selected_cell=self.input_controller.selected)
        self.piece_renderer.render(canvas, self.game, now_ms)

        sx = self.layout.sidebar_origin_x
        self.player_names_panel.render(canvas, sx, 0, gfx_config.SIDEBAR_PX_W, gfx_config.PLAYER_NAME_BAR_H)
        self.score_board.render(canvas, sx, gfx_config.PLAYER_NAME_BAR_H, gfx_config.SIDEBAR_PX_W, gfx_config.SCOREBOARD_H)
        self.moves_log.render(canvas, sx, gfx_config.PLAYER_NAME_BAR_H + gfx_config.SCOREBOARD_H,
                               gfx_config.SIDEBAR_PX_W, gfx_config.MOVES_LOG_H)
        canvas.show("Kung-Fu Chess")

    def _now_ms(self):
        return int(time.monotonic() * 1000)

if __name__ == "__main__":
    GraphicsApp().run()