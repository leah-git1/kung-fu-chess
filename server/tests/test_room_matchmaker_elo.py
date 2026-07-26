"""
Tests for server/session/room.py, server/room_manager.py,
server/matchmaker.py, and server/rating/elo.py
"""
import asyncio
import pytest
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

from unittest.mock import MagicMock
from server.session.room import Room
from server.room_manager import RoomManager
from server.matchmaker import Matchmaker
from server.rating.elo import calculate_elo
from server.session.player_connection import PlayerConnection
from shared.enums import Color


# ── helpers ───────────────────────────────────────────────────────────────────

def _conn(name="alice", rating=1200, color=Color.WHITE):
    ws = MagicMock()
    conn = PlayerConnection(ws, color=color, name=name, rating=rating)
    return conn


# ══ Room ══════════════════════════════════════════════════════════════════════

def test_room_initial_state():
    white = _conn("alice")
    room = Room("ABC", white)
    assert room.room_id == "ABC"
    assert room.white is white
    assert room.black is None
    assert room.spectators == []
    assert room.session is None


def test_room_player_names_one_player():
    room = Room("X", _conn("alice"))
    assert room.player_names == ["alice"]


def test_room_player_names_two_players():
    room = Room("X", _conn("alice"))
    room.black = _conn("bob")
    assert room.player_names == ["alice", "bob"]


def test_room_add_second_player_returns_black():
    room = Room("X", _conn("alice"))
    role = room.add(_conn("bob"))
    assert role == Color.BLACK


def test_room_add_second_player_sets_black():
    bob = _conn("bob")
    room = Room("X", _conn("alice"))
    room.add(bob)
    assert room.black is bob


def test_room_add_second_player_sets_ready_event():
    room = Room("X", _conn("alice"))
    room.add(_conn("bob"))
    assert room.ready.is_set()


def test_room_add_third_player_returns_spectator():
    room = Room("X", _conn("alice"))
    room.add(_conn("bob"))
    role = room.add(_conn("carol"))
    assert role == Color.SPECTATOR


def test_room_add_spectator_appended():
    carol = _conn("carol")
    room = Room("X", _conn("alice"))
    room.add(_conn("bob"))
    room.add(carol)
    assert carol in room.spectators


def test_room_ready_not_set_initially():
    room = Room("X", _conn("alice"))
    assert not room.ready.is_set()


# ══ RoomManager ═══════════════════════════════════════════════════════════════

def test_room_manager_create_returns_room():
    rm = RoomManager()
    room = rm.create(_conn("alice"))
    assert isinstance(room, Room)


def test_room_manager_create_unique_ids():
    rm = RoomManager()
    ids = {rm.create(_conn()).room_id for _ in range(20)}
    assert len(ids) == 20


def test_room_manager_join_returns_room_and_color():
    rm = RoomManager()
    room = rm.create(_conn("alice"))
    result = rm.join(room.room_id, _conn("bob"))
    assert result is not None
    r, color = result
    assert r is room
    assert color == Color.BLACK


def test_room_manager_join_case_insensitive():
    rm = RoomManager()
    room = rm.create(_conn("alice"))
    result = rm.join(room.room_id.lower(), _conn("bob"))
    assert result is not None


def test_room_manager_join_unknown_id_returns_none():
    rm = RoomManager()
    assert rm.join("ZZZZZZ", _conn()) is None


def test_room_manager_remove_deletes_room():
    rm = RoomManager()
    room = rm.create(_conn())
    rm.remove(room.room_id)
    assert rm.join(room.room_id, _conn()) is None


def test_room_manager_remove_nonexistent_does_not_raise():
    rm = RoomManager()
    rm.remove("DOESNOTEXIST")  # should not raise


# ══ Matchmaker ════════════════════════════════════════════════════════════════

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_matchmaker_add_returns_future():
    mm = Matchmaker()
    fut = mm.add(_conn())
    assert isinstance(fut, asyncio.Future)


def test_matchmaker_match_pairs_compatible_players():
    mm = Matchmaker()
    a = _conn("alice", rating=1200)
    b = _conn("bob",   rating=1200)
    mm.add(a)
    mm.add(b)
    pairs = mm.match()
    assert len(pairs) == 1
    assert set(pairs[0]) == {a, b}


def test_matchmaker_match_resolves_futures():
    mm = Matchmaker()
    a = _conn("alice", rating=1200)
    b = _conn("bob",   rating=1200)
    fa = mm.add(a)
    fb = mm.add(b)
    mm.match()
    assert fa.done() and fb.done()
    assert fa.result() is b
    assert fb.result() is a


def test_matchmaker_match_does_not_pair_incompatible_elo():
    mm = Matchmaker()
    mm.add(_conn("alice", rating=1200))
    mm.add(_conn("bob",   rating=9999))
    pairs = mm.match()
    assert pairs == []


def test_matchmaker_remove_cancels_future():
    mm = Matchmaker()
    a = _conn("alice")
    fut = mm.add(a)
    mm.remove(a)
    assert fut.cancelled()


def test_matchmaker_remove_prevents_matching():
    mm = Matchmaker()
    a = _conn("alice", rating=1200)
    b = _conn("bob",   rating=1200)
    mm.add(a)
    mm.add(b)
    mm.remove(a)
    pairs = mm.match()
    assert pairs == []


def test_matchmaker_queue_cleared_after_match():
    mm = Matchmaker()
    mm.add(_conn("alice", rating=1200))
    mm.add(_conn("bob",   rating=1200))
    mm.match()
    assert mm._queue == []


def test_matchmaker_three_players_one_pair_one_waiting():
    mm = Matchmaker()
    mm.add(_conn("a", rating=1200))
    mm.add(_conn("b", rating=1200))
    mm.add(_conn("c", rating=1200))
    pairs = mm.match()
    assert len(pairs) == 1
    assert len(mm._queue) == 1


# ══ ELO ═══════════════════════════════════════════════════════════════════════

def test_elo_winner_gains_points():
    w, l = calculate_elo(1200, 1200)
    assert w > 1200


def test_elo_loser_loses_points():
    w, l = calculate_elo(1200, 1200)
    assert l < 1200


def test_elo_sum_preserved():
    w, l = calculate_elo(1200, 1200)
    assert w + l == 2400


def test_elo_upset_winner_gains_more():
    w_upset, _ = calculate_elo(1000, 1400)
    w_expected, _ = calculate_elo(1400, 1000)
    assert w_upset - 1000 > w_expected - 1400


def test_elo_equal_ratings_symmetric():
    w, l = calculate_elo(1500, 1500)
    assert w - 1500 == 1500 - l


def test_elo_custom_k_factor():
    w1, _ = calculate_elo(1200, 1200, k=16)
    w2, _ = calculate_elo(1200, 1200, k=32)
    assert w2 - 1200 > w1 - 1200
