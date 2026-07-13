from board.piece import Piece, PieceState
from realtime.motion import MoveMotion, JumpMotion, CooldownMotion
import config


class RealTimeArbiter:
    """
    Owns all active Motion objects and advances simulated time.

    Responsibilities:
    - Store active MoveMotion and JumpMotion objects
    - Detect whether any move is in progress (for the one-active-move policy)
    - Detect whether a cell is airborne
    - Resolve arrivals: apply board mutations, detect captures
    - Detect interception of arriving pieces by airborne enemies

    No knowledge of: chess legality, clicks, rendering, script interpretation.
    """

    def __init__(self):
        self._motions: list = []

    # ------------------------------------------------------------------
    # Mutation — called by Game after validation
    # ------------------------------------------------------------------

    def add_move(self, piece, origin, destination, finish_time: int) -> None:
        piece.state = PieceState.MOVING
        self._motions.append(MoveMotion(piece, origin, destination, finish_time))

    def add_jump(self, piece, cell, finish_time: int) -> None:
        self._motions.append(JumpMotion(piece, cell, finish_time))

    # ------------------------------------------------------------------
    # Queries — read-only, used by Game to enforce policies
    # ------------------------------------------------------------------

    def is_any_moving(self) -> bool:
        return any(isinstance(m, MoveMotion) for m in self._motions)

    def is_piece_available(self, piece) -> bool:
        return piece.state == PieceState.IDLE

    def is_airborne(self, cell) -> bool:
        return any(isinstance(m, JumpMotion) and m.cell == cell for m in self._motions)

    # ------------------------------------------------------------------
    # Time advancement — resolves finished motions, returns events
    # ------------------------------------------------------------------

    def advance(self, current_time: int, board) -> tuple:
        """
        Resolves all motions that have finished by current_time.
        Returns (captured, applied_moves).
        - captured: list of Piece objects that were captured
        - applied_moves: list of MoveMotion objects that were applied to the board

        Finishing MoveMotions are processed in ascending finish_time order so
        that an earlier arrival always lands before a later one inspects the
        same square.  Ties are broken by insertion order (stable sort).
        """
        captured = []
        applied = []

        finishing = [m for m in self._motions if m.is_finished(current_time)]
        still_active = [m for m in self._motions if not m.is_finished(current_time)]

        # Process MoveMotions first, ordered by finish_time so earlier arrivals
        # land before later ones inspect the destination.
        move_finishing = sorted(
            [m for m in finishing if isinstance(m, MoveMotion)],
            key=lambda m: m.finish_time,
        )
        other_finishing = [m for m in finishing if not isinstance(m, MoveMotion)]

        # All origins that are logically vacated: still-travelling pieces plus
        # finishing peers that haven't resolved yet in this tick.
        in_flight_origins = (
            {m.origin for m in still_active if isinstance(m, MoveMotion)}
            | {m.origin for m in move_finishing}
        )

        for motion in move_finishing:
            # This piece has now resolved — its origin is no longer "pending".
            in_flight_origins.discard(motion.origin)
            if self._intercepted(motion):
                motion.piece.state = PieceState.CAPTURED
                captured.append(motion.piece)
                board.set_piece(motion.origin[0], motion.origin[1], Piece.EMPTY)
            else:
                self._resolve_move(motion, board, captured, applied, current_time, in_flight_origins)

        for motion in other_finishing:
            if isinstance(motion, CooldownMotion):
                motion.piece.state = PieceState.IDLE

        # Keep motions that did not finish this tick, plus any CooldownMotions
        # appended during resolution above.
        finishing_set = set(id(m) for m in finishing)
        self._motions = [m for m in self._motions if id(m) not in finishing_set]
        return captured, applied

    # ------------------------------------------------------------------
    # Internal resolution — board mutation lives here, not in Motion
    # ------------------------------------------------------------------

    def _resolve_move(self, motion: MoveMotion, board, captured: list, applied: list,
                      current_time: int, in_flight_origins: set) -> None:
        actual_dest = self._last_reachable_cell(
            motion.origin, motion.destination, motion.piece, board, in_flight_origins
        )
        if actual_dest is None:
            motion.piece.state = PieceState.IDLE
            return
        destination_piece = board.get_piece(*actual_dest)
        if destination_piece is not Piece.EMPTY:
            destination_piece.state = PieceState.CAPTURED
            captured.append(destination_piece)
        motion.destination = actual_dest
        board.move(motion.origin, actual_dest)
        applied.append(motion)
        motion.piece.state = PieceState.COOLDOWN
        self._motions.append(CooldownMotion(motion.piece, current_time + config.COOLDOWN_DURATION))

    def _last_reachable_cell(self, origin, destination, piece, board, in_flight_origins: set):
        """
        Walk the path from origin toward destination and return the furthest
        cell the piece can legally occupy at resolution time.

        Cells that are origins of still-travelling pieces are treated as empty
        because those pieces have logically vacated them.  The moving piece's
        own origin is also treated as empty (it is leaving).

        Returns None if the very first step is blocked by a friendly.
        """
        sr, sc = origin
        er, ec = destination
        dr = 0 if er == sr else (1 if er > sr else -1)
        dc = 0 if ec == sc else (1 if ec > sc else -1)

        vacated = in_flight_origins | {origin}

        last_clear = None
        r, c = sr + dr, sc + dc
        while True:
            cell_piece = board.get_piece(r, c)
            is_vacated = (r, c) in vacated
            if cell_piece is not Piece.EMPTY and not is_vacated:
                if piece.is_same_color(cell_piece):
                    return last_clear  # blocked by friendly — stop before this cell
                else:
                    return (r, c)     # enemy — capture here
            last_clear = (r, c)
            if (r, c) == (er, ec):
                return last_clear
            r += dr
            c += dc

    def _intercepted(self, motion: MoveMotion) -> bool:
        return any(
            isinstance(m, JumpMotion)
            and m.cell == motion.destination
            and m.piece.color != motion.piece.color
            for m in self._motions
        )
