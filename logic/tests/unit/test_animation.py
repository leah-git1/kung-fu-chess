import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from graphics.sprites.animation import Animation
from graphics.sprites.animation_state_machine import AnimationState


FRAMES = ["f0", "f1", "f2", "f3", "f4"]   # plain strings as stand-in frames


# ── Animation ────────────────────────────────────────────────────────────────

class TestAnimationFrameAt:
    def _anim(self, fps=10, loop=True, frames=None):
        return Animation(frames or FRAMES, fps=fps, loop=loop)

    def test_zero_elapsed_returns_first_frame(self):
        assert self._anim().frame_at(0) == "f0"

    def test_negative_elapsed_returns_first_frame(self):
        assert self._anim().frame_at(-100) == "f0"

    def test_advances_to_correct_frame(self):
        # fps=10 → 100 ms per frame; at 250 ms → frame index 2
        assert self._anim(fps=10).frame_at(250) == "f2"

    def test_loops_back_to_start(self):
        # 5 frames × 100 ms = 500 ms full cycle; at 500 ms → frame 0 again
        assert self._anim(fps=10, loop=True).frame_at(500) == "f0"

    def test_no_loop_clamps_to_last_frame(self):
        anim = self._anim(fps=10, loop=False)
        assert anim.frame_at(9999) == "f4"

    def test_no_loop_mid_sequence(self):
        anim = self._anim(fps=10, loop=False)
        assert anim.frame_at(200) == "f2"

    def test_single_frame_always_returns_it(self):
        anim = Animation(["only"], fps=10, loop=True)
        assert anim.frame_at(0) == "only"
        assert anim.frame_at(9999) == "only"

    def test_empty_frames_raises(self):
        with pytest.raises(ValueError):
            Animation([], fps=10)

    def test_exact_frame_boundary(self):
        # at exactly 100 ms (fps=10) we should be on frame 1
        assert self._anim(fps=10).frame_at(100) == "f1"


# ── AnimationState ────────────────────────────────────────────────────────────

class _StubAnimation:
    def __init__(self, frames, fps=10):
        self._anim = Animation(frames, fps=fps)

    def frame_at(self, elapsed_ms):
        return self._anim.frame_at(elapsed_ms)


class _StubLoader:
    def __init__(self, animations):
        # animations: dict of folder -> list-of-frames
        self._animations = animations

    def piece_key(self, piece):
        return "PW"

    def get_animation(self, piece_key, state_folder):
        return _StubAnimation(self._animations[state_folder])


class TestAnimationState:
    def _make(self, folders=None):
        folders = folders or {"idle": FRAMES, "move": ["m0", "m1"]}
        loader = _StubLoader(folders)
        state = AnimationState(piece=object(), loader=loader)
        return state, loader

    def test_current_frame_after_update(self):
        state, _ = self._make()
        state.update("idle", now_ms=0)
        assert state.current_frame(0) == "f0"

    def test_elapsed_is_relative_to_state_entry(self):
        state, _ = self._make()
        state.update("idle", now_ms=1000)
        # 100 ms after entry at fps=10 → frame 1
        assert state.current_frame(1100) == "f1"

    def test_folder_change_resets_elapsed(self):
        state, _ = self._make()
        state.update("idle", now_ms=0)
        state.update("move", now_ms=500)
        # elapsed since "move" started = 0 → first move frame
        assert state.current_frame(500) == "m0"

    def test_same_folder_does_not_reset_elapsed(self):
        state, _ = self._make()
        state.update("idle", now_ms=0)
        state.update("idle", now_ms=999)   # same folder, should be ignored
        # elapsed is still from t=0, so at now=200 → frame 2
        assert state.current_frame(200) == "f2"

    def test_loader_called_only_on_folder_change(self):
        calls = []

        class TrackingLoader(_StubLoader):
            def get_animation(self, piece_key, folder):
                calls.append(folder)
                return super().get_animation(piece_key, folder)

        loader = TrackingLoader({"idle": FRAMES})
        state = AnimationState(piece=object(), loader=loader)
        state.update("idle", now_ms=0)
        state.update("idle", now_ms=100)
        state.update("idle", now_ms=200)
        assert calls.count("idle") == 1
