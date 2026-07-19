import cv2
import numpy as np
from graphics import gfx_config
from graphics.observers.game_events import GameStartedEvent
from graphics.panels.panel_action import PanelAction


class StartGamePanel:
    """Overlay with a START GAME button. Hidden once GameStartedEvent is received."""

    def __init__(self, bus):
        self._btn_rect = None
        self._active = True
        bus.subscribe(GameStartedEvent, lambda _: setattr(self, '_active', False))

    @property
    def active(self):
        return self._active
        
    def render(self, canvas) -> None:
        img = canvas.img
        H, W = img.shape[:2]

        img[:] = (img.astype(np.float32) * 0.45).astype(np.uint8)

        gold = gfx_config.COLOR_GOLD[:3]

        box_w, box_h = min(560, W - 40), 120
        bx = (W - box_w) // 2
        by = (H - box_h) // 2 - 60

        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 3)
        cv2.rectangle(img, (bx + 6, by + 6), (bx + box_w - 6, by + box_h - 6), (*gold, 255), 1)

        title = "KUNG-FU CHESS"
        (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.putText(img, title, ((W - tw) // 2, by + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (*gold, 255), 2, cv2.LINE_AA)

        btn_w, btn_h = 260, 60
        btn_x = (W - btn_w) // 2
        btn_y = by + box_h + 30
        self._btn_rect = (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h)

        cv2.rectangle(img, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (*gold, 255), -1)
        cv2.rectangle(img, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (20, 20, 20, 255), 2)

        label = "START GAME"
        (lw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        cv2.putText(img, label, ((W - lw) // 2, btn_y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20, 255), 2, cv2.LINE_AA)

    def on_click(self, screen_x, screen_y) -> PanelAction | None:
        if self._btn_rect is None:
            return None
        x1, y1, x2, y2 = self._btn_rect
        if x1 <= screen_x <= x2 and y1 <= screen_y <= y2:
            return PanelAction.START
        return None
