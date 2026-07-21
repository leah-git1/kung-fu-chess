import cv2
import numpy as np
from graphics import gfx_config
from events.game_events import GameOverEvent
from graphics.panels.panel_action import PanelAction


class GameOverPanel:
    """Semi-transparent overlay that announces the winner with New Game / Close buttons."""

    def __init__(self, bus, white_name: str, black_name: str):
        self._new_game_rect = None
        self._close_rect    = None
        self._winner_name   = None
        self._reason        = ""
        self._names = {"w": white_name, "b": black_name}
        bus.subscribe(GameOverEvent, self._on_game_over)

    def _on_game_over(self, event):
        self._winner_name = self._names.get(event.winner_color, event.winner_color)

    def set_reason(self, reason: str) -> None:
        self._reason = reason.replace("_", " ")

    @property
    def active(self):
        return self._winner_name is not None

    def render(self, canvas) -> None:
        img = canvas.img
        H, W = img.shape[:2]

        img[:] = (img.astype(np.float32) * gfx_config.GAME_OVER_DIM).astype(np.uint8)

        box_w = min(gfx_config.PANEL_BOX_MAX_W, W - gfx_config.PANEL_MARGIN)
        box_h = gfx_config.GAME_OVER_BOX_H_REASON if self._reason else gfx_config.GAME_OVER_BOX_H
        bx = (W - box_w) // 2
        by = (H - box_h) // 2
        gold = gfx_config.COLOR_GOLD[:3]
        p = gfx_config.PANEL_PADDING

        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 3)
        cv2.rectangle(img, (bx + p - 2, by + p - 2), (bx + box_w - p + 2, by + box_h - p + 2), (*gold, 255), 1)

        header = "GAME OVER"
        (hw, _), _ = cv2.getTextSize(header, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)
        cv2.putText(img, header, ((W - hw) // 2, by + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (*gold, 255), 2, cv2.LINE_AA)

        winner_text = f"{self._winner_name} wins!"
        (ww, _), _ = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
        cv2.putText(img, winner_text, ((W - ww) // 2, by + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (220, 220, 220, 255), 2, cv2.LINE_AA)

        if self._reason:
            (rw, _), _ = cv2.getTextSize(self._reason, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 1)
            cv2.putText(img, self._reason, ((W - rw) // 2, by + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 180, 255), 1, cv2.LINE_AA)

        btn_w   = gfx_config.GAME_OVER_BTN_W
        btn_h   = gfx_config.GAME_OVER_BTN_H
        gap     = gfx_config.GAME_OVER_BTN_GAP
        label_y = gfx_config.GAME_OVER_BTN_LABEL_Y
        btn_y   = by + box_h - btn_h - gap

        ng_x = (W - btn_w * 2 - gap) // 2
        self._new_game_rect = (ng_x, btn_y, ng_x + btn_w, btn_y + btn_h)
        cv2.rectangle(img, (ng_x, btn_y), (ng_x + btn_w, btn_y + btn_h), (*gold, 255), -1)
        cv2.rectangle(img, (ng_x, btn_y), (ng_x + btn_w, btn_y + btn_h), (20, 20, 20, 255), 2)
        label = "NEW GAME"
        (lw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(img, label, (ng_x + (btn_w - lw) // 2, btn_y + label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20, 255), 2, cv2.LINE_AA)

        cl_x = ng_x + btn_w + gap
        self._close_rect = (cl_x, btn_y, cl_x + btn_w, btn_y + btn_h)
        cv2.rectangle(img, (cl_x, btn_y), (cl_x + btn_w, btn_y + btn_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (cl_x, btn_y), (cl_x + btn_w, btn_y + btn_h), (*gold, 255), 2)
        label2 = "CLOSE"
        (lw2, _), _ = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(img, label2, (cl_x + (btn_w - lw2) // 2, btn_y + label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (*gold, 255), 2, cv2.LINE_AA)

    def on_click(self, x, y) -> PanelAction | None:
        if self._new_game_rect and self._hit(self._new_game_rect, x, y):
            return PanelAction.NEW_GAME
        if self._close_rect and self._hit(self._close_rect, x, y):
            return PanelAction.CLOSE
        return None

    @staticmethod
    def _hit(rect, x, y) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2
