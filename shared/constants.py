# ── Network ───────────────────────────────────────────────────────────────────
DEFAULT_PORT        = 5555
PROTOCOL_VERSION    = 1

# ── Server tick ───────────────────────────────────────────────────────────────
TICK_RATE_MS        = 50        # server advances game time every 50 ms

# ── Matchmaking ───────────────────────────────────────────────────────────────
ELO_RANGE           = 100       # max ELO difference for a ranked match
MATCH_TIMEOUT_S     = 60        # give up searching after this many seconds

# ── Connection ────────────────────────────────────────────────────────────────
DISCONNECT_GRACE_S  = 20        # seconds opponent has to reconnect before forfeit

# ── Game timing (shared between server logic and client animation) ─────────────
MOVE_DURATION_PER_CELL = 600    # ms per board cell travelled
JUMP_DURATION          = 1000   # ms a piece is airborne during a jump
LONG_REST_DURATION     = 2000   # ms cooldown after a move
SHORT_REST_DURATION    = 1000   # ms cooldown after a jump
