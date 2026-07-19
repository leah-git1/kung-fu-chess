import pytest
from shared.messages import (
    parse, HelloMsg, LoginMsg, LoginOkMsg, LoginFailMsg,
    MoveMsg, JumpMsg, StateUpdateMsg, MoveAckMsg, JumpAckMsg,
    GameOverMsg, ErrorMsg, RoomStateMsg, ResignMsg,
    PlayRequestMsg, MatchFoundMsg, SearchTimeoutMsg,
    RoomCreateMsg, RoomJoinMsg, StartMsg, LogEventMsg,
    OpponentDisconnectedMsg,
)
import shared.message_types as T


# ── round-trip helpers ────────────────────────────────────────────────────────

def rt(msg):
    """Serialise then deserialise; return the reconstructed message."""
    return parse(msg.to_json())


# ── HelloMsg ──────────────────────────────────────────────────────────────────

def test_hello_type_field():
    assert HelloMsg(1).to_json()["type"] == T.HELLO


def test_hello_round_trip():
    assert rt(HelloMsg(protocol_version=3)).protocol_version == 3


# ── LoginMsg ──────────────────────────────────────────────────────────────────

def test_login_round_trip():
    msg = rt(LoginMsg(name="alice", password="secret"))
    assert msg.name == "alice"
    assert msg.password == "secret"


def test_login_ok_round_trip():
    msg = rt(LoginOkMsg(name="alice", elo=1200))
    assert msg.name == "alice" and msg.elo == 1200


def test_login_fail_round_trip():
    assert rt(LoginFailMsg(reason="bad password")).reason == "bad password"


# ── Matchmaking ───────────────────────────────────────────────────────────────

def test_play_request_round_trip():
    assert rt(PlayRequestMsg(mode="ranked")).mode == "ranked"


def test_match_found_round_trip():
    msg = rt(MatchFoundMsg(room_id="r1", opponent="bob", color="b"))
    assert msg.room_id == "r1" and msg.opponent == "bob" and msg.color == "b"


def test_search_timeout_round_trip():
    assert isinstance(rt(SearchTimeoutMsg()), SearchTimeoutMsg)


# ── Room ──────────────────────────────────────────────────────────────────────

def test_room_create_round_trip():
    assert rt(RoomCreateMsg(room_id="abc")).room_id == "abc"


def test_room_join_round_trip():
    assert rt(RoomJoinMsg(room_id="abc")).room_id == "abc"


def test_room_state_round_trip():
    msg = rt(RoomStateMsg(room_id="r1", players=["a", "b"], started=True, color="w"))
    assert msg.started is True and msg.color == "w"


def test_room_state_color_defaults_to_empty():
    d = {"type": T.ROOM_STATE, "room_id": "r", "players": [], "started": False}
    assert RoomStateMsg.from_json(d).color == ""


# ── In-game ───────────────────────────────────────────────────────────────────

def test_start_round_trip():
    assert isinstance(rt(StartMsg()), StartMsg)


def test_move_msg_round_trip():
    msg = rt(MoveMsg(from_cell=[1, 2], to_cell=[3, 4]))
    assert msg.from_cell == [1, 2] and msg.to_cell == [3, 4]


def test_move_msg_json_keys():
    d = MoveMsg(from_cell=[0, 0], to_cell=[1, 1]).to_json()
    assert "from" in d and "to" in d


def test_jump_msg_round_trip():
    assert rt(JumpMsg(cell=[4, 5])).cell == [4, 5]


def test_state_update_round_trip():
    motions = {"moves": [], "jumps": []}
    msg = rt(StateUpdateMsg(board=[[None]], time_ms=500, motions=motions))
    assert msg.time_ms == 500 and msg.motions == motions


def test_state_update_motions_defaults():
    d = {"type": T.STATE_UPDATE, "board": [], "time_ms": 0}
    msg = StateUpdateMsg.from_json(d)
    assert msg.motions == {"moves": [], "jumps": []}


def test_state_update_to_json_fills_empty_motions():
    d = StateUpdateMsg(board=[], time_ms=0, motions=None).to_json()
    assert d["motions"] == {"moves": [], "jumps": []}


def test_move_ack_round_trip():
    msg = rt(MoveAckMsg(from_cell=[0, 0], to_cell=[0, 7], time_ms=100))
    assert msg.from_cell == [0, 0] and msg.time_ms == 100


def test_jump_ack_round_trip():
    msg = rt(JumpAckMsg(cell=[3, 3], time_ms=200))
    assert msg.cell == [3, 3] and msg.time_ms == 200


def test_game_over_round_trip():
    msg = rt(GameOverMsg(winner="b", reason="king captured"))
    assert msg.winner == "b" and msg.reason == "king captured"


def test_resign_round_trip():
    assert isinstance(rt(ResignMsg()), ResignMsg)


# ── Events / errors ───────────────────────────────────────────────────────────

def test_log_event_round_trip():
    msg = rt(LogEventMsg(text="wR moved", time_ms=42))
    assert msg.text == "wR moved" and msg.time_ms == 42


def test_error_round_trip():
    assert rt(ErrorMsg(reason="not your piece")).reason == "not your piece"


def test_opponent_disconnected_round_trip():
    assert rt(OpponentDisconnectedMsg(grace_s=20)).grace_s == 20


# ── parse dispatcher ──────────────────────────────────────────────────────────

def test_parse_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown message type"):
        parse({"type": "does_not_exist"})


def test_parse_missing_type_raises():
    with pytest.raises(ValueError):
        parse({})


def test_every_message_type_is_in_registry():
    from shared.messages import REGISTRY
    for attr in vars(T):
        if attr.startswith("_"):
            continue
        val = getattr(T, attr)
        assert val in REGISTRY, f"{attr!r} = {val!r} missing from REGISTRY"
