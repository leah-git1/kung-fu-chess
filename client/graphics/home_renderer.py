import cv2
from graphics import gfx_config


class HomeRenderer:
    BTN_W, BTN_H = 200, 60
    BTN_GAP      = 16

    def render(self, canvas, player_name: str, rating: int,
               status_msg: str = "") -> tuple:
        """Draw home screen. Returns ((play_bx, play_by, bw, bh), (room_bx, room_by, bw, bh))."""
        img = canvas.img
        H, W = img.shape[:2]
        gold = gfx_config.COLOR_GOLD[:3]

        # title
        title = "Kung-Fu Chess"
        (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)
        cv2.putText(img, title, ((W - tw) // 2, H // 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (*gold, 255), 3, cv2.LINE_AA)

        # player info
        info = f"{player_name}  |  ELO: {rating}"
        (iw, _), _ = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        cv2.putText(img, info, ((W - iw) // 2, H // 4 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 200, 200, 255), 2, cv2.LINE_AA)

        # Play button
        total_w = self.BTN_W * 2 + self.BTN_GAP
        bx = (W - total_w) // 2
        by = H // 2 - self.BTN_H // 2
        self._draw_btn(img, bx, by, "PLAY", filled=True, gold=gold)
        play_rect = (bx, by, self.BTN_W, self.BTN_H)

        # Room button
        rx = bx + self.BTN_W + self.BTN_GAP
        self._draw_btn(img, rx, by, "ROOM", filled=False, gold=gold)
        room_rect = (rx, by, self.BTN_W, self.BTN_H)

        # status message
        if status_msg:
            (sw, _), _ = cv2.getTextSize(status_msg, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 1)
            cv2.putText(img, status_msg, ((W - sw) // 2, by + self.BTN_H + 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (80, 80, 220, 255), 1, cv2.LINE_AA)

        return play_rect, room_rect

    def _draw_btn(self, img, x, y, label, filled, gold) -> None:
        bg = (*gold, 255) if filled else (20, 20, 20, 255)
        fg = (20, 20, 20, 255) if filled else (*gold, 255)
        cv2.rectangle(img, (x, y), (x + self.BTN_W, y + self.BTN_H), bg, -1)
        cv2.rectangle(img, (x, y), (x + self.BTN_W, y + self.BTN_H), (*gold, 255), 2)
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.putText(img, label,
                    (x + (self.BTN_W - lw) // 2, y + (self.BTN_H + lh) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, fg, 2, cv2.LINE_AA)
