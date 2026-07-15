"""
Graphics-only configuration.

Kept separate from the root `config.py` on purpose: `config.py` belongs to the
logic layer (timing, rules, board size). Nothing in here is read by logic/,
and nothing in logic/ is read by here except pure data (CELL_SIZE, durations).
This keeps the two layers swappable independently of each other.
"""
import os

import config as logic_config

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GRAPHICS_ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(GRAPHICS_ROOT, "assets")
PIECES_DIR = os.path.join(ASSETS_DIR, "pieces")
BOARD_IMAGE_PATH = os.path.join(ASSETS_DIR, "board", "board.png")
FONT_PATH = os.path.join(ASSETS_DIR, "ui", "font.ttf")

# ---------------------------------------------------------------------------
# Board geometry (derived from the logic layer so the two never disagree)
# ---------------------------------------------------------------------------
CELL_PX = logic_config.CELL_SIZE          # pixel size of one board cell at 1x scale
BOARD_ROWS = 8
BOARD_COLS = 8
BOARD_PX_W = CELL_PX * BOARD_COLS
BOARD_PX_H = CELL_PX * BOARD_ROWS

# ---------------------------------------------------------------------------
# Sidebar (score, moves log, player names) layout
# ---------------------------------------------------------------------------
SIDEBAR_PX_W = 220
TOP_BAR_H = 60          # name + score bar above the board
WINDOW_PX_W = BOARD_PX_W + 2 * SIDEBAR_PX_W
WINDOW_PX_H = BOARD_PX_H + TOP_BAR_H

MOVES_LOG_H = BOARD_PX_H
MOVES_LOG_ROW_H = 22
MOVES_LOG_HEADER_H = 28

# legacy aliases kept so nothing else breaks
PLAYER_NAME_BAR_H = TOP_BAR_H
SCOREBOARD_H = 0

# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------
TARGET_FPS = 30
FRAME_TIME_MS = 1000 // TARGET_FPS
DEFAULT_SPRITE_FPS = 12

# Piece state -> sprite folder name (must match the folder structure under
# assets/pieces/<piece_key>/states/<state_folder>/, per the CTD26 asset repo).
#
# board.piece.PieceState (idle/moving/jumping/short_rest/long_rest/captured)
# now names its members after the exact same folders, so this is a 1:1
# identity map:
#   IDLE -> MOVING -> LONG_REST  -> IDLE   (after a move)
#   IDLE -> JUMPING -> SHORT_REST -> IDLE  (after a jump)
#   - CAPTURED has no dedicated folder in the asset repo, so it reuses
#     "idle" while PieceRenderer fades its alpha out (see with_alpha_scale)
STATE_TO_FOLDER = {
    "idle": "idle",
    "moving": "move",
    "jumping": "jump",
    "short_rest": "short_rest",
    "long_rest": "long_rest",
    "captured": "idle",
}
# Kept as a defensive fallback only: PieceRenderer still has access to the
# live JumpMotion list for interpolating *position* while airborne, and
# uses this in case a JumpMotion is ever active without piece.state
# already reading "jumping" (e.g. mid-refactor). Normal play never needs it.
JUMP_FOLDER = "jump"

# How long a captured piece keeps fading out before PieceRenderer drops it
# for good (ms). Purely a graphics-layer concept - the logic layer already
# removed the piece from the board the instant it was captured.
CAPTURE_FADE_MS = 400

# ---------------------------------------------------------------------------
# Colors (RGBA) - only used for programmatically drawn overlays (highlights,
# selection marker, text). Board/piece pixels come from sprite images.
# ---------------------------------------------------------------------------
COLOR_LIGHT_SQUARE = (237, 214, 176, 255)   # warm light tan
COLOR_DARK_SQUARE  = (184, 111,  55, 255)   # medium warm brown
COLOR_SELECTED = (246, 246, 105, 160)
COLOR_LEGAL_DOT = (20, 20, 20, 120)
COLOR_TEXT = (20, 20, 20, 255)
COLOR_PANEL_BG = (30, 30, 30, 255)
COLOR_PANEL_TEXT = (235, 235, 235, 255)


WINDOW_TITLE = "Kung-Fu Chess"