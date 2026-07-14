class Animation:
    def __init__(self, frames, fps, loop=True):
        if not frames:
            raise ValueError("Animation requires at least one frame")
        self.frames, self.fps, self.loop = frames, fps, loop
        self._frame_duration_ms = 1000 / fps

    def frame_at(self, elapsed_ms):
        if elapsed_ms <= 0:
            return self.frames[0]
        index = int(elapsed_ms // self._frame_duration_ms)
        return self.frames[index % len(self.frames)] if self.loop \
            else self.frames[min(index, len(self.frames) - 1)]