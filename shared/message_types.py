# Every "type" field value that can appear on the wire.
# Import these instead of using raw strings so typos are caught at import time.

# ── Handshake ────────────────────────────────────────────────────────────────
HELLO           = "hello"           # C→S  first packet after TCP connect

# ── Auth ─────────────────────────────────────────────────────────────────────
LOGIN           = "login"           # C→S  {"name": str, "password": str}
LOGIN_OK        = "login_ok"        # S→C  {"name": str, "elo": int}
LOGIN_FAIL      = "login_fail"      # S→C  {"reason": str}

# ── Matchmaking ───────────────────────────────────────────────────────────────
PLAY_REQUEST    = "play_request"    # C→S  {"mode": "ranked"|"casual"}
MATCH_FOUND     = "match_found"     # S→C  {"room_id": str, "opponent": str, "color": "w"|"b"}
SEARCH_TIMEOUT  = "search_timeout"  # S→C  {}

# ── Room (private/custom games) ───────────────────────────────────────────────
ROOM_CREATE     = "room_create"     # C→S  {"room_id": str}
ROOM_JOIN       = "room_join"       # C→S  {"room_id": str}
ROOM_STATE      = "room_state"      # S→C  {"room_id": str, "players": list[str], "started": bool}

# ── In-game ───────────────────────────────────────────────────────────────────
START           = "start"           # C→S  {} (ready signal)
MOVE            = "move"            # C→S  {"from": [r,c], "to": [r,c]}
JUMP            = "jump"            # C→S  {"cell": [r,c]}
STATE_UPDATE    = "state_update"    # S→C  {"board": list, "time_ms": int}
MOVE_ACK        = "move_ack"        # S→C  {"from": [r,c], "to": [r,c], "time_ms": int}
JUMP_ACK        = "jump_ack"        # S→C  {"cell": [r,c], "time_ms": int}
GAME_OVER       = "game_over"       # S→C  {"winner": "w"|"b", "reason": str}
RESIGN          = "resign"          # C→S  {}

# ── Events / logging ─────────────────────────────────────────────────────────
LOG_EVENT       = "log_event"       # S→C  {"text": str, "time_ms": int}

# ── Errors / connection ───────────────────────────────────────────────────────
ERROR                   = "error"               # S→C  {"reason": str}
OPPONENT_DISCONNECTED   = "opponent_disconnected"  # S→C  {"grace_s": int}
