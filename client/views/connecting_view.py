import cv2
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from shared.messages import RoomStateMsg
from graphics import gfx_config


class ConnectingView(BaseView):
    """
    Shown while the WebSocket connection is being established.

    Transitions:
      RoomStateMsg(started=True)  → GOTO_GAME   (both players connected)
      RoomStateMsg(started=False) → stays here  (waiting for second player)
    """

    def on_enter(self, context: dict) -> None:
        self._status = context.get("status", "Connecting to server…")

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, RoomStateMsg):
            if msg.started:
                return ViewAction.GOTO_GAME
            self._status = "Waiting for opponent…"
        return None

    def render(self, canvas) -> None:
        img = canvas.img
        H, W = img.shape[:2]
        gold = gfx_config.COLOR_GOLD[:3]

        box_w, box_h = min(500, W - 40), 100
        bx = (W - box_w) // 2
        by = (H - box_h) // 2

        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (20, 20, 20, 255), -1)
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (*gold, 255), 2)

        (tw, th), _ = cv2.getTextSize(self._status, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.putText(img, self._status,
                    ((W - tw) // 2, by + box_h // 2 + th // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 220, 220, 255), 2, cv2.LINE_AA)
