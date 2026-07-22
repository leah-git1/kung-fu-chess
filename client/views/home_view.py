from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from graphics.home_renderer import HomeRenderer
from shared.messages import PlayRequestMsg
from shared.enums import PlayMode


class HomeView(BaseView):
    """
    Home screen shown after login.
    Displays player name + ELO and a Play button.

    context keys:
      ws_client   : WsClient
      player_name : str
      rating      : int
    """

    def on_enter(self, context: dict) -> None:
        self._ws          = context["ws_client"]
        self._player_name = context.get("player_name", "Player")
        self._rating      = context.get("rating", 1200)
        self._status_msg  = context.get("status_msg", "")
        self._renderer    = HomeRenderer()
        self._btn_rect    = None   # (x, y, w, h) — set on first render

    def handle_click(self, x: int, y: int) -> ViewAction | None:
        if self._btn_rect:
            bx, by, bw, bh = self._btn_rect
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self._ws.send(PlayRequestMsg(mode=PlayMode.RANKED.value))
                return ViewAction.GOTO_MATCHMAKING
        return None

    def render(self, canvas) -> None:
        self._btn_rect = self._renderer.render(canvas, self._player_name, self._rating,
                                               status_msg=self._status_msg)
