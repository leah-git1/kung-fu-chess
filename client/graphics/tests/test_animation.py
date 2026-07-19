"""
Tests for client/graphics/sprites/animation.py

No OpenCV — frames are plain sentinel objects.
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

import pytest
from graphics.sprites.animation import Animation

F0, F1, F2, F3 = object(), object(), object(), object()


# ── construction ──────────────────────────────────────────────────────────────

def test_empty_frames_raises():
    with pytest.raises(ValueError):
        Animation([], fps=12)


def test_stores_fps():
    a = Animation([F0], fps=24)
    assert a.fps == 24


# ── looping animation ─────────────────────────────────────────────────────────

def test_frame_at_zero_returns_first_frame():
    a = Animation([F0, F1, F2], fps=10, loop=True)
    assert a.frame_at(0) is F0


def test_frame_at_negative_returns_first_frame():
    a = Animation([F0, F1, F2], fps=10, loop=True)
    assert a.frame_at(-100) is F0


def test_frame_advances_at_correct_time():
    # fps=10 → 100 ms per frame
    a = Animation([F0, F1, F2], fps=10, loop=True)
    assert a.frame_at(100) is F1
    assert a.frame_at(200) is F2


def test_loop_wraps_around():
    a = Animation([F0, F1, F2], fps=10, loop=True)
    assert a.frame_at(300) is F0   # wraps back to frame 0


def test_loop_multiple_cycles():
    a = Animation([F0, F1], fps=10, loop=True)
    # fps=10 → 100 ms per frame; 2 frames = 200 ms per cycle
    assert a.frame_at(0)   is F0
    assert a.frame_at(100) is F1
    assert a.frame_at(200) is F0   # second cycle starts
    assert a.frame_at(300) is F1


# ── non-looping animation ─────────────────────────────────────────────────────

def test_non_loop_clamps_to_last_frame():
    a = Animation([F0, F1, F2], fps=10, loop=False)
    assert a.frame_at(9999) is F2


def test_non_loop_plays_normally_within_duration():
    a = Animation([F0, F1, F2], fps=10, loop=False)
    assert a.frame_at(0) is F0
    assert a.frame_at(100) is F1
    assert a.frame_at(200) is F2


# ── single-frame animation ────────────────────────────────────────────────────

def test_single_frame_always_returns_that_frame():
    a = Animation([F0], fps=12, loop=True)
    for t in [0, 100, 500, 9999]:
        assert a.frame_at(t) is F0


# ── frame duration ────────────────────────────────────────────────────────────

def test_frame_duration_matches_fps():
    a = Animation([F0, F1], fps=20)
    # 20 fps → 50 ms per frame
    assert a.frame_at(49) is F0
    assert a.frame_at(50) is F1
