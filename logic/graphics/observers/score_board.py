import cv2
from graphics.observers.game_events import GameObserver


class ScoreBoard(GameObserver):
    def __init__(self):
        self._score = {"w": 0, "b": 0}

    def on_piece_captured(self, event):
        if event.by_color and event.by_color in self._score:
            self._score[event.by_color] += event.piece_value

    def render_for(self, canvas, color, x, y, width, height):
        from graphics import gfx_config
        cv2.rectangle(canvas.img, (x, y), (x + width, y + height),
                      (*gfx_config.COLOR_PANEL_BG[:3], 255), -1)
        label = f"Score: {self._score[color]}"
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(canvas.img, label, (x + (width - tw) // 2, y + height - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220, 255), 1, cv2.LINE_AA)
