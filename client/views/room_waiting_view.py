from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from graphics.connecting_renderer import ConnectingRenderer
from shared.messages import RoomStateMsg, RoomErrorMsg


class RoomWaitingView(BaseView):
    """
    Shown after Create (waiting for opponent) or after Join (briefly, before game starts).

    Transitions:
      RoomStateMsg(started=True)  → GOTO_GAME  (handled by GameClientApp)
      RoomErrorMsg                → GOTO_HOME with error message
    """

    def on_enter(self, context: dict) -> None:
        s              = context["app_state"]
        self._room_id  = s.room_id
        self._renderer = ConnectingRenderer()
        self._status   = (f"Waiting for opponent…  Room: {self._room_id}"
                          if self._room_id else "Waiting for opponent…")

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, RoomStateMsg) and not msg.started:
            # Creator receives this first with started=False — update room_id display
            self._room_id = msg.room_id
            self._status  = f"Waiting for opponent…  Room: {self._room_id}"
        if isinstance(msg, RoomErrorMsg):
            return ViewAction.GOTO_HOME
        return None

    def render(self, canvas) -> None:
        self._renderer.render(canvas, self._status)

    @property
    def error_message(self) -> str:
        return getattr(self, "_error", "")
