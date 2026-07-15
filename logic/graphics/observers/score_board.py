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
        import cv2
        panel = GameImg.blank(width, height, gfx_config.COLOR_PANEL_BG)
        total = self._score["w"] - self._score["b"]
        label = f"Score: {total:+d}" if total != 0 else "Score: Even"
        text_w = len(label) * 11
        panel.put_text(label, x=(width - text_w) // 2, y=height - 8,
                       font_size=0.75, color=gfx_config.COLOR_PANEL_TEXT[:3], thickness=1)
        # thin separator line at the bottom
        cv2.line(panel.img, (0, height - 1), (width, height - 1),
                 (*gfx_config.COLOR_GOLD[:3], 255), 1)
        panel.draw_on(canvas, x, y)
