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
CELL_PX = logic_config.CELL_SIZE          
BOARD_ROWS = 8
BOARD_COLS = 8
BOARD_PX_W = CELL_PX * BOARD_COLS
BOARD_PX_H = CELL_PX * BOARD_ROWS

# ---------------------------------------------------------------------------
# Sidebar (score, moves log, player names) layout
# ---------------------------------------------------------------------------
SIDEBAR_PX_W = 220
SIDEBAR_MARGIN = 18          
BOARD_SIDE_GAP = 24          
BOARD_LABEL_MARGIN = 26      
BOARD_DISPLAY_SCALE = 0.80   
TOP_BAR_H = 80               
TOP_NAME_H = 44              
TOP_SCORE_H = 36            
WINDOW_PX_W = BOARD_PX_W + 2 * SIDEBAR_PX_W + 2 * BOARD_SIDE_GAP + 2 * SIDEBAR_MARGIN + 160
WINDOW_PX_H = BOARD_PX_H + TOP_BAR_H + 80

MOVES_LOG_H = BOARD_PX_H
MOVES_LOG_ROW_H = 28
MOVES_LOG_HEADER_H = 34

# legacy aliases kept so nothing else breaks
PLAYER_NAME_BAR_H = TOP_BAR_H
SCOREBOARD_H = 0

# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------
TARGET_FPS = 30
FRAME_TIME_MS = 1000 // TARGET_FPS
DEFAULT_SPRITE_FPS = 12


STATE_TO_FOLDER = {
    "idle": "idle",
    "moving": "move",
    "jumping": "jump",
    "short_rest": "short_rest",
    "long_rest": "long_rest",
    "captured": "idle",
}
JUMP_FOLDER = "jump"

# ---------------------------------------------------------------------------
# Colors (RGBA) - only used for programmatically drawn overlays (highlights,
# selection marker, text). Board/piece pixels come from sprite images.
# ---------------------------------------------------------------------------
COLOR_LIGHT_SQUARE = (200, 185, 155, 255)  
COLOR_DARK_SQUARE  = (100,  60,  20, 255)  
COLOR_SELECTED = (246, 246, 105, 160)
COLOR_LEGAL_DOT = (20, 20, 20, 120)
COLOR_TEXT = (220, 220, 220, 255)
COLOR_PANEL_BG    = ( 30,  30,  30, 255)   
COLOR_PANEL_TEXT  = (220, 220, 220, 255)   
COLOR_PANEL_HEADER= ( 45,  45,  45, 255)   
COLOR_PANEL_LINE  = ( 70,  70,  70, 255)   
COLOR_GOLD        = ( 30, 190, 210, 255)   

# Cooldown overlay drawn behind a piece during LONG_REST / SHORT_REST
COOLDOWN_BAR_COLOR       = ( 30, 210, 240, 160)  
COOLDOWN_BAR_COLOR_SHORT = (180,  80, 255, 160)  
MOVE_DURATION_PER_CELL = logic_config.MOVE_DURATION_PER_CELL


WINDOW_TITLE = "Kung-Fu Chess"