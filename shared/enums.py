from enum import Enum


class Color(Enum):
    WHITE     = "w"
    BLACK     = "b"
    SPECTATOR = ""


class RestType(Enum):
    LONG  = "long"
    SHORT = "short"


class PlayMode(Enum):
    RANKED = "ranked"
    CASUAL = "casual"
