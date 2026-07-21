from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.views.view_action import ViewAction


class BaseView:
    """
    Interface every client screen must implement.

    Rendering is done by client/graphics — views receive a canvas and draw on it.
    No OpenCV imports belong here; this file must stay importable without a display.
    """

    def on_enter(self, context: dict) -> None:
        """Called once when this view becomes the active view.

        context: arbitrary data passed by the caller (e.g. winner name, room id).
        """

    def on_exit(self) -> None:
        """Called once just before this view is replaced by another."""

    def handle_click(self, x: int, y: int) -> "ViewAction | None":
        """Left-click at screen coordinates. Return a ViewAction to trigger a transition."""

    def handle_key(self, key: int) -> "ViewAction | None":
        """Key press (cv2 key code). Used for text-entry screens (login, room name)."""

    def handle_server_message(self, msg) -> "ViewAction | None":
        """React to an inbound network message (already deserialised dataclass)."""

    def render(self, canvas) -> None:
        """Draw this view onto canvas (a GameImg). Called every frame."""
        
    def tick(self):
        pass
