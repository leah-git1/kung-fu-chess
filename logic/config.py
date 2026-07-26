from enum import Enum


class Color(Enum):
    WHITE     = "w"
    BLACK     = "b"
    SPECTATOR = ""


class RestType(Enum):
    LONG  = "long"
    SHORT = "short"


# ============================================================================
# Cell & Piece Representation
# ============================================================================
EMPTY_CELL = "."


# ============================================================================
# Animation & Timing
# ============================================================================
CELL_SIZE = 100
MOVE_DURATION_PER_CELL = 600
JUMP_DURATION = 1000


# ============================================================================
# Input/Output Headers
# ============================================================================
BOARD_HEADER = "Board:"
COMMANDS_HEADER = "Commands:"


# ============================================================================
# Piece Configuration
# ============================================================================
FORWARD_DIRECTION = {Color.WHITE: -1, Color.BLACK: 1}

PROMOTION_RULES = {Color.WHITE: 0, Color.BLACK: -1}  # Row index; -1 = board.rows - 1

ROYAL_PIECE_TYPES = {"K"}

PROMOTION_TARGETS = {"P": "Q"}  # Pawn promotes to Queen

PIECE_VALUES = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "P": 1,
}

KING_MAX_DISTANCE = 1

KNIGHT_MOVE_OFFSETS = frozenset({
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
})

SHORT_REST_DURATION = 1000   # rest after a jump
LONG_REST_DURATION  = 2000   # rest after a move
