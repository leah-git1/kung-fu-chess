import sys, os as _os
sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "logic"))

from config import Color, RestType  # noqa: F401 — re-exported for client/server use
from enum import Enum


class PlayMode(Enum):
    RANKED = "ranked"
    CASUAL = "casual"
