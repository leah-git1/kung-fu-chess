import os
import config as logic_config   # the ONLY thing graphics borrows from logic/config.py

GRAPHICS_ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(GRAPHICS_ROOT, "assets")
PIECES_DIR = os.path.join(ASSETS_DIR, "pieces")
BOARD_IMAGE_PATH = os.path.join(ASSETS_DIR, "board", "board.png")

CELL_PX = logic_config.CELL_SIZE     # keep board geometry in one place, never duplicate
BOARD_ROWS, BOARD_COLS = 8, 8
BOARD_PX_W = CELL_PX * BOARD_COLS
BOARD_PX_H = CELL_PX * BOARD_ROWS

SIDEBAR_PX_W = 320
WINDOW_PX_W = BOARD_PX_W + SIDEBAR_PX_W
WINDOW_PX_H = BOARD_PX_H

PLAYER_NAME_BAR_H = 60
SCOREBOARD_H = 90
MOVES_LOG_H = WINDOW_PX_H - PLAYER_NAME_BAR_H - SCOREBOARD_H

TARGET_FPS = 30
FRAME_TIME_MS = 1000 // TARGET_FPS
DEFAULT_SPRITE_FPS = 12

# Piece.state.value -> sprite folder name under assets/pieces/<KEY>/states/
# Your PieceState only has idle/moving/cooldown/captured today (no separate
# jump state) - see the note in Milestone 6 about how "is this piece
# currently airborne" is answered a different way, not through this map.
STATE_TO_FOLDER = {
    "idle": "idle",
    "moving": "move",
    "cooldown": "long_rest",
    "captured": "idle",     # captured pieces fade out from their last idle frame
}
JUMP_FOLDER = "jump"

CAPTURE_FADE_MS = 400

COLOR_SELECTED = (246, 246, 105, 160)
COLOR_LEGAL_DOT = (20, 20, 20, 120)
COLOR_PANEL_BG = (30, 30, 30, 255)
COLOR_PANEL_TEXT = (235, 235, 235, 255)