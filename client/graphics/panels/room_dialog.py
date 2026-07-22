import cv2
import numpy as np
from enum import Enum, auto
from graphics import gfx_config


class RoomDialogAction(Enum):
    CREATE = auto()
    JOIN   = auto()
    CANCEL = auto()


class RoomDialog:
    """
    Modal overlay with a room-code text field and three buttons.

    Call on_key(cv2_key) each frame to handle typing.
    Call on_click(x, y) on left-click; returns RoomDialogAction or None.
    Read .room_id for the current text field value.
    """

    _BOX_W, _BOX_H = 480, 220
    _BTN_W, _BTN_H = 120, 44
    _BTN_GAP       = 16

    def __init__(self):
        self.room_id: str = ""
        self._create_rect = None
        self._join_rect   = None
        self._cancel_rect = None

    # ── input ─────────────────────────────────────────────────────────────────

    def on_key(self, key: int) -> None:
        """Feed a cv2 waitKey result. Handles printable ASCII and backspace."""
        if key == 8 or key == 127:          # backspace / delete
            self.room_id = self.room_id[:-1]
        elif 32 <= key < 127:               # printable ASCII
            if len(self.room_id) < 8:
                self.room_id += chr(key).upper()

    def on_click(self, x: int, y: int) -> RoomDialogAction | None:
        if self._create_rect and self._hit(self._create_rect, x, y):
            return RoomDialogAction.CREATE
        if self._join_rect and self._hit(self._join_rect, x, y):
            return RoomDialogAction.JOIN
        if self._cancel_rect and self._hit(self._cancel_rect, x, y):
            return RoomDialogAction.CANCEL
        return None

    # ── rendering ─────────────────────────────────────────────────────────────

    def render(self, canvas) -> None:
        img = canvas.img
        H, W = img.shape[:2]

        # dim background
        img[:] = (img.astype(np.float32) * 0.45).astype(np.uint8)

        gold = gfx_config.COLOR_GOLD[:3]
        bx = (W - self._BOX_W) // 2
        by = (H - self._BOX_H) // 2

        # panel background + border
        cv2.rectangle(img, (bx, by), (bx + self._BOX_W, by + self._BOX_H), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + self._BOX_W, by + self._BOX_H), (*gold, 255), 2)

        # title
        title = "ROOM"
        (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.putText(img, title, ((W - tw) // 2, by + 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (*gold, 255), 2, cv2.LINE_AA)

        # text field label
        cv2.putText(img, "Room code:", (bx + 20, by + 88),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200, 255), 1, cv2.LINE_AA)

        # text field box
        fx, fy, fw, fh = bx + 20, by + 98, self._BOX_W - 40, 36
        cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), (40, 40, 40, 255), -1)
        cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), (*gold, 255), 1)
        display = self.room_id + "|"
        cv2.putText(img, display, (fx + 8, fy + fh - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220, 255), 1, cv2.LINE_AA)

        # buttons: Create | Join | Cancel
        total_w = 3 * self._BTN_W + 2 * self._BTN_GAP
        btn_y   = by + self._BOX_H - self._BTN_H - 20
        btn_x0  = bx + (self._BOX_W - total_w) // 2

        self._create_rect = self._draw_btn(img, btn_x0, btn_y, "CREATE", filled=True, gold=gold)
        self._join_rect   = self._draw_btn(img, btn_x0 + self._BTN_W + self._BTN_GAP,
                                           btn_y, "JOIN", filled=True, gold=gold)
        self._cancel_rect = self._draw_btn(img, btn_x0 + 2 * (self._BTN_W + self._BTN_GAP),
                                           btn_y, "CANCEL", filled=False, gold=gold)

    def _draw_btn(self, img, x, y, label, filled, gold) -> tuple:
        rect = (x, y, x + self._BTN_W, y + self._BTN_H)
        bg   = (*gold, 255) if filled else (20, 20, 20, 255)
        fg   = (20, 20, 20, 255) if filled else (*gold, 255)
        cv2.rectangle(img, (x, y), (x + self._BTN_W, y + self._BTN_H), bg, -1)
        cv2.rectangle(img, (x, y), (x + self._BTN_W, y + self._BTN_H), (*gold, 255), 2)
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(img, label,
                    (x + (self._BTN_W - lw) // 2, y + (self._BTN_H + lh) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, fg, 1, cv2.LINE_AA)
        return rect

    @staticmethod
    def _hit(rect, x, y) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2
