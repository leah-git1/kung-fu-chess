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
