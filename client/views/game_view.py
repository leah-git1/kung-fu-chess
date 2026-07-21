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

from client.network.board_mirror import BoardMirror
from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from shared.messages import StateUpdateMsg, GameOverMsg, MoveMsg, JumpMsg, MoveAckMsg, JumpAckMsg


class GameView(BaseView):
    """
    Networked game screen.

    Rendering is driven entirely by BoardMirror (fed by STATE_UPDATE from the server).
    No local Game instance — the server is authoritative.

    context keys:
      ws_client  : WsClient
      color      : "w" | "b"
      white_name : str
      black_name : str
      my_name    : str
      my_rating  : int
    """

    def on_enter(self, context: dict) -> None:
        self._ws     = context["ws_client"]
        self._color  = context.get("color", "w")
        self._mirror = BoardMirror()
        self._mapper = BoardMapper(gfx_config.CELL_PX)
        self._selected: tuple | None = None

        self._renderer = GameRenderer(
            context.get("white_name", "White"),
            context.get("black_name", "Black"),
            my_name=context.get("my_name", ""),
            my_rating=context.get("my_rating", 0),
        )

    def on_exit(self) -> None:
        self._selected = None

    def tick(self) -> None:
        pass  # time is driven by STATE_UPDATE from the server

    # ── server messages ───────────────────────────────────────────────────────

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, StateUpdateMsg):
            self._mirror.apply_state_update(msg.board, msg.time_ms, msg.motions)

        elif isinstance(msg, MoveAckMsg):
            from events.game_events import PieceMovedEvent, PieceCapturedEvent
            src = tuple(msg.from_cell)
            dst = tuple(msg.to_cell)
            # if something was at the destination it was captured
            target = self._mirror.get_piece_at(dst)
            if target is not None:
                self._renderer.bus.publish(PieceCapturedEvent(
                    at_cell=dst,
                    elapsed_ms=msg.time_ms,
                    piece_value=target.value,
                    by_color=self._mirror.get_piece_at(src).color if self._mirror.get_piece_at(src) else None,
                    captured_color=target.color,
                    captured_type=target.piece_type.value,
                ))
            mover = self._mirror.get_piece_at(src)
            if mover is not None:
                self._renderer.bus.publish(PieceMovedEvent(
                    color=mover.color,
                    origin=src,
                    destination=dst,
                    elapsed_ms=msg.time_ms,
                    piece_name=mover.sprite_key[1],
                ))

        elif isinstance(msg, GameOverMsg):
            self._mirror.apply_game_over(msg.winner)
            from events.game_events import GameOverEvent
            self._renderer.bus.publish(GameOverEvent(winner_color=msg.winner))

        return None

    # ── input ─────────────────────────────────────────────────────────────────

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

    def _on_board_click(self, bx: int, by: int, kind: str) -> None:
        cell = self._mapper.to_cell(bx, by)
        if not self._mirror.is_inside(cell):
            self._selected = None
            return

        if kind == "right_click":
            vm = self._mirror.get_piece_at(cell)
            if vm and vm.sprite_key[0] == self._color:
                self._ws.send(JumpMsg(cell=list(cell)))
            return

        if self._selected is None:
            vm = self._mirror.get_piece_at(cell)
            if vm and vm.sprite_key[0] == self._color:
                self._selected = cell
            return

        src = self._selected
        if src == cell:
            self._selected = None
            return

        # same color → reselect
        vm = self._mirror.get_piece_at(cell)
        if vm and vm.sprite_key[0] == self._color:
            self._selected = cell
            return

        self._ws.send(MoveMsg(from_cell=list(src), to_cell=list(cell)))
        self._selected = None

    # ── render ────────────────────────────────────────────────────────────────

    def render(self, canvas) -> None:
        self._renderer.render_frame(
            canvas,
            self._mirror,
            self._mirror.current_time,
            selected_cell=self._selected,
        )
