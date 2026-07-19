import logging

_log = logging.getLogger(__name__)


class AnimationState:
    def __init__(self, sprite_key: str, loader):
        self._piece_key = sprite_key
        self._loader = loader
        self._current_folder = None
        self._state_entered_at_ms = 0
        self._current_animation = None
        _log.debug("AnimationState CREATED for piece_key=%s", self._piece_key)

    def update(self, piece_key: str, state_folder: str, now_ms: int):
        if piece_key != self._piece_key or state_folder != self._current_folder:
            _log.debug(
                "AnimationState TRANSITION key=%s  %r -> %r  at t=%d",
                piece_key, self._current_folder, state_folder, now_ms,
            )
            self._piece_key = piece_key
            self._current_folder = state_folder
            self._state_entered_at_ms = now_ms
            self._current_animation = self._loader.get_animation(piece_key, state_folder)

    def current_frame(self, now_ms: int):
        return self._current_animation.frame_at(now_ms - self._state_entered_at_ms)
