"""
GameClientApp — the networked client application loop.

Flow: ConnectingView → HomeView → MatchmakingView → GameView
"""
import time
import sys, os

_CLIENT_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGIC_DIR  = os.path.join(os.path.dirname(_CLIENT_DIR), "logic")
sys.path.insert(0, _CLIENT_DIR)
sys.path.insert(0, _LOGIC_DIR)

from graphics import gfx_config
from graphics.img_provider import GameImg, WindowManager

from client.network.ws_client import WsClient
from client.views.view_action import ViewAction
from client.views.connecting_view import ConnectingView
from client.views.home_view import HomeView
from client.views.matchmaking_view import MatchmakingView
from client.views.game_view import GameView
from shared.messages import RoomStateMsg, LoginMsg, LoginOkMsg, LoginFailMsg, SearchTimeoutMsg
from shared.constants import DEFAULT_PORT


class GameClientApp:
    def __init__(self, host: str, port: int = DEFAULT_PORT,
                 player_name: str = "Player", password: str = "",
                 register: bool = False, rating: int = 1200):
        self._player_name = player_name
        self._password    = password
        self._register    = register
        self._rating      = rating
        url = f"ws://{host}:{port}"

        self._ws = WsClient(url)

        self._connecting_view  = ConnectingView()
        self._home_view        = HomeView()
        self._matchmaking_view = MatchmakingView()
        self._game_view        = GameView()

        self._window = WindowManager(
            gfx_config.WINDOW_TITLE,
            gfx_config.WINDOW_PX_W,
            gfx_config.WINDOW_PX_H,
        )

        self._color      = "w"
        self._white_name = "White"
        self._black_name = "Black"
        self._current_view = self._connecting_view

    def run(self) -> None:
        self._ws.start()
        self._ws.send(LoginMsg(name=self._player_name, password=self._password,
                               register=self._register))
        self._current_view.on_enter({"status": "Connecting to server…"})

        last_ms = self._now_ms()
        while self._window.is_open():
            now     = self._now_ms()
            elapsed = now - last_ms
            last_ms = now

            while not self._ws.inbound.empty():
                msg = self._ws.inbound.get_nowait()
                self._handle_server_message(msg)
                if not self._window.is_open():
                    return

            self._current_view.tick()

            for event in self._window.poll_events():
                if self._dispatch_event(event) == "close":
                    self._window.close()
                    return

            canvas = GameImg.blank(gfx_config.WINDOW_PX_W, gfx_config.WINDOW_PX_H,
                                   (15, 15, 15, 255))
            self._current_view.render(canvas)
            canvas.show(window_name=gfx_config.WINDOW_TITLE)

            remaining = gfx_config.FRAME_TIME_MS - elapsed
            if remaining > 0:
                time.sleep(remaining / 1000)

    # ── server message routing ────────────────────────────────────────────────

    def _handle_server_message(self, msg) -> None:
        if isinstance(msg, LoginOkMsg):
            self._player_name = msg.name
            self._rating      = msg.elo
            self._switch_to_home()
            return

        if isinstance(msg, LoginFailMsg):
            print(f"Auth failed: {msg.reason}")
            self._window.close()
            return

        if isinstance(msg, RoomStateMsg) and msg.started:
            players = msg.players
            if len(players) == 2:
                self._white_name = players[0]
                self._black_name = players[1]
            if msg.color:
                self._color = msg.color
            self._switch_to_game()
            return

        action = self._current_view.handle_server_message(msg)
        if action == ViewAction.GOTO_HOME:
            # MatchmakingView returns GOTO_HOME on timeout — pass the message
            self._switch_to_home({"status_msg": "No opponent found. Try again later."})
        elif action:
            self._switch(action)

    # ── view transitions ──────────────────────────────────────────────────────

    def _switch_to_home(self, extra: dict = None) -> None:
        self._current_view.on_exit()
        ctx = {
            "ws_client":   self._ws,
            "player_name": self._player_name,
            "rating":      self._rating,
        }
        if extra:
            ctx.update(extra)
        self._home_view.on_enter(ctx)
        self._current_view = self._home_view

    def _switch_to_matchmaking(self) -> None:
        self._current_view.on_exit()
        self._matchmaking_view.on_enter({})
        self._current_view = self._matchmaking_view

    def _switch_to_game(self) -> None:
        self._current_view.on_exit()
        self._game_view.on_enter({
            "ws_client":   self._ws,
            "color":       self._color,
            "white_name":  self._white_name,
            "black_name":  self._black_name,
            "my_rating":   self._rating,
            "my_name":     self._player_name,
        })
        self._current_view = self._game_view

    def _switch(self, action: ViewAction, context: dict = None) -> None:
        if action == ViewAction.QUIT:
            self._window.close()
        elif action == ViewAction.GOTO_HOME:
            self._switch_to_home(context or {})
        elif action == ViewAction.GOTO_MATCHMAKING:
            self._switch_to_matchmaking()
        elif action == ViewAction.GOTO_GAME:
            self._switch_to_game()

    # ── input dispatch ────────────────────────────────────────────────────────

    def _dispatch_event(self, event: dict):
        kind = event["type"]
        if kind == "resize":
            if hasattr(self._current_view, "handle_resize"):
                self._current_view.handle_resize(event["width"], event["height"])
        elif kind == "left_click":
            action = self._current_view.handle_click(event["x"], event["y"])
            if action == ViewAction.QUIT:
                return "close"
            if action:
                self._switch(action)
        elif kind == "right_click":
            if hasattr(self._current_view, "handle_right_click"):
                self._current_view.handle_right_click(event["x"], event["y"])

    @staticmethod
    def _now_ms() -> int:
        return int(time.monotonic() * 1000)
