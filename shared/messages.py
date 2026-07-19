"""
One dataclass per message.  Every class has:
  - to_json()   → dict  (ready to pass to json.dumps)
  - from_json() → instance  (classmethod, accepts a dict)

The "type" field is always included in to_json() so the receiver can dispatch
on it without knowing the class in advance.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import shared.message_types as T


# ── helpers ───────────────────────────────────────────────────────────────────

def _base(msg_type: str, data: dict) -> dict:
    return {"type": msg_type, **data}


# ── Handshake ─────────────────────────────────────────────────────────────────

@dataclass
class HelloMsg:
    protocol_version: int

    def to_json(self) -> dict:
        return _base(T.HELLO, {"protocol_version": self.protocol_version})

    @classmethod
    def from_json(cls, d: dict) -> HelloMsg:
        return cls(protocol_version=d["protocol_version"])


# ── Auth ──────────────────────────────────────────────────────────────────────

@dataclass
class LoginMsg:
    name: str
    password: str

    def to_json(self) -> dict:
        return _base(T.LOGIN, {"name": self.name, "password": self.password})

    @classmethod
    def from_json(cls, d: dict) -> LoginMsg:
        return cls(name=d["name"], password=d["password"])


@dataclass
class LoginOkMsg:
    name: str
    elo: int

    def to_json(self) -> dict:
        return _base(T.LOGIN_OK, {"name": self.name, "elo": self.elo})

    @classmethod
    def from_json(cls, d: dict) -> LoginOkMsg:
        return cls(name=d["name"], elo=d["elo"])


@dataclass
class LoginFailMsg:
    reason: str

    def to_json(self) -> dict:
        return _base(T.LOGIN_FAIL, {"reason": self.reason})

    @classmethod
    def from_json(cls, d: dict) -> LoginFailMsg:
        return cls(reason=d["reason"])


# ── Matchmaking ───────────────────────────────────────────────────────────────

@dataclass
class PlayRequestMsg:
    mode: str  # "ranked" | "casual"

    def to_json(self) -> dict:
        return _base(T.PLAY_REQUEST, {"mode": self.mode})

    @classmethod
    def from_json(cls, d: dict) -> PlayRequestMsg:
        return cls(mode=d["mode"])


@dataclass
class MatchFoundMsg:
    room_id: str
    opponent: str
    color: str  # "w" | "b"

    def to_json(self) -> dict:
        return _base(T.MATCH_FOUND, {"room_id": self.room_id, "opponent": self.opponent, "color": self.color})

    @classmethod
    def from_json(cls, d: dict) -> MatchFoundMsg:
        return cls(room_id=d["room_id"], opponent=d["opponent"], color=d["color"])


@dataclass
class SearchTimeoutMsg:
    def to_json(self) -> dict:
        return _base(T.SEARCH_TIMEOUT, {})

    @classmethod
    def from_json(cls, d: dict) -> SearchTimeoutMsg:
        return cls()


# ── Room ──────────────────────────────────────────────────────────────────────

@dataclass
class RoomCreateMsg:
    room_id: str

    def to_json(self) -> dict:
        return _base(T.ROOM_CREATE, {"room_id": self.room_id})

    @classmethod
    def from_json(cls, d: dict) -> RoomCreateMsg:
        return cls(room_id=d["room_id"])


@dataclass
class RoomJoinMsg:
    room_id: str

    def to_json(self) -> dict:
        return _base(T.ROOM_JOIN, {"room_id": self.room_id})

    @classmethod
    def from_json(cls, d: dict) -> RoomJoinMsg:
        return cls(room_id=d["room_id"])


@dataclass
class RoomStateMsg:
    room_id: str
    players: list[str]
    started: bool
    color: str = ""   # assigned color for the receiving player ("w" or "b")

    def to_json(self) -> dict:
        return _base(T.ROOM_STATE, {"room_id": self.room_id, "players": self.players,
                                    "started": self.started, "color": self.color})

    @classmethod
    def from_json(cls, d: dict) -> RoomStateMsg:
        return cls(room_id=d["room_id"], players=d["players"],
                   started=d["started"], color=d.get("color", ""))


# ── In-game ───────────────────────────────────────────────────────────────────

@dataclass
class StartMsg:
    def to_json(self) -> dict:
        return _base(T.START, {})

    @classmethod
    def from_json(cls, d: dict) -> StartMsg:
        return cls()


@dataclass
class MoveMsg:
    from_cell: list[int]   # [row, col]
    to_cell: list[int]

    def to_json(self) -> dict:
        return _base(T.MOVE, {"from": self.from_cell, "to": self.to_cell})

    @classmethod
    def from_json(cls, d: dict) -> MoveMsg:
        return cls(from_cell=d["from"], to_cell=d["to"])


@dataclass
class JumpMsg:
    cell: list[int]

    def to_json(self) -> dict:
        return _base(T.JUMP, {"cell": self.cell})

    @classmethod
    def from_json(cls, d: dict) -> JumpMsg:
        return cls(cell=d["cell"])


@dataclass
class StateUpdateMsg:
    board: list
    time_ms: int
    motions: dict = None

    def to_json(self) -> dict:
        return _base(T.STATE_UPDATE, {"board": self.board, "time_ms": self.time_ms,
                                      "motions": self.motions or {"moves": [], "jumps": []}})

    @classmethod
    def from_json(cls, d: dict) -> StateUpdateMsg:
        return cls(board=d["board"], time_ms=d["time_ms"],
                   motions=d.get("motions", {"moves": [], "jumps": []}))


@dataclass
class MoveAckMsg:
    from_cell: list[int]
    to_cell: list[int]
    time_ms: int

    def to_json(self) -> dict:
        return _base(T.MOVE_ACK, {"from": self.from_cell, "to": self.to_cell, "time_ms": self.time_ms})

    @classmethod
    def from_json(cls, d: dict) -> MoveAckMsg:
        return cls(from_cell=d["from"], to_cell=d["to"], time_ms=d["time_ms"])


@dataclass
class JumpAckMsg:
    cell: list[int]
    time_ms: int

    def to_json(self) -> dict:
        return _base(T.JUMP_ACK, {"cell": self.cell, "time_ms": self.time_ms})

    @classmethod
    def from_json(cls, d: dict) -> JumpAckMsg:
        return cls(cell=d["cell"], time_ms=d["time_ms"])


@dataclass
class GameOverMsg:
    winner: str   # "w" | "b"
    reason: str

    def to_json(self) -> dict:
        return _base(T.GAME_OVER, {"winner": self.winner, "reason": self.reason})

    @classmethod
    def from_json(cls, d: dict) -> GameOverMsg:
        return cls(winner=d["winner"], reason=d["reason"])


@dataclass
class ResignMsg:
    def to_json(self) -> dict:
        return _base(T.RESIGN, {})

    @classmethod
    def from_json(cls, d: dict) -> ResignMsg:
        return cls()


# ── Events / logging ──────────────────────────────────────────────────────────

@dataclass
class LogEventMsg:
    text: str
    time_ms: int

    def to_json(self) -> dict:
        return _base(T.LOG_EVENT, {"text": self.text, "time_ms": self.time_ms})

    @classmethod
    def from_json(cls, d: dict) -> LogEventMsg:
        return cls(text=d["text"], time_ms=d["time_ms"])


# ── Errors / connection ───────────────────────────────────────────────────────

@dataclass
class ErrorMsg:
    reason: str

    def to_json(self) -> dict:
        return _base(T.ERROR, {"reason": self.reason})

    @classmethod
    def from_json(cls, d: dict) -> ErrorMsg:
        return cls(reason=d["reason"])


@dataclass
class OpponentDisconnectedMsg:
    grace_s: int

    def to_json(self) -> dict:
        return _base(T.OPPONENT_DISCONNECTED, {"grace_s": self.grace_s})

    @classmethod
    def from_json(cls, d: dict) -> OpponentDisconnectedMsg:
        return cls(grace_s=d["grace_s"])


# ── Dispatcher ────────────────────────────────────────────────────────────────
# Maps type string → from_json callable so receivers can do:
#   msg = REGISTRY[d["type"]].from_json(d)

REGISTRY: dict[str, type] = {
    T.HELLO:                  HelloMsg,
    T.LOGIN:                  LoginMsg,
    T.LOGIN_OK:               LoginOkMsg,
    T.LOGIN_FAIL:             LoginFailMsg,
    T.PLAY_REQUEST:           PlayRequestMsg,
    T.MATCH_FOUND:            MatchFoundMsg,
    T.SEARCH_TIMEOUT:         SearchTimeoutMsg,
    T.ROOM_CREATE:            RoomCreateMsg,
    T.ROOM_JOIN:              RoomJoinMsg,
    T.ROOM_STATE:             RoomStateMsg,
    T.START:                  StartMsg,
    T.MOVE:                   MoveMsg,
    T.JUMP:                   JumpMsg,
    T.STATE_UPDATE:           StateUpdateMsg,
    T.MOVE_ACK:               MoveAckMsg,
    T.JUMP_ACK:               JumpAckMsg,
    T.GAME_OVER:              GameOverMsg,
    T.RESIGN:                 ResignMsg,
    T.LOG_EVENT:              LogEventMsg,
    T.ERROR:                  ErrorMsg,
    T.OPPONENT_DISCONNECTED:  OpponentDisconnectedMsg,
}


def parse(d: dict):
    """Deserialise a raw dict (from json.loads) into the correct message dataclass."""
    cls = REGISTRY.get(d.get("type"))
    if cls is None:
        raise ValueError(f"Unknown message type: {d.get('type')!r}")
    return cls.from_json(d)
