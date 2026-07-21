import cv2
from graphics import gfx_config


class ConnectingRenderer:
    """Draws the status box shown while waiting for a connection or opponent."""

    def render(self, canvas, status: str) -> None:
        img = canvas.img
        H, W = img.shape[:2]
        gold = gfx_config.COLOR_GOLD[:3]

        box_w = min(gfx_config.CONNECTING_BOX_W, W - gfx_config.PANEL_MARGIN)
        box_h = gfx_config.CONNECTING_BOX_H
        bx = (W - box_w) // 2
        by = (H - box_h) // 2

        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 2)

        (tw, th), _ = cv2.getTextSize(status, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.putText(img, status,
                    ((W - tw) // 2, by + box_h // 2 + th // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 220, 220, 255), 2, cv2.LINE_AA)
