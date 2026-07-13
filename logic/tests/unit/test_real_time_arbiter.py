from board.board import Board
from board.piece import Piece, PieceState
from board.piece_type import PieceType
from realtime.real_time_arbiter import RealTimeArbiter


def _p(token):
    return Piece(token[0], PieceType(token[1]))


def board_with(pieces: dict, rows=8, cols=8):
    grid = [[Piece.EMPTY] * cols for _ in range(rows)]
    for (r, c), token in pieces.items():
        grid[r][c] = _p(token)
    return Board(grid)


# ------------------------------------------------------------------
# is_any_moving
# ------------------------------------------------------------------

def test_no_motions_not_moving():
    arbiter = RealTimeArbiter()
    assert not arbiter.is_any_moving()


def test_move_added_is_moving():
    arbiter = RealTimeArbiter()
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    assert arbiter.is_any_moving()


def test_jump_only_not_moving():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert not arbiter.is_any_moving()


# ------------------------------------------------------------------
# is_airborne
# ------------------------------------------------------------------

def test_cell_not_airborne_initially():
    arbiter = RealTimeArbiter()
    assert not arbiter.is_airborne((0, 0))


def test_cell_airborne_after_jump():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert arbiter.is_airborne((0, 0))


def test_different_cell_not_airborne():
    arbiter = RealTimeArbiter()
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    assert not arbiter.is_airborne((0, 1))


# ------------------------------------------------------------------
# advance — move arrival
# ------------------------------------------------------------------

def test_move_applies_to_board_on_arrival():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(1000, board)
    assert board.get_piece(0, 7) == _p("wR")
    assert board.get_piece(0, 0) is Piece.EMPTY


def test_move_not_applied_before_finish_time():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(999, board)
    assert board.get_piece(0, 0) == _p("wR")
    assert board.get_piece(0, 7) is Piece.EMPTY


def test_move_cleared_from_active_after_arrival():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    arbiter.advance(1000, board)
    assert not arbiter.is_any_moving()


# ------------------------------------------------------------------
# advance — capture events
# ------------------------------------------------------------------

def test_enemy_at_destination_is_captured():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "bP"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, _ = arbiter.advance(1000, board)
    assert _p("bP") in captured


def test_friendly_at_destination_piece_stops_before_it():
    # Friendly already occupying the destination: rook stops one cell short.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "wP"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 1
    assert board.get_piece(0, 6) == _p("wR")  # stopped one cell before the friendly
    assert board.get_piece(0, 7) == _p("wP")  # friendly untouched


# ------------------------------------------------------------------
# advance — airborne interception
# ------------------------------------------------------------------

def test_airborne_enemy_intercepts_arriving_piece():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 2): "bR"})
    arbiter.add_jump(_p("bR"), (0, 0), finish_time=2000)
    arbiter.add_move(_p("wR"), (0, 2), (0, 0), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert _p("wR") in captured
    assert len(applied) == 0


def test_no_interception_same_color():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wP"), (0, 7), finish_time=2000)
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0


# ------------------------------------------------------------------
# advance — jump clears after finish
# ------------------------------------------------------------------

def test_jump_clears_after_finish():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    arbiter.advance(1000, board)
    assert not arbiter.is_airborne((0, 0))


def test_jump_still_active_before_finish():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    arbiter.advance(999, board)
    assert arbiter.is_airborne((0, 0))


def test_piece_stays_on_cell_during_jump():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_jump(_p("wR"), (0, 0), finish_time=1000)
    arbiter.advance(1000, board)
    assert board.get_piece(0, 0) == _p("wR")


def test_airborne_piece_stays_on_cell_after_interception():
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "bR", (0, 2): "wR"})
    arbiter.add_jump(_p("bR"), (0, 0), finish_time=2000)
    arbiter.add_move(_p("wR"), (0, 2), (0, 0), finish_time=1000)
    arbiter.advance(1000, board)
    assert board.get_piece(0, 0) == _p("bR")


# ------------------------------------------------------------------
# Scenario 1 — two enemies reach the same square at different times
#              → later arrival captures the earlier one
# ------------------------------------------------------------------

