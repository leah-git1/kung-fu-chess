import cv2
from graphics import gfx_config


class HomeRenderer:
    # Play button rect (centered, computed on first render)
    BTN_W, BTN_H = 200, 60

    def render(self, canvas, player_name: str, rating: int,
               status_msg: str = "") -> tuple[int, int, int, int]:
        """Draw home screen. Returns (bx, by, bw, bh) of the Play button."""
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
        bx = (W - self.BTN_W) // 2
        by = H // 2 - self.BTN_H // 2
        cv2.rectangle(img, (bx, by), (bx + self.BTN_W, by + self.BTN_H), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + self.BTN_W, by + self.BTN_H), (*gold, 255), 2)
        label = "PLAY"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.putText(img, label,
                    (bx + (self.BTN_W - lw) // 2, by + (self.BTN_H + lh) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (*gold, 255), 2, cv2.LINE_AA)

        # status message (e.g. timeout notice)
        if status_msg:
            (sw, _), _ = cv2.getTextSize(status_msg, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 1)
            cv2.putText(img, status_msg, ((W - sw) // 2, by + self.BTN_H + 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (80, 80, 220, 255), 1, cv2.LINE_AA)

        return bx, by, self.BTN_W, self.BTN_H
