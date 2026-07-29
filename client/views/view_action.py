from enum import Enum, auto


class ViewAction(Enum):
    GOTO_HOME           = auto()
    GOTO_LOGIN          = auto()
    GOTO_CONNECTING     = auto()
    GOTO_ROOM_DIALOG    = auto()
    GOTO_ROOM_WAITING   = auto()
    GOTO_MATCHMAKING    = auto()
    GOTO_GAME           = auto()
    GOTO_GAME_OVER      = auto()
    QUIT                = auto()