def test_enemy_arrives_later_captures_earlier():
    # wR arrives at (0,4) at t=1000; bR arrives at (0,4) at t=2000.
    # After both ticks: bR should occupy (0,4) and wR should be captured.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "bR"})
    wr = board.get_piece(0, 0)
    br = board.get_piece(0, 7)
    arbiter.add_move(wr, (0, 0), (0, 4), finish_time=1000)
    arbiter.add_move(br, (0, 7), (0, 4), finish_time=2000)

    captured1, _ = arbiter.advance(1000, board)
    assert len(captured1) == 0
    assert board.get_piece(0, 4) == _p("wR")

    captured2, _ = arbiter.advance(2000, board)
    assert _p("wR") in captured2
    assert board.get_piece(0, 4) == _p("bR")


# ------------------------------------------------------------------
# Scenario 2 — two enemies reach the same square at the same time
#              → resolve deterministically by insertion order
# ------------------------------------------------------------------

def test_two_enemies_arrive_same_time_first_inserted_lands_second_captures():
    # wR added first → lands first; bR added second → captures wR.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "bR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 4), finish_time=1000)
    arbiter.add_move(_p("bR"), (0, 7), (0, 4), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 1
    assert len(applied) == 2
    assert board.get_piece(0, 4) == _p("bR")


# ------------------------------------------------------------------
# Scenario 3 — two friendlies move toward the same destination
#              → both start, finish on different legal squares
# ------------------------------------------------------------------

def test_two_friendlies_toward_same_dest_both_start_finish_different_squares():
    # wR from (0,0) → (0,4), wB from (0,7) → (0,4), same finish time.
    # wR lands at (0,4); wB stops at (0,5) (one cell short from the right).
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 7): "wB"})
    wr = board.get_piece(0, 0)
    wb = board.get_piece(0, 7)
    arbiter.add_move(wr, (0, 0), (0, 4), finish_time=1000)
    arbiter.add_move(wb, (0, 7), (0, 4), finish_time=1000)

    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 2
    # Both pieces must be on different squares
    dest_wr = board.get_piece(0, 4)
    dest_wb = board.get_piece(0, 5)
    assert dest_wr == _p("wR")
    assert dest_wb == _p("wB")


# ------------------------------------------------------------------
# Scenario 4 — a friendly piece blocks another during movement
#              → later piece stops at nearest legal square
# ------------------------------------------------------------------

def test_friendly_moves_into_path_piece_stops_before_it():
    # wR moves (0,0)→(0,7); wB is placed at (0,4) before arrival resolves.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    board.set_piece(0, 4, _p("wB"))  # friendly moved into path mid-flight
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 1
    assert board.get_piece(0, 3) == _p("wR")  # stopped one cell before blocker
    assert board.get_piece(0, 4) == _p("wB")  # blocker untouched


def test_enemy_moves_into_path_piece_captures_it():
    # wR moves (0,0)→(0,7); bB appears at (0,4) before arrival.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    board.set_piece(0, 4, _p("bB"))  # enemy moved into path mid-flight
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 1
    assert len(applied) == 1
    assert board.get_piece(0, 4) == _p("wR")  # rook captured and took the cell


def test_friendly_at_first_step_piece_stays_at_origin():
    # wR moves (0,0)→(0,7); wB is at (0,1) — no room at all.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 1): "wB"})
    arbiter.add_move(_p("wR"), (0, 0), (0, 7), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 0
    assert board.get_piece(0, 0) == _p("wR")  # piece stays put


# ------------------------------------------------------------------
# In-flight origin treated as vacated
# ------------------------------------------------------------------

def test_two_pieces_crossing_paths_do_not_block_each_other():
    # wR: (0,0)→(0,7), wB: (0,3)→(0,0), same finish time.
    # wB's origin (0,3) is in wR's path but is vacated — wR should pass through.
    arbiter = RealTimeArbiter()
    board = board_with({(0, 0): "wR", (0, 3): "wB"})
    wr = board.get_piece(0, 0)
    wb = board.get_piece(0, 3)
    arbiter.add_move(wr, (0, 0), (0, 7), finish_time=1000)
    arbiter.add_move(wb, (0, 3), (0, 0), finish_time=1000)
    captured, applied = arbiter.advance(1000, board)
    assert len(captured) == 0
    assert len(applied) == 2
    assert board.get_piece(0, 7) == _p("wR")
    assert board.get_piece(0, 0) == _p("wB")
