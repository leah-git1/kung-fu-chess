# ============================================================================
# Cell & Piece Representation
# ============================================================================
EMPTY_CELL = "."


# ============================================================================
# Animation & Timing
# ============================================================================
CELL_SIZE = 100
MOVE_DURATION_PER_CELL = 1000
JUMP_DURATION = 1000


# ============================================================================
# Input/Output Headers
# ============================================================================
BOARD_HEADER = "Board:"
COMMANDS_HEADER = "Commands:"


# ============================================================================
# Piece Configuration
# ============================================================================
# Piece colors and their movement directions
FORWARD_DIRECTION = {"w": -1, "b": 1}

# Promotion rules: which piece type promotes to which
PROMOTION_RULES = {"w": 0, "b": -1}  # Row index; -1 = board.rows - 1

# Piece types that grant royal status (e.g., kings)
ROYAL_PIECE_TYPES = {"K"}  # Only kings are royal

# Piece promotion mappings (source -> target)
PROMOTION_TARGETS = {"P": "Q"}  # Pawn promotes to Queen


# ============================================================================
# Movement Rules & Constraints
# ============================================================================
# King movement constraint
KING_MAX_DISTANCE = 1

# Knight movement offsets
KNIGHT_MOVE_OFFSETS = frozenset({
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
})

