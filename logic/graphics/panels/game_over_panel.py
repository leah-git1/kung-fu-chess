import cv2
import numpy as np
from graphics import gfx_config


class GameOverPanel:
    """Semi-transparent overlay that announces the winner with New Game / Close buttons."""

    def __init__(self):
        self._new_game_rect = None  # (x1, y1, x2, y2)
        self._close_rect = None

    def render(self, canvas, winner_name: str) -> None:
        img = canvas.img
        H, W = img.shape[:2]

        img[:] = (img.astype(np.float32) * 0.35).astype(np.uint8)

        box_w, box_h = min(600, W - 40), 220
        bx = (W - box_w) // 2
        by = (H - box_h) // 2
        gold = gfx_config.COLOR_GOLD[:3]

        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 3)
        cv2.rectangle(img, (bx + 6, by + 6), (bx + box_w - 6, by + box_h - 6), (*gold, 255), 1)

        header = "GAME OVER"
        (hw, _), _ = cv2.getTextSize(header, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)
        cv2.putText(img, header, ((W - hw) // 2, by + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (*gold, 255), 2, cv2.LINE_AA)

        winner_text = f"{winner_name} wins!"
        (ww, _), _ = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
        cv2.putText(img, winner_text, ((W - ww) // 2, by + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (220, 220, 220, 255), 2, cv2.LINE_AA)

        # buttons
        btn_w, btn_h = 180, 48
        gap = 20
        total_btns_w = btn_w * 2 + gap
        btn_y = by + box_h - btn_h - 20

        # NEW GAME button (gold fill)
        ng_x = (W - total_btns_w) // 2
        self._new_game_rect = (ng_x, btn_y, ng_x + btn_w, btn_y + btn_h)
        cv2.rectangle(img, (ng_x, btn_y), (ng_x + btn_w, btn_y + btn_h), (*gold, 255), -1)
        cv2.rectangle(img, (ng_x, btn_y), (ng_x + btn_w, btn_y + btn_h), (20, 20, 20, 255), 2)
        label = "NEW GAME"
        (lw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(img, label, (ng_x + (btn_w - lw) // 2, btn_y + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20, 255), 2, cv2.LINE_AA)

        # CLOSE button (dark fill, gold border)
        cl_x = ng_x + btn_w + gap
        self._close_rect = (cl_x, btn_y, cl_x + btn_w, btn_y + btn_h)
        cv2.rectangle(img, (cl_x, btn_y), (cl_x + btn_w, btn_y + btn_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (cl_x, btn_y), (cl_x + btn_w, btn_y + btn_h), (*gold, 255), 2)
        label2 = "CLOSE"
        (lw2, _), _ = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(img, label2, (cl_x + (btn_w - lw2) // 2, btn_y + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (*gold, 255), 2, cv2.LINE_AA)

    def on_click(self, x, y) -> str | None:
        """Returns 'new_game', 'close', or None."""
        if self._new_game_rect and self._hit(self._new_game_rect, x, y):
            return "new_game"
        if self._close_rect and self._hit(self._close_rect, x, y):
            return "close"
        return None

    @staticmethod
    def _hit(rect, x, y) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2
