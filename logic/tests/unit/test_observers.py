import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from board.piece import Piece
from board.piece_type import PieceType
from graphics.observers.game_events import (
    GameSubject, GameObserver, PieceMovedEvent, PieceCapturedEvent,
)
from graphics.observers.game_event_source import GameEventSource
from graphics.observers.score_board import ScoreBoard


# ── helpers ───────────────────────────────────────────────────────────────────

def _piece(color, pt_value):
    return Piece(color=color, piece_type=PieceType(pt_value))


class _RecordingObserver(GameObserver):
    def __init__(self):
        self.moved = []
        self.captured = []

    def on_piece_moved(self, event):
        self.moved.append(event)

    def on_piece_captured(self, event):
        self.captured.append(event)


class _FakeGame:
    def __init__(self, grid):
        self._grid = grid

    def snapshot(self):
        return self._grid


# ── GameSubject ───────────────────────────────────────────────────────────────

class TestGameSubject:
    def test_notify_piece_moved_reaches_observer(self):
        subj = GameSubject()
        obs = _RecordingObserver()
        subj.add_observer(obs)
        p = _piece("w", "P")
        evt = PieceMovedEvent(p, (1, 0), (2, 0))
        subj.notify_piece_moved(evt)
        assert obs.moved == [evt]

    def test_notify_piece_captured_reaches_observer(self):
        subj = GameSubject()
        obs = _RecordingObserver()
        subj.add_observer(obs)
        p = _piece("b", "Q")
        evt = PieceCapturedEvent(p, (3, 3))
        subj.notify_piece_captured(evt)
        assert obs.captured == [evt]

    def test_multiple_observers_all_notified(self):
        subj = GameSubject()
        obs1, obs2 = _RecordingObserver(), _RecordingObserver()
        subj.add_observer(obs1)
        subj.add_observer(obs2)
        evt = PieceMovedEvent(_piece("w", "R"), (0, 0), (0, 4))
        subj.notify_piece_moved(evt)
        assert obs1.moved and obs2.moved

    def test_no_observers_does_not_raise(self):
        subj = GameSubject()
        subj.notify_piece_moved(PieceMovedEvent(_piece("w", "K"), (0, 4), (0, 5)))


# ── GameEventSource ───────────────────────────────────────────────────────────

class TestGameEventSource:
    def _empty(self):
        return [[Piece.EMPTY] * 8 for _ in range(8)]

    def test_first_poll_emits_nothing(self):
        src = GameEventSource()
        obs = _RecordingObserver()
        src.add_observer(obs)
        grid = self._empty()
        grid[0][0] = _piece("w", "R")
        src.poll(_FakeGame(grid))
        assert not obs.moved and not obs.captured

    def test_move_detected_on_second_poll(self):
        src = GameEventSource()
        obs = _RecordingObserver()
        src.add_observer(obs)
        p = _piece("w", "R")
        g1 = self._empty(); g1[0][0] = p
        g2 = self._empty(); g2[0][4] = p
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert len(obs.moved) == 1
        assert obs.moved[0].origin == (0, 0)
        assert obs.moved[0].destination == (0, 4)

    def test_capture_detected_when_piece_disappears(self):
        src = GameEventSource()
        obs = _RecordingObserver()
        src.add_observer(obs)
        victim = _piece("b", "P")
        attacker = _piece("w", "R")
        g1 = self._empty(); g1[3][3] = victim
        # attacker arrives at victim's cell; victim gone
        g2 = self._empty(); g2[3][3] = attacker
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert len(obs.captured) == 1
        assert obs.captured[0].captured_piece is victim
        assert obs.captured[0].at_cell == (3, 3)

    def test_no_event_when_board_unchanged(self):
        src = GameEventSource()
        obs = _RecordingObserver()
        src.add_observer(obs)
        p = _piece("w", "N")
        grid = self._empty(); grid[2][2] = p
        src.poll(_FakeGame(grid))
        src.poll(_FakeGame(grid))
        assert not obs.moved and not obs.captured

    def test_capture_by_piece_identified(self):
        src = GameEventSource()
        obs = _RecordingObserver()
        src.add_observer(obs)
        victim = _piece("b", "P")
        attacker = _piece("w", "R")
        g1 = self._empty(); g1[4][4] = victim
        g2 = self._empty(); g2[4][4] = attacker
        src.poll(_FakeGame(g1))
        src.poll(_FakeGame(g2))
        assert obs.captured[0].by_piece is attacker


# ── ScoreBoard ────────────────────────────────────────────────────────────────

class TestScoreBoard:
    def test_initial_scores_are_zero(self):
        sb = ScoreBoard()
        assert sb._score == {"w": 0, "b": 0}

    def test_capture_adds_piece_value_to_capturer(self):
        sb = ScoreBoard()
        queen = _piece("b", "Q")   # value = 9
        attacker = _piece("w", "R")
        sb.on_piece_captured(PieceCapturedEvent(queen, (0, 0), by_piece=attacker))
        assert sb._score["w"] == 9
        assert sb._score["b"] == 0

    def test_capture_by_black_adds_to_black(self):
        sb = ScoreBoard()
        pawn = _piece("w", "P")    # value = 1
        attacker = _piece("b", "N")
        sb.on_piece_captured(PieceCapturedEvent(pawn, (1, 1), by_piece=attacker))
        assert sb._score["b"] == 1

    def test_capture_without_by_piece_does_not_change_score(self):
        sb = ScoreBoard()
        pawn = _piece("w", "P")
        sb.on_piece_captured(PieceCapturedEvent(pawn, (1, 1), by_piece=None))
        assert sb._score == {"w": 0, "b": 0}

    def test_multiple_captures_accumulate(self):
        sb = ScoreBoard()
        attacker = _piece("w", "Q")
        sb.on_piece_captured(PieceCapturedEvent(_piece("b", "P"), (0, 0), by_piece=attacker))
        sb.on_piece_captured(PieceCapturedEvent(_piece("b", "R"), (1, 0), by_piece=attacker))
        assert sb._score["w"] == 6   # 1 + 5

    def test_king_capture_adds_zero(self):
        sb = ScoreBoard()
        king = _piece("b", "K")    # value = 0
        attacker = _piece("w", "Q")
        sb.on_piece_captured(PieceCapturedEvent(king, (0, 4), by_piece=attacker))
        assert sb._score["w"] == 0
