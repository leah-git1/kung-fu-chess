import json, os, re
from graphics import gfx_config
from graphics.img_provider import GameImg
from graphics.sprites.animation import Animation

_NUM = re.compile(r"\d+")


class SpriteLoader:
    def __init__(self, pieces_dir=gfx_config.PIECES_DIR):
        self._pieces_dir = pieces_dir
        self._cache = {}   # (piece_key, state_folder) -> Animation

    def get_animation(self, piece_key, state_folder):
        key = (piece_key, state_folder)
        if key not in self._cache:
            self._cache[key] = self._load(piece_key, state_folder)
        return self._cache[key]

    def _load(self, piece_key, state_folder):
        state_dir = os.path.join(self._pieces_dir, piece_key, "states", state_folder)
        with open(os.path.join(state_dir, "config.json")) as f:
            cfg = json.load(f)
        fps = cfg["graphics"]["frames_per_sec"]
        loop = cfg["graphics"]["is_loop"]
        frames_dir = os.path.join(state_dir, "sprites")
        names = sorted(os.listdir(frames_dir), key=lambda n: int(_NUM.match(n).group()))
        frames = [GameImg.read(os.path.join(frames_dir, n),
                               size=(gfx_config.CELL_PX, gfx_config.CELL_PX))
                  for n in names]
        return Animation(frames, fps=fps, loop=loop)

    @staticmethod
    def piece_key(piece):
        return f"{piece.color.lower()}{piece.piece_type.value.upper()}"