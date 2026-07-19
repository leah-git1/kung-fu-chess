from __future__ import annotations
import sys, os, time

_CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGIC_DIR  = os.path.join(os.path.dirname(_CLIENT_DIR), "logic")
sys.path.insert(0, _CLIENT_DIR)
sys.path.insert(0, _LOGIC_DIR)

from board.board_parser import BoardParser
from board.piece import Piece
from controller.board_mapper import BoardMapper
from controller.input_controller import InputController
from game.game import Game
from events.event_bus import EventBus
from events.game_event_source import GameEventSource

from graphics import gfx_config
from graphics.game_renderer import GameRenderer
from graphics.panels.panel_action import PanelAction

from client.views.base_view import BaseView
from client.views.view_action import ViewAction
from shared.messages import MoveAckMsg, JumpAckMsg, StateUpdateMsg, GameOverMsg, MoveMsg, JumpMsg


_STARTING_POSITION = """\
Board:
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
Commands:"""


class GameView(BaseView):
    """
    Networked game screen.

    Owns a real Game instance — identical to GraphicsApp — driven by
    MOVE_ACK / JUMP_ACK from the server.  All existing graphics work unchanged.

    context keys:
      ws_client  : WsClient
      color      : "w" | "b"
      white_name : str
      black_name : str
    """

    def on_enter(self, context: dict) -> None:
        self._ws    = context["ws_client"]
        self._color = context.get("color", "w")

        board = BoardParser().parse(_STARTING_POSITION.splitlines())
        self._game = Game(board)

        self._renderer    = GameRenderer(context.get("white_name", "White"),
                                         context.get("black_name", "Black"))
        self._controller  = InputController(BoardMapper(gfx_config.CELL_PX))
        self._event_source = GameEventSource(self._renderer.bus)
        self._last_ms     = self._now_ms()

    def on_exit(self) -> None:
        self._controller.reset()

    # ── called every frame by GameClientApp before render ─────────────────────

    def tick(self) -> None:
        now     = self._now_ms()
        elapsed = now - self._last_ms
        self._last_ms = now
        self._game.advance_time(elapsed)
        self._event_source.poll(self._game)

    # ── server messages ───────────────────────────────────────────────────────

    def handle_server_message(self, msg) -> ViewAction | None:
        if isinstance(msg, MoveAckMsg):
            src   = tuple(msg.from_cell)
            dst   = tuple(msg.to_cell)
            piece = self._game.get_piece_at(src)
            if piece is not Piece.EMPTY:
                self._game.request_move(piece, src, dst)

        elif isinstance(msg, JumpAckMsg):
            cell  = tuple(msg.cell)
            piece = self._game.get_piece_at(cell)
            if piece is not Piece.EMPTY:
                self._game.request_jump(piece, cell)

        elif isinstance(msg, StateUpdateMsg):
            # time-sync: nudge local clock toward server clock
            if msg.time_ms and abs(self._game.current_time - msg.time_ms) > 200:
                self._game.current_time = msg.time_ms

        elif isinstance(msg, GameOverMsg):
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
        cell  = self._controller._mapper.to_cell(bx, by)
        if not self._game.is_inside(cell):
            self._controller.reset()
            return
        piece = self._game.get_piece_at(cell)

        if kind == "right_click":
            if piece is not Piece.EMPTY and piece.color == self._color:
                self._ws.send(JumpMsg(cell=list(cell)))
            return

        if self._controller.selected is None:
            if piece is not Piece.EMPTY and piece.color == self._color:
                self._controller._selected = cell
            return

        src = self._controller.selected
        if src == cell:
            self._controller.reset()
            return

        src_piece = self._game.get_piece_at(src)
        if piece is not Piece.EMPTY and src_piece.is_same_color(piece):
            self._controller._selected = cell
            return

        self._ws.send(MoveMsg(from_cell=list(src), to_cell=list(cell)))
        self._controller.reset()

    # ── render ────────────────────────────────────────────────────────────────

    def render(self, canvas) -> None:
        self._renderer.render_frame(canvas, self._game, self._game.current_time,
                                    selected_cell=self._controller.selected)

    @staticmethod
    def _now_ms() -> int:
        return int(time.monotonic() * 1000)
