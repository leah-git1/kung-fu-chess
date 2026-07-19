import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from board.piece import Piece
from board.piece_type import PieceType
from events.event_bus import EventBus
from events.game_events import PieceMovedEvent, PieceCapturedEvent
from events.game_event_source import GameEventSource
from graphics.observers.score_board import ScoreBoard


# ── helpers ───────────────────────────────────────────────────────────────────

def _piece(color, pt_value):
    return Piece(color=color, piece_type=PieceType(pt_value))


class _FakeGame:
    def __init__(self, grid):
        self._grid = grid
        self.game_over = False
        self.winner_color = None

    def snapshot(self):
        return self._grid


# ── EventBus ──────────────────────────────────────────────────────────────────

class TestEventBus:
    def test_subscriber_receives_published_event(self):
        bus = EventBus()
        received = []
        bus.subscribe(PieceMovedEvent, received.append)
        evt = PieceMovedEvent("w", (0, 0), (1, 0))
        bus.publish(evt)
        assert received == [evt]

    def test_multiple_subscribers_all_notified(self):
        bus = EventBus()
        r1, r2 = [], []
        bus.subscribe(PieceMovedEvent, r1.append)
        bus.subscribe(PieceMovedEvent, r2.append)
        evt = PieceMovedEvent("w", (0, 0), (1, 0))
        bus.publish(evt)
        assert r1 == [evt] and r2 == [evt]

    def test_unsubscribe_stops_notifications(self):
        bus = EventBus()
        received = []
        bus.subscribe(PieceMovedEvent, received.append)
        bus.unsubscribe(PieceMovedEvent, received.append)
        bus.publish(PieceMovedEvent("w", (0, 0), (1, 0)))
        assert received == []

    def test_different_event_types_do_not_cross(self):
        bus = EventBus()
        moved, captured = [], []
        bus.subscribe(PieceMovedEvent, moved.append)
        bus.subscribe(PieceCapturedEvent, captured.append)
        bus.publish(PieceMovedEvent("w", (0, 0), (1, 0)))
        assert moved and not captured

    def test_no_subscribers_does_not_raise(self):
        bus = EventBus()
        bus.publish(PieceMovedEvent("w", (0, 0), (1, 0)))


# ── GameEventSource ───────────────────────────────────────────────────────────

class TestGameEventSource:
    def _empty(self):
        return [[Piece.EMPTY] * 8 for _ in range(8)]

    def _make(self):
        bus = EventBus()
        moved, captured = [], []
        bus.subscribe(PieceMovedEvent, moved.append)
        bus.subscribe(PieceCapturedEvent, captured.append)
        src = GameEventSource(bus)
        return src, moved, captured

    def test_first_poll_emits_nothing(self):
        src, moved, captured = self._make()
        grid = self._empty()
        grid[0][0] = _piece("w", "R")
        src.poll(_FakeGame(grid))
        assert not moved and not captured

    def test_move_detected_on_second_poll(self):
        src, moved, _ = self._make()
        p = _piece("w", "R")
        g1 = self._empty(); g1[0][0] = p
        g2 = self._empty(); g2[0][4] = p
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert len(moved) == 1
        assert moved[0].origin == (0, 0)
        assert moved[0].destination == (0, 4)

    def test_capture_detected_when_piece_disappears(self):
        src, _, captured = self._make()
        victim = _piece("b", "P")
        attacker = _piece("w", "R")
        g1 = self._empty(); g1[3][3] = victim
        g2 = self._empty(); g2[3][3] = attacker
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert len(captured) == 1
        assert captured[0].captured_type == "P"
        assert captured[0].at_cell == (3, 3)

    def test_no_event_when_board_unchanged(self):
        src, moved, captured = self._make()
        p = _piece("w", "N")
        grid = self._empty(); grid[2][2] = p
        src.poll(_FakeGame(grid))
        src.poll(_FakeGame(grid))
        assert not moved and not captured

    def test_capture_by_piece_identified(self):
        src, _, captured = self._make()
        victim = _piece("b", "P")
        attacker = _piece("w", "R")
        g1 = self._empty(); g1[4][4] = victim
        g2 = self._empty(); g2[4][4] = attacker
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert captured[0].by_color == "w"


# ── ScoreBoard ────────────────────────────────────────────────────────────────

class TestScoreBoard:
    def _make(self):
        bus = EventBus()
        return ScoreBoard(bus), bus

    def test_initial_scores_are_zero(self):
        sb, _ = self._make()
        assert sb._score == {"w": 0, "b": 0}

    def test_capture_adds_piece_value_to_capturer(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((0, 0), piece_value=9, by_color="w"))
        assert sb._score["w"] == 9
        assert sb._score["b"] == 0

    def test_capture_by_black_adds_to_black(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((1, 1), piece_value=1, by_color="b"))
        assert sb._score["b"] == 1

    def test_capture_without_by_color_does_not_change_score(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((1, 1), piece_value=1, by_color=None))
        assert sb._score == {"w": 0, "b": 0}

    def test_multiple_captures_accumulate(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((0, 0), piece_value=1, by_color="w"))
        bus.publish(PieceCapturedEvent((1, 0), piece_value=5, by_color="w"))
        assert sb._score["w"] == 6

    def test_king_capture_adds_zero(self):
        sb, bus = self._make()
        bus.publish(PieceCapturedEvent((0, 4), piece_value=0, by_color="w"))
        assert sb._score["w"] == 0
