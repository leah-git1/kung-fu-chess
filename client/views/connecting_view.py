import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from graphics.connecting_renderer import ConnectingRenderer
from shared.messages import RoomStateMsg


class ConnectingView(BaseView):
    """
    Shown while the WebSocket connection is being established.

    Transitions:
      RoomStateMsg(started=True)  → GOTO_GAME   (both players connected)
      RoomStateMsg(started=False) → stays here  (waiting for second player)
    """

    def on_enter(self, context: dict) -> None:
        self._status = context.get("status", "Connecting to server…")
        self._renderer = ConnectingRenderer()

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, RoomStateMsg):
            if msg.started:
                return ViewAction.GOTO_GAME
            self._status = "Waiting for opponent…"
        return None

    def render(self, canvas) -> None:
        self._renderer.render(canvas, self._status)
