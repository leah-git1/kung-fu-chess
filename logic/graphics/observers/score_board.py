import config as logic_config
from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.observers.game_events import GameObserver

class ScoreBoard(GameObserver):
    def __init__(self):
        self._score = {"w": 0, "b": 0}

    def on_piece_captured(self, event):
        value = logic_config.PIECE_VALUES.get(event.captured_piece.piece_type.value, 0)
        if event.by_piece and event.by_piece.color in self._score:
            self._score[event.by_piece.color] += value

    def render(self, canvas, x, y, width, height):
        panel = GameImg.blank(width, height, gfx_config.COLOR_PANEL_BG)
        panel.put_text(f"White: {self._score['w']}", x=8, y=10, font_size=18, color=gfx_config.COLOR_PANEL_TEXT[:3])
        panel.put_text(f"Black: {self._score['b']}", x=8, y=40, font_size=18, color=gfx_config.COLOR_PANEL_TEXT[:3])
        panel.draw_on(canvas, x, y)