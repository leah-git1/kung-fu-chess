"""
Tests for client/graphics/sprites/animation_state_machine.py

No OpenCV, no sprite files — the loader is stubbed.
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

from unittest.mock import MagicMock
from board.piece import Piece
from board.piece_type import PieceType
from graphics.sprites.animation_state_machine import AnimationState


# ── helpers ───────────────────────────────────────────────────────────────────

def _piece(color="w", pt="R"):
    return Piece(color, PieceType(pt))


def _loader(*frames_per_animation):
    """Return a stub loader whose get_animation returns a mock animation."""
    loader = MagicMock()
    def _get(key, folder):
        anim = MagicMock()
        anim.frame_at.return_value = MagicMock()   # a fake frame
        return anim
    loader.get_animation.side_effect = _get
    return loader


# ── construction ──────────────────────────────────────────────────────────────

def test_initial_folder_is_none():
    p = _piece()
    state = AnimationState(p, _loader())
    assert state._current_folder is None


def test_initial_animation_is_none():
    p = _piece()
    state = AnimationState(p, _loader())
    assert state._current_animation is None


def test_piece_key_stored_as_sprite_key_string():
    p = _piece("w", "R")
    state = AnimationState(p, _loader())
    assert state._piece_key == "wR"


# ── update — first call ───────────────────────────────────────────────────────

def test_first_update_loads_animation():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=0)
    loader.get_animation.assert_called_once_with("wR", "idle")


def test_first_update_sets_folder():
    state = AnimationState(_piece(), _loader())
    state.update("wR", "idle", now_ms=100)
    assert state._current_folder == "idle"


def test_first_update_records_entered_at():
    state = AnimationState(_piece(), _loader())
    state.update("wR", "idle", now_ms=250)
    assert state._state_entered_at_ms == 250


# ── update — same folder, no reload ──────────────────────────────────────────

def test_same_folder_does_not_reload_animation():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=0)
    state.update("wR", "idle", now_ms=50)
    state.update("wR", "idle", now_ms=100)
    assert loader.get_animation.call_count == 1


def test_same_folder_does_not_reset_entered_at():
    state = AnimationState(_piece(), _loader())
    state.update("wR", "idle", now_ms=100)
    state.update("wR", "idle", now_ms=200)
    assert state._state_entered_at_ms == 100


# ── update — folder change ────────────────────────────────────────────────────

def test_folder_change_reloads_animation():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=0)
    state.update("wR", "move", now_ms=500)
    assert loader.get_animation.call_count == 2


def test_folder_change_resets_entered_at():
    state = AnimationState(_piece(), _loader())
    state.update("wR", "idle", now_ms=0)
    state.update("wR", "move", now_ms=500)
    assert state._state_entered_at_ms == 500


def test_folder_change_updates_current_folder():
    state = AnimationState(_piece(), _loader())
    state.update("wR", "idle", now_ms=0)
    state.update("wR", "long_rest", now_ms=1000)
    assert state._current_folder == "long_rest"


# ── update — key change ───────────────────────────────────────────────────────

def test_key_change_reloads_animation():
    loader = _loader()
    state = AnimationState(_piece("w", "R"), loader)
    state.update("wR", "idle", now_ms=0)
    state.update("wQ", "idle", now_ms=100)   # promoted to queen
    assert loader.get_animation.call_count == 2


def test_key_change_resets_entered_at():
    state = AnimationState(_piece("w", "R"), _loader())
    state.update("wR", "idle", now_ms=0)
    state.update("wQ", "idle", now_ms=100)
    assert state._state_entered_at_ms == 100


# ── current_frame ─────────────────────────────────────────────────────────────

def test_current_frame_passes_elapsed_to_animation():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=1000)
    anim = state._current_animation          # the actual object returned by side_effect
    state.current_frame(now_ms=1300)
    anim.frame_at.assert_called_once_with(300)


def test_current_frame_elapsed_is_zero_at_entry():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=500)
    anim = state._current_animation
    state.current_frame(now_ms=500)
    anim.frame_at.assert_called_once_with(0)


def test_current_frame_elapsed_grows_each_call():
    loader = _loader()
    state = AnimationState(_piece(), loader)
    state.update("wR", "idle", now_ms=0)
    anim = state._current_animation
    state.current_frame(now_ms=100)
    state.current_frame(now_ms=200)
    calls = [c.args[0] for c in anim.frame_at.call_args_list]
    assert calls == [100, 200]


# ── full state-machine sequence ───────────────────────────────────────────────

def test_idle_to_move_to_long_rest_sequence():
    loader = _loader()
    state = AnimationState(_piece(), loader)

    state.update("wR", "idle", now_ms=0)
    assert state._current_folder == "idle"

    state.update("wR", "move", now_ms=1000)
    assert state._current_folder == "move"
    assert state._state_entered_at_ms == 1000

    state.update("wR", "long_rest", now_ms=2600)
    assert state._current_folder == "long_rest"
    assert state._state_entered_at_ms == 2600

    state.update("wR", "idle", now_ms=4600)
    assert state._current_folder == "idle"
    assert loader.get_animation.call_count == 4
