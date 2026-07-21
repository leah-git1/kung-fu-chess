from __future__ import annotations
import sys, os, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from graphics.connecting_renderer import ConnectingRenderer
from shared.messages import SearchTimeoutMsg


class MatchmakingView(BaseView):
    """
    Shown while searching for an opponent.
    Reuses ConnectingRenderer for the status box.

    Transitions:
      RoomStateMsg(started=True) → handled by GameClientApp → GOTO_GAME
      SearchTimeoutMsg           → GOTO_HOME with timeout message
    """

    def on_enter(self, context: dict) -> None:
        self._renderer  = ConnectingRenderer()
        self._start_s   = time.monotonic()
        self._status    = "Searching for opponent…"

    def tick(self) -> None:
        elapsed = int(time.monotonic() - self._start_s)
        self._status = f"Searching for opponent… ({elapsed}s)"

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, SearchTimeoutMsg):
            return ViewAction.GOTO_HOME
        return None

    def render(self, canvas) -> None:
        self._renderer.render(canvas, self._status)
