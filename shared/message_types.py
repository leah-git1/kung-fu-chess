# Every "type" field value that can appear on the wire.
# Import these instead of using raw strings so typos are caught at import time.

# ── Handshake ────────────────────────────────────────────────────────────────
HELLO           = "hello"           

# ── Auth ─────────────────────────────────────────────────────────────────────
LOGIN           = "login"           
LOGIN_OK        = "login_ok"        
LOGIN_FAIL      = "login_fail"      

# ── Matchmaking ───────────────────────────────────────────────────────────────
PLAY_REQUEST    = "play_request"    
MATCH_FOUND     = "match_found"     
SEARCH_TIMEOUT  = "search_timeout"  

# ── Room (private/custom games) ───────────────────────────────────────────────
ROOM_CREATE     = "room_create"     
ROOM_JOIN       = "room_join"       
ROOM_STATE      = "room_state"      

# ── In-game ───────────────────────────────────────────────────────────────────
START           = "start"           
MOVE            = "move"            
JUMP            = "jump"            
STATE_UPDATE    = "state_update"    
MOVE_ACK        = "move_ack"        
JUMP_ACK        = "jump_ack"        
GAME_OVER       = "game_over"       
RESIGN          = "resign"          

# ── Events / logging ─────────────────────────────────────────────────────────
LOG_EVENT       = "log_event"       

# ── Errors / connection ───────────────────────────────────────────────────────
ERROR                   = "error"               
OPPONENT_DISCONNECTED   = "opponent_disconnected"  
