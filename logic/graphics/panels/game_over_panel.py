import cv2
import numpy as np
from graphics.img_provider import GameImg
from graphics import gfx_config


class GameOverPanel:
    """Semi-transparent full-window overlay that announces the winner."""

    def render(self, canvas, winner_name: str) -> None:
        img = canvas.img
        H, W = img.shape[:2]

        # dim the whole window
        overlay = img.astype(np.float32)
        overlay = overlay * 0.35
        img[:] = overlay.astype(np.uint8)

        # central box
        box_w, box_h = min(600, W - 40), 160
        bx = (W - box_w) // 2
        by = (H - box_h) // 2

        # filled dark box
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        # gold border (2px)
        gold = gfx_config.COLOR_GOLD[:3]
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 3)
        # inner border (1px, slightly inset)
        cv2.rectangle(img, (bx + 6, by + 6), (bx + box_w - 6, by + box_h - 6), (*gold, 255), 1)

        # "GAME OVER" header
        header = "GAME OVER"
        (hw, _), _ = cv2.getTextSize(header, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)
        cv2.putText(img, header,
                    ((W - hw) // 2, by + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1,
                    (*gold, 255), 2, cv2.LINE_AA)

        # winner line
        winner_text = f"{winner_name} wins!"
        (ww, _), _ = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)
        cv2.putText(img, winner_text,
                    ((W - ww) // 2, by + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                    (220, 220, 220, 255), 3, cv2.LINE_AA)
