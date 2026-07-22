# -- Game over reasons --------------------------------------------------------
class GameOverReason:
    KING_CAPTURED         = "king captured"
    OPPONENT_DISCONNECTED = "opponent disconnected"


# -- Room IDs -----------------------------------------------------------------
class RoomId:
    MAIN = "main"



# -- Network ------------------------------------------------------------------
DEFAULT_PORT             = 5555
PROTOCOL_VERSION         = 1

# -- Server tick --------------------------------------------------------------
TICK_RATE_MS             = 50    # server advances game time every 50 ms
STATE_UPDATE_INTERVAL_MS = 200   # how often STATE_UPDATE is broadcast to clients

# -- Matchmaking --------------------------------------------------------------
ELO_RANGE                = 100   # max ELO difference for a ranked match
MATCH_TIMEOUT_S          = 60    # give up searching after this many seconds
PLAY_REQUEST_TIMEOUT_S   = 300   # seconds to wait for PlayRequestMsg after login

# -- ELO ----------------------------------------------------------------------
ELO_K_FACTOR             = 32    # sensitivity of rating changes per game
ELO_SCALE                = 400   # ELO scale factor (standard)
ELO_DEFAULT              = 1200  # starting rating for new players

# -- Connection ---------------------------------------------------------------
DISCONNECT_GRACE_S       = 20    # seconds before forfeit on disconnect

# -- Game timing (shared between server logic and client animation) -----------
MOVE_DURATION_PER_CELL   = 600   # ms per board cell travelled
JUMP_DURATION            = 1000  # ms a piece is airborne during a jump
LONG_REST_DURATION       = 2000  # ms cooldown after a move
SHORT_REST_DURATION      = 1000  # ms cooldown after a jump
