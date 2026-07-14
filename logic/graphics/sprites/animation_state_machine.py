class AnimationState:
    def __init__(self, piece, loader):
        self._piece_key = loader.piece_key(piece)
        self._loader = loader
        self._current_folder = None
        self._state_entered_at_ms = 0
        self._current_animation = None

    def update(self, state_folder, now_ms):
        if state_folder != self._current_folder:
            self._current_folder = state_folder
            self._state_entered_at_ms = now_ms
            self._current_animation = self._loader.get_animation(self._piece_key, state_folder)

    def current_frame(self, now_ms):
        return self._current_animation.frame_at(now_ms - self._state_entered_at_ms)