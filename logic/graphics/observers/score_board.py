import cv2
from graphics.observers.game_events import GameObserver


class ScoreBoard(GameObserver):
    def __init__(self):
        self._score = {"w": 0, "b": 0}

    def on_piece_captured(self, event):
        if event.by_color and event.by_color in self._score:
            self._score[event.by_color] += event.piece_value

    def render_for(self, canvas, color, x, y, width, height):
        """Render score for a single player (color='w' or 'b') at the given position."""
        score = self._score[color]
        label = f"Score: {score}"
        text_w = len(label) * 10
        tx = x + (width - text_w) // 2
        ty = y + height - 8
        cv2.putText(canvas.img, label, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20, 255), 2, cv2.LINE_AA)
