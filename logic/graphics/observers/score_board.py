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
        panel = GameImg.blank(width, height, (18, 18, 18, 255))
        total = self._score["w"] - self._score["b"]
        label = f"Score: {total:+d}" if total != 0 else "Score: 0"
        text_w = len(label) * 9
        panel.put_text(label, x=(width - text_w) // 2, y=height - 10,
                       font_size=0.65, color=(235, 235, 235), thickness=2)
        panel.draw_on(canvas, x, y)
