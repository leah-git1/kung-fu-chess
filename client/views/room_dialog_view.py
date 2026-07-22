from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from graphics.panels.room_dialog import RoomDialog, RoomDialogAction
from shared.messages import RoomCreateMsg, RoomJoinMsg


class RoomDialogView(BaseView):
    """
    Renders the room dialog (Create / Join / Cancel).

    context keys:
      ws_client : WsClient
    """

    def on_enter(self, context: dict) -> None:
        self._ws     = context["ws_client"]
        self._dialog = RoomDialog()

    def handle_click(self, x: int, y: int) -> ViewAction | None:
        action = self._dialog.on_click(x, y)
        if action == RoomDialogAction.CREATE:
            self._ws.send(RoomCreateMsg(room_id=""))
            return ViewAction.GOTO_ROOM_WAITING
        if action == RoomDialogAction.JOIN:
            if self._dialog.room_id:
                self._ws.send(RoomJoinMsg(room_id=self._dialog.room_id))
                return ViewAction.GOTO_ROOM_WAITING
        if action == RoomDialogAction.CANCEL:
            return ViewAction.GOTO_HOME
        return None

    def handle_key(self, key: int) -> ViewAction | None:
        if key == 27:   # Escape
            return ViewAction.GOTO_HOME
        self._dialog.on_key(key)
        return None

    def render(self, canvas) -> None:
        self._dialog.render(canvas)
