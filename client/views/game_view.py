from __future__ import annotations
import sys, os

_CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGIC_DIR  = os.path.join(os.path.dirname(_CLIENT_DIR), "logic")
sys.path.insert(0, _CLIENT_DIR)
sys.path.insert(0, _LOGIC_DIR)

from controller.board_mapper import BoardMapper
from graphics import gfx_config
from graphics.game_renderer import GameRenderer
from graphics.panels.panel_action import PanelAction
from events.event_bus import EventBus
from events.network_event_adapter import NetworkEventAdapter

from client.network.board_mirror import BoardMirror
from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from shared.messages import StateUpdateMsg, GameOverMsg, MoveMsg, JumpMsg, MoveAckMsg, OpponentDisconnectedMsg
from shared.enums import Color


class GameView(BaseView):
    """
    Networked game screen.
    Rendering driven by BoardMirror (STATE_UPDATE). Server is authoritative.

    context keys:
      ws_client, color, white_name, black_name, my_name, my_rating
    """

    def on_enter(self, context: dict) -> None:
        self._ws     = context["ws_client"]
        self._color  = context.get("color", Color.WHITE)
        self._mirror = BoardMirror(on_capture=self._on_capture)
        self._mapper = BoardMapper(gfx_config.CELL_PX)
        self._selected: tuple | None = None
        self._disconnect_countdown: int | None = None

        bus = EventBus()
        self._renderer = GameRenderer(
            context.get("white_name", "White"),
            context.get("black_name", "Black"),
            bus,
            my_name=context.get("my_name", ""),
            my_rating=context.get("my_rating", 0),
            player_color=self._color.value,
        )
        self._event_adapter = NetworkEventAdapter(bus, self._mirror)

    def on_exit(self) -> None:
        self._selected = None

    def tick(self) -> None:
        pass

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, StateUpdateMsg):
            self._mirror.apply_state_update(msg.board, msg.time_ms, msg.motions)

        elif isinstance(msg, MoveAckMsg):
            self._event_adapter.on_move_ack(msg)

        elif isinstance(msg, OpponentDisconnectedMsg):
            self._disconnect_countdown = msg.grace_s

        elif isinstance(msg, GameOverMsg):
            self._mirror.apply_game_over(msg.winner)
            self._renderer.game_over_panel.set_reason(msg.reason)
            self._event_adapter.on_game_over(msg)

        return None

    def handle_click(self, x: int, y: int) -> ViewAction | None:
        if self._renderer.game_over_panel.active:
            if self._renderer.game_over_panel.on_click(x, y) == PanelAction.CLOSE:
                return ViewAction.QUIT
            return None
        bp = self._renderer.layout.screen_to_board_pixel(x, y)
        if bp:
            self._on_board_click(*bp, "left_click")
        return None

    def handle_right_click(self, x: int, y: int) -> None:
        bp = self._renderer.layout.screen_to_board_pixel(x, y)
        if bp:
            self._on_board_click(*bp, "right_click")

    def handle_resize(self, w: int, h: int) -> None:
        self._renderer.layout.on_resize(w, h)

    def _on_capture(self, vm, at_cell: tuple, time_ms: int, by_color: str | None) -> None:
        self._event_adapter.on_capture(vm, at_cell, time_ms, by_color)

    def _to_server_cell(self, cell: tuple) -> tuple:
        """Flip screen cell back to server coordinates for black player."""
        if self._color == Color.BLACK:
            return (7 - cell[0], 7 - cell[1])
        return cell

    def _on_board_click(self, bx: int, by: int, kind: str) -> None:
        cell = self._to_server_cell(self._mapper.to_cell(bx, by))
        if not self._mirror.is_inside(cell):
            self._selected = None
            return

        if kind == "right_click":
            vm = self._mirror.get_piece_at(cell)
            if vm and vm.sprite_key[0] == self._color.value:
                self._ws.send(JumpMsg(cell=list(cell)))
            return

        if self._selected is None:
            vm = self._mirror.get_piece_at(cell)
            if vm and vm.sprite_key[0] == self._color.value:
                self._selected = cell
            return

        src = self._selected
        if src == cell:
            self._selected = None
            return

        vm = self._mirror.get_piece_at(cell)
        if vm and vm.sprite_key[0] == self._color.value:
            self._selected = cell
            return

        self._ws.send(MoveMsg(from_cell=list(src), to_cell=list(cell)))
        self._selected = None

    def render(self, canvas) -> None:
        self._renderer.render_frame(
            canvas,
            self._mirror,
            self._mirror.current_time,
            selected_cell=self._selected,
            disconnect_countdown=self._disconnect_countdown,
        )
