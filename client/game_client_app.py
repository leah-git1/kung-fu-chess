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
from client.app_state import AppState
from client.views.view_action import ViewAction
from client.views.view_manager import ViewManager
from client.views.connecting_view import ConnectingView
from client.views.home_view import HomeView
from client.views.matchmaking_view import MatchmakingView
from client.views.room_dialog_view import RoomDialogView
from client.views.room_waiting_view import RoomWaitingView
from client.views.game_view import GameView
from shared.messages import RoomStateMsg, RoomErrorMsg, TokenMsg, ShardConnectMsg
from shared.constants import DEFAULT_PORT
from shared.enums import Color
from client.log_utils.client_logger import log


class GameClientApp:
    def __init__(self, host: str, port: int = DEFAULT_PORT,
                 player_name: str = "Player", rating: int = 1200, token: str = ""):
        self._state = AppState(player_name, rating, token)
        self._ws    = WsClient(f"ws://{host}:{port}")
        self._window = WindowManager(
            gfx_config.WINDOW_TITLE,
            gfx_config.WINDOW_PX_W,
            gfx_config.WINDOW_PX_H,
        )
        self._vm = self._build_view_manager()
        self._registry = {
            RoomStateMsg:     self._on_game_start,
            RoomErrorMsg:     self._on_room_error,
            ShardConnectMsg:  self._on_shard_connect,
        }

    def _build_view_manager(self) -> ViewManager:
        s, ws = self._state, self._ws
        ctx   = lambda: {"app_state": s, "ws_client": ws}
        vm = ViewManager()
        vm.register(ViewAction.GOTO_HOME,         HomeView(),         ctx)
        vm.register(ViewAction.GOTO_MATCHMAKING,  MatchmakingView())
        vm.register(ViewAction.GOTO_ROOM_DIALOG,  RoomDialogView(),   ctx)
        vm.register(ViewAction.GOTO_ROOM_WAITING, RoomWaitingView(),  ctx)
        vm.register(ViewAction.GOTO_GAME,         GameView(),         ctx)
        return vm

    def run(self) -> None:
        self._ws.start()
        log(f"connecting to server as {self._state.player_name}")
        self._ws.send(TokenMsg(token=self._state.token,
                               username=self._state.player_name,
                               rating=self._state.rating))

        self._vm.init(ConnectingView(), {"status": "Connecting to server…"})

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

            self._vm.current.tick()

            for event in self._window.poll_events():
                if self._dispatch_event(event) == "close":
                    self._window.close()
                    return

            if not self._window.is_open():
                return

            canvas = GameImg.blank(gfx_config.WINDOW_PX_W, gfx_config.WINDOW_PX_H,
                                   (15, 15, 15, 255))
            self._vm.current.render(canvas)
            canvas.show(window_name=gfx_config.WINDOW_TITLE)

            remaining = gfx_config.FRAME_TIME_MS - elapsed
            if remaining > 0:
                time.sleep(remaining / 1000)

    def _handle_server_message(self, msg) -> None:
        if handler := self._registry.get(type(msg)):
            handler(msg)
            return
        action = self._vm.handle_server_message(msg)
        if action == ViewAction.GOTO_HOME:
            self._vm.switch(ViewAction.GOTO_HOME,
                            extra={"status_msg": "No opponent found. Try again later."})
        elif action:
            self._vm.switch(action)

    def _on_shard_connect(self, msg: ShardConnectMsg) -> None:
        """Server told us to connect to the game shard directly."""
        players = msg.players
        self._state.white_name = players[0]
        self._state.black_name = players[1]
        self._state.color  = Color(msg.color) if msg.color else Color.SPECTATOR
        self._state.room_id = msg.room_id
        log(f"connecting to shard {msg.shard_url} room={msg.room_id} color={msg.color}")
        # replace the WS connection with one pointing at the shard
        self._ws.reconnect(msg.shard_url, first_msg={
            "type": "shard_join",
            "room_id": msg.room_id,
            "token": msg.token,
            "color": msg.color,
        })
        self._vm.switch(ViewAction.GOTO_GAME)

    def _on_room_state_pre_start(self, msg: RoomStateMsg) -> None:
        """RoomStateMsg(started=False) — server confirmed auth, we're in lobby."""
        self._state.room_id = msg.room_id
        self._vm.switch(ViewAction.GOTO_HOME)

    def _on_game_start(self, msg: RoomStateMsg) -> None:
        if not msg.started:
            self._on_room_state_pre_start(msg)
            return
        players = msg.players
        if len(players) == 2:
            self._state.white_name = players[0]
            self._state.black_name = players[1]
        self._state.color   = Color(msg.color) if msg.color else Color.SPECTATOR
        self._state.room_id = msg.room_id
        log(f"game starting — room={msg.room_id} "
            f"role={self._state.color.name.lower()} players={players}")
        self._vm.switch(ViewAction.GOTO_GAME)

    def _on_room_error(self, msg: RoomErrorMsg) -> None:
        log(f"room error: {msg.reason}", level="warning")
        self._vm.switch(ViewAction.GOTO_HOME, extra={"status_msg": msg.reason})

    # ── input dispatch ────────────────────────────────────────────────────────

    def _dispatch_event(self, event: dict):
        kind = event["type"]
        view = self._vm.current

        def on_resize():
            if hasattr(view, "handle_resize"):
                view.handle_resize(event["width"], event["height"])

        def on_left_click():
            action = view.handle_click(event["x"], event["y"])
            if action == ViewAction.QUIT:
                return "close"
            if action:
                self._vm.switch(action)

        def on_right_click():
            if hasattr(view, "handle_right_click"):
                view.handle_right_click(event["x"], event["y"])

        def on_key():
            action = view.handle_key(event["key"])
            if action:
                self._vm.switch(action)

        registry = {
            gfx_config.EventType.RESIZE:      on_resize,
            gfx_config.EventType.LEFT_CLICK:  on_left_click,
            gfx_config.EventType.RIGHT_CLICK: on_right_click,
            "key":                            on_key,
        }
        if handler := registry.get(kind):
            return handler()

    @staticmethod
    def _now_ms() -> int:
        return int(time.monotonic() * 1000)
