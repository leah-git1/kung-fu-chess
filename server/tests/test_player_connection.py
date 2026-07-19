"""
Tests for server/session/player_connection.py
"""
import asyncio
import json
import pytest
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

from server.session.player_connection import PlayerConnection
from shared.messages import ErrorMsg


class _FakeWebSocket:
    """Minimal websocket stub that records sent payloads."""
    def __init__(self):
        self.sent = []

    async def send(self, data):
        self.sent.append(data)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_player_connection_stores_attributes():
    ws = _FakeWebSocket()
    conn = PlayerConnection(ws, color="w", name="alice")
    assert conn.color == "w"
    assert conn.name == "alice"
    assert conn.websocket is ws


def test_send_serialises_message():
    ws = _FakeWebSocket()
    conn = PlayerConnection(ws, color="w", name="alice")
    _run(conn.send(ErrorMsg(reason="oops")))
    assert len(ws.sent) == 1
    d = json.loads(ws.sent[0])
    assert d["type"] == "error"
    assert d["reason"] == "oops"


def test_send_raw_sends_dict_as_json():
    ws = _FakeWebSocket()
    conn = PlayerConnection(ws, color="b", name="bob")
    _run(conn.send_raw({"type": "ping"}))
    assert json.loads(ws.sent[0]) == {"type": "ping"}


def test_multiple_sends_are_ordered():
    ws = _FakeWebSocket()
    conn = PlayerConnection(ws, color="w", name="alice")
    _run(conn.send(ErrorMsg(reason="first")))
    _run(conn.send(ErrorMsg(reason="second")))
    assert json.loads(ws.sent[0])["reason"] == "first"
    assert json.loads(ws.sent[1])["reason"] == "second"
