from graphics import gfx_config
from graphics.sprites.animation_state_machine import AnimationState
from graphics.sprites.sprite_loader import SpriteLoader
import cv2
import numpy as np


class PieceRenderer:
    def __init__(self, layout, loader=None):
        self._layout = layout
        self._loader = loader or SpriteLoader()
        self._states = {}   
        
    def render(self, canvas, game, now_ms):
        board_grid = game.snapshot()
        jumping_ids = {id(m.piece) for m in game.active_jumps()}
        moving_ids = self._draw_active_motions(canvas, game, now_ms, jumping_ids)
        self._draw_static_pieces(canvas, board_grid, moving_ids | jumping_ids, game, now_ms)

    def _draw_static_pieces(self, canvas, board_grid, skip_ids, game, now_ms):
        for r, row in enumerate(board_grid):
            for c, piece in enumerate(row):
                if piece is None or id(piece) in skip_ids:
                    continue
                self._draw_piece_at(canvas, piece, r, c, game, now_ms, is_jumping=False)

    def _draw_active_motions(self, canvas, game, now_ms, jumping_ids):
        drawn = set()
        for motion in game.active_moves():
            actual = motion.actual_destination
            full_duration = self._move_duration(motion.origin, motion.destination)
            actual_duration = self._move_duration(motion.origin, actual)
            start = motion.finish_time - full_duration
            elapsed = now_ms - start
            t = 0.0 if actual_duration <= 0 else max(0.0, min(1.0, elapsed / actual_duration))
            row = motion.origin[0] + (actual[0] - motion.origin[0]) * t
            col = motion.origin[1] + (actual[1] - motion.origin[1]) * t
            self._draw_piece_at(canvas, motion.piece, row, col, game, now_ms, is_jumping=False)
            drawn.add(id(motion.piece))
        for motion in game.active_jumps():
            self._draw_piece_at(canvas, motion.piece, motion.cell[0], motion.cell[1], game, now_ms, is_jumping=True)
            drawn.add(id(motion.piece))
        return drawn

    def _draw_piece_at(self, canvas, piece, row, col, game, now_ms, is_jumping):
        state = self._states.setdefault(id(piece), AnimationState(piece, self._loader))
        folder = gfx_config.JUMP_FOLDER if is_jumping else gfx_config.STATE_TO_FOLDER[piece.state_name]
        state.update(piece.sprite_key, folder, now_ms)
        frame = state.current_frame(now_ms)

        cs = self._layout.cell_size
        cell_x = self._layout.board_origin_x + int(col * cs)
        cell_y = self._layout.board_origin_y + int(row * cs)

        self._draw_cooldown_bar(canvas, piece, game, cell_x, cell_y, cs)
        frame.resize(cs, cs).draw_on(canvas, cell_x, cell_y)

    def _draw_cooldown_bar(self, canvas, piece, game, cell_x, cell_y, cell_size):
        result = game.cooldown_progress(piece)
        if result is None:
            return
        progress, rest_type = result
        color = gfx_config.COOLDOWN_BAR_COLOR if rest_type == "long" else gfx_config.COOLDOWN_BAR_COLOR_SHORT

        bar_h = int(cell_size * (1.0 - progress))
        if bar_h <= 0:
            return

        b, g, r, a = color
        alpha = a / 255.0
        img = canvas.img
        H, W = img.shape[:2]
        x1 = max(0, cell_x)
        y1 = max(0, cell_y + (cell_size - bar_h))
        x2 = min(W, cell_x + cell_size)
        y2 = min(H, cell_y + cell_size)
        if x2 <= x1 or y2 <= y1:
            return

        roi = img[y1:y2, x1:x2].astype(np.float32)
        roi[..., 0] = roi[..., 0] * (1 - alpha) + b * alpha
        roi[..., 1] = roi[..., 1] * (1 - alpha) + g * alpha
        roi[..., 2] = roi[..., 2] * (1 - alpha) + r * alpha
        img[y1:y2, x1:x2] = roi.astype(np.uint8)

    @staticmethod
    def _move_duration(origin, destination):
        return max(abs(destination[0] - origin[0]), abs(destination[1] - origin[1])) \
            * gfx_config.MOVE_DURATION_PER_CELL
