"""
Tests for client/views/game_view.py

GameView is network-driven: it receives server messages and delegates to
BoardMirror + NetworkEventAdapter. No rendering, no WebSocket, no OpenCV.
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

from unittest.mock import MagicMock, patch
from client.views.game_view import GameView
from client.network.board_mirror import BoardMirror
from shared.messages import StateUpdateMsg, MoveAckMsg, OpponentDisconnectedMsg, GameOverMsg
from shared.enums import Color


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_view(color=Color.WHITE):
    """Return a GameView with all rendering/network dependencies mocked."""
    view = GameView.__new__(GameView)
    view._ws               = MagicMock()
    view._color            = color
    view._spectator        = (color == Color.SPECTATOR)
    view._mirror           = BoardMirror()
    view._selected         = None
    view._disconnect_countdown = None
    view._renderer         = MagicMock()
    view._event_adapter    = MagicMock()
    view._mapper           = MagicMock()
    return view


def _empty_board():
    return [[None] * 8 for _ in range(8)]


# ── handle_server_message always returns None ─────────────────────────────────

def test_handle_server_message_returns_none_for_state_update():
    view = _make_view()
    msg = StateUpdateMsg(board=_empty_board(), time_ms=0, motions=None)
    assert view.handle_server_message(msg) is None


def test_handle_server_message_returns_none_for_move_ack():
    view = _make_view()
    assert view.handle_server_message(MoveAckMsg(from_cell=[0,0], to_cell=[0,1], time_ms=0)) is None


def test_handle_server_message_returns_none_for_game_over():
    view = _make_view()
    assert view.handle_server_message(GameOverMsg(winner="w", reason="king captured")) is None


def test_handle_server_message_returns_none_for_disconnect():
    view = _make_view()
    assert view.handle_server_message(OpponentDisconnectedMsg(grace_s=30)) is None


# ── StateUpdateMsg ────────────────────────────────────────────────────────────

def test_state_update_advances_mirror_time():
    view = _make_view()
    view.handle_server_message(StateUpdateMsg(board=_empty_board(), time_ms=500, motions=None))
    assert view._mirror.current_time == 500


def test_state_update_with_piece_populates_mirror():
    view = _make_view()
    board = _empty_board()
    board[3][4] = {"k": "wR", "s": "idle"}
    view.handle_server_message(StateUpdateMsg(board=board, time_ms=0, motions=None))
    assert view._mirror.get_piece_at((3, 4)).sprite_key == "wR"


# ── MoveAckMsg ────────────────────────────────────────────────────────────────

def test_move_ack_delegates_to_event_adapter():
    view = _make_view()
    msg = MoveAckMsg(from_cell=[0, 0], to_cell=[0, 4], time_ms=100)
    view.handle_server_message(msg)
    view._event_adapter.on_move_ack.assert_called_once_with(msg)


# ── OpponentDisconnectedMsg ───────────────────────────────────────────────────

def test_disconnect_sets_countdown():
    view = _make_view()
    view.handle_server_message(OpponentDisconnectedMsg(grace_s=30))
    assert view._disconnect_countdown == 30


def test_disconnect_countdown_updates_on_repeat():
    view = _make_view()
    view.handle_server_message(OpponentDisconnectedMsg(grace_s=30))
    view.handle_server_message(OpponentDisconnectedMsg(grace_s=10))
    assert view._disconnect_countdown == 10


# ── GameOverMsg ───────────────────────────────────────────────────────────────

def test_game_over_sets_mirror_winner():
    view = _make_view()
    view.handle_server_message(GameOverMsg(winner="b", reason="king captured"))
    assert view._mirror.game_over is True
    assert view._mirror.winner_color == "b"


def test_game_over_sets_panel_reason():
    view = _make_view()
    view.handle_server_message(GameOverMsg(winner="w", reason="resignation"))
    view._renderer.game_over_panel.set_reason.assert_called_once_with("resignation")


def test_game_over_delegates_to_event_adapter():
    view = _make_view()
    msg = GameOverMsg(winner="w", reason="king captured")
    view.handle_server_message(msg)
    view._event_adapter.on_game_over.assert_called_once_with(msg)


# ── on_exit ───────────────────────────────────────────────────────────────────

def test_on_exit_clears_selection():
    view = _make_view()
    view._selected = (3, 3)
    view.on_exit()
    assert view._selected is None


# ── spectator mode ────────────────────────────────────────────────────────────

def test_spectator_handle_click_returns_none():
    view = _make_view(color=Color.SPECTATOR)
    assert view.handle_click(100, 100) is None


def test_spectator_flag_set_correctly():
    view = _make_view(color=Color.SPECTATOR)
    assert view._spectator is True


def test_non_spectator_flag():
    view = _make_view(color=Color.WHITE)
    assert view._spectator is False


# ── handle_click game over panel ──────────────────────────────────────────────

def test_handle_click_returns_quit_when_game_over_panel_closes():
    from graphics.panels.panel_action import PanelAction
    view = _make_view()
    view._renderer.game_over_panel.active = True
    view._renderer.game_over_panel.on_click.return_value = PanelAction.CLOSE
    from client.views.view_action import ViewAction
    assert view.handle_click(100, 100) == ViewAction.QUIT


def test_handle_click_returns_none_when_game_over_panel_not_closed():
    from graphics.panels.panel_action import PanelAction
    view = _make_view()
    view._renderer.game_over_panel.active = True
    view._renderer.game_over_panel.on_click.return_value = None
    assert view.handle_click(100, 100) is None


def test_handle_click_no_board_hit_returns_none():
    view = _make_view()
    view._renderer.game_over_panel.active = False
    view._renderer.layout.screen_to_board_pixel.return_value = None
    assert view.handle_click(0, 0) is None


# ── handle_resize ─────────────────────────────────────────────────────────────

def test_handle_resize_delegates_to_layout():
    view = _make_view()
    view.handle_resize(1280, 720)
    view._renderer.layout.on_resize.assert_called_once_with(1280, 720)
