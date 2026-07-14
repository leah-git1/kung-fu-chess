from board.piece import Piece
from graphics import gfx_config
from graphics.sprites.animation_state_machine import AnimationState
from graphics.sprites.sprite_loader import SpriteLoader
import config as logic_config

class PieceRenderer:
    def __init__(self, layout, loader=None):
        self._layout = layout
        self._loader = loader or SpriteLoader()
        self._states = {}   # id(piece) -> AnimationState

    def render(self, canvas, game, now_ms):
        board_grid = game.snapshot()
        jumping_ids = {id(m.piece) for m in game.active_jumps()}
        moving_ids = self._draw_active_motions(canvas, game, now_ms, jumping_ids)
        self._draw_static_pieces(canvas, board_grid, moving_ids | jumping_ids, now_ms)

    def _draw_static_pieces(self, canvas, board_grid, skip_ids, now_ms):
        for r, row in enumerate(board_grid):
            for c, piece in enumerate(row):
                if piece is Piece.EMPTY or id(piece) in skip_ids:
                    continue
                self._draw_piece_at(canvas, piece, r, c, now_ms, is_jumping=False)

    def _draw_active_motions(self, canvas, game, now_ms, jumping_ids):
        drawn = set()
        for motion in game.active_moves():
            duration = self._move_duration(motion.origin, motion.destination)
            start = motion.finish_time - duration
            t = 0.0 if duration <= 0 else max(0.0, min(1.0, (now_ms - start) / duration))
            row = motion.origin[0] + (motion.destination[0] - motion.origin[0]) * t
            col = motion.origin[1] + (motion.destination[1] - motion.origin[1]) * t
            self._draw_piece_at(canvas, motion.piece, row, col, now_ms, is_jumping=False)
            drawn.add(id(motion.piece))
        for motion in game.active_jumps():
            self._draw_piece_at(canvas, motion.piece, motion.cell[0], motion.cell[1], now_ms, is_jumping=True)
            drawn.add(id(motion.piece))
        return drawn

    def _draw_piece_at(self, canvas, piece, row, col, now_ms, is_jumping):
        state = self._states.setdefault(id(piece), AnimationState(piece, self._loader))
        folder = gfx_config.JUMP_FOLDER if is_jumping else gfx_config.STATE_TO_FOLDER[piece.state.value]
        state.update(folder, now_ms)
        frame = state.current_frame(now_ms)

        cell_px = gfx_config.CELL_PX * self._layout.scale
        x = self._layout.board_origin_x + int(col * cell_px)
        y = self._layout.board_origin_y + int(row * cell_px)
        size = max(1, int(cell_px))
        frame.resize(size, size).draw_on(canvas, x, y)

    @staticmethod
    def _move_duration(origin, destination):
        return max(abs(destination[0]-origin[0]), abs(destination[1]-origin[1])) \
            * logic_config.MOVE_DURATION_PER_CELL