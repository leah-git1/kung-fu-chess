"""
Tests for client/views/game_view.py — clock synchronisation logic only.

GameView owns a real Game and drives it with MOVE_ACK / JUMP_ACK.
The tests here focus on the _pending_clock_nudge mechanism that was
introduced to fix animation stuttering caused by multiple STATE_UPDATE
messages queuing up between frames.

No rendering, no WebSocket, no OpenCV.
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

from unittest.mock import MagicMock, patch
from shared.messages import StateUpdateMsg, MoveAckMsg, JumpAckMsg, GameOverMsg
from client.views.game_view import GameView


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_view():
    """Return a GameView wired up with a fake ws and no renderer."""
    view = GameView.__new__(GameView)
    # Minimal on_enter without touching OpenCV
    from board.board_parser import BoardParser
    from game.game import Game
    from events.event_bus import EventBus
    from events.game_event_source import GameEventSource

    _STARTING = """\
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
    board = BoardParser().parse(_STARTING.splitlines())
    view._game = Game(board)
    view._ws = MagicMock()
    view._color = "w"
    view._last_ms = 0
    view._pending_clock_nudge = 0
    view._renderer = MagicMock()
    view._controller = MagicMock()
    view._controller.selected = None
    view._event_source = MagicMock()
    return view


# ── STATE_UPDATE clock nudge ──────────────────────────────────────────────────

def test_state_update_stores_drift_as_pending_nudge():
    view = _make_view()
    view._game.current_time = 1000
    view.handle_server_message(StateUpdateMsg(board=[], time_ms=1050, motions=None))
    assert view._pending_clock_nudge == 50


def test_multiple_state_updates_only_last_drift_kept():
    """Multiple queued messages must not compound — only the latest matters."""
    view = _make_view()
    view._game.current_time = 1000
    view.handle_server_message(StateUpdateMsg(board=[], time_ms=1010, motions=None))
    view.handle_server_message(StateUpdateMsg(board=[], time_ms=1050, motions=None))
    view.handle_server_message(StateUpdateMsg(board=[], time_ms=1080, motions=None))
    # pending nudge is the drift from the last message, not the sum
    assert view._pending_clock_nudge == 80


def test_tick_applies_nudge_once_then_clears_it():
    view = _make_view()
    view._game.current_time = 1000
    view._pending_clock_nudge = 30
    before = view._game.current_time
    with patch.object(view, '_now_ms', return_value=view._last_ms + 33):
        view.tick()
    # nudge capped at 20, then advance_time(33) added
    assert view._pending_clock_nudge == 0
    assert view._game.current_time == before + 20 + 33


def test_tick_nudge_capped_at_positive_20():
    view = _make_view()
    view._game.current_time = 1000
    view._pending_clock_nudge = 999   # large positive drift
    with patch.object(view, '_now_ms', return_value=view._last_ms + 0):
        view.tick()
    # only 20 ms applied, not 999
    assert view._game.current_time == 1020


def test_tick_nudge_capped_at_negative_20():
    view = _make_view()
    view._game.current_time = 1000
    view._pending_clock_nudge = -999  # large negative drift
    with patch.object(view, '_now_ms', return_value=view._last_ms + 0):
        view.tick()
    assert view._game.current_time == 980


def test_tick_no_nudge_when_zero():
    view = _make_view()
    view._game.current_time = 500
    view._pending_clock_nudge = 0
    with patch.object(view, '_now_ms', return_value=view._last_ms + 33):
        view.tick()
    assert view._game.current_time == 533


def test_tick_clears_pending_nudge_after_application():
    view = _make_view()
    view._pending_clock_nudge = 15
    with patch.object(view, '_now_ms', return_value=view._last_ms + 0):
        view.tick()
    assert view._pending_clock_nudge == 0


# ── MOVE_ACK ──────────────────────────────────────────────────────────────────

def test_move_ack_starts_motion():
    view = _make_view()
    msg = MoveAckMsg(from_cell=[6, 0], to_cell=[4, 0], time_ms=0)
    view.handle_server_message(msg)
    assert len(view._game.active_moves()) == 1


def test_move_ack_ignored_for_empty_cell():
    view = _make_view()
    msg = MoveAckMsg(from_cell=[3, 3], to_cell=[4, 3], time_ms=0)
    view.handle_server_message(msg)
    assert len(view._game.active_moves()) == 0


# ── JUMP_ACK ──────────────────────────────────────────────────────────────────

def test_jump_ack_starts_jump():
    view = _make_view()
    msg = JumpAckMsg(cell=[6, 0], time_ms=0)
    view.handle_server_message(msg)
    assert len(view._game.active_jumps()) == 1


def test_jump_ack_ignored_for_empty_cell():
    view = _make_view()
    msg = JumpAckMsg(cell=[3, 3], time_ms=0)
    view.handle_server_message(msg)
    assert len(view._game.active_jumps()) == 0


# ── GAME_OVER ─────────────────────────────────────────────────────────────────

def test_game_over_publishes_event():
    view = _make_view()
    view.handle_server_message(GameOverMsg(winner="w", reason="king captured"))
    view._renderer.bus.publish.assert_called_once()


# ── handle_server_message returns None ───────────────────────────────────────

def test_handle_server_message_always_returns_none():
    view = _make_view()
    for msg in [
        StateUpdateMsg(board=[], time_ms=0, motions=None),
        MoveAckMsg(from_cell=[6, 0], to_cell=[4, 0], time_ms=0),
        JumpAckMsg(cell=[6, 0], time_ms=0),
        GameOverMsg(winner="b", reason="king captured"),
    ]:
        assert view.handle_server_message(msg) is None
