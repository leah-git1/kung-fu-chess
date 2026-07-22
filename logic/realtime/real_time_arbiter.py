from board.piece import Piece, PieceState
from board.piece_type import PieceType
from realtime.motion import MoveMotion, JumpMotion, CooldownMotion
import config
from config import RestType


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
        self._current_time: int = 0

    # ------------------------------------------------------------------
    # Mutation — called by Game after validation
    # ------------------------------------------------------------------

    def add_move(self, piece, origin, destination, finish_time: int) -> None:
        piece.state = PieceState.MOVING
        self._motions.append(MoveMotion(piece, origin, destination, finish_time))

    def add_jump(self, piece, cell, finish_time: int) -> None:
        piece.state = PieceState.JUMPING
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

    def active_moves(self) -> list:
        """
        Read-only snapshot of in-flight MoveMotions, for rendering only.
        Never mutated by callers; used by the graphics layer to interpolate
        a piece's on-screen position between origin and destination while
        `piece.state is PieceState.MOVING`. Adds no new state and changes no
        existing behaviour.
        """
        return [m for m in self._motions if isinstance(m, MoveMotion)]

    def active_jumps(self) -> list:
        """Read-only snapshot of in-flight JumpMotions, for rendering only."""
        return [m for m in self._motions if isinstance(m, JumpMotion)]

    def cooldown_progress(self, piece) -> tuple | None:
        """Returns (progress 0→1, rest_type 'long'|'short') for a resting piece, or None."""
        for m in self._motions:
            if isinstance(m, CooldownMotion) and m.piece is piece:
                state = piece.state
                if state == PieceState.LONG_REST:
                    duration = config.LONG_REST_DURATION
                elif state == PieceState.SHORT_REST:
                    duration = config.SHORT_REST_DURATION
                else:
                    return None
                elapsed = duration - (m.finish_time - self._current_time)
                progress = max(0.0, min(1.0, elapsed / duration))
                rest_type = RestType.LONG if state == PieceState.LONG_REST else RestType.SHORT
                return progress, rest_type
        return None

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
        self._current_time = current_time

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
            if isinstance(motion, JumpMotion):
                # JUMP -> SHORT_REST -> IDLE. This transition used to be
                # missing entirely: a finished jump left piece.state
                # untouched, so the piece never rested and its clip never
                # switched to the short_rest sprite.
                motion.piece.state = PieceState.SHORT_REST
                self._motions.append(
                    CooldownMotion(motion.piece, current_time + config.SHORT_REST_DURATION)
                )
            elif isinstance(motion, CooldownMotion):
                motion.piece.state = PieceState.IDLE

        # Keep motions that did not finish this tick, plus any CooldownMotions
        # appended during resolution above.
        finishing_set = set(id(m) for m in finishing)
        self._motions = [m for m in self._motions if id(m) not in finishing_set]

        in_flight_origins_live = {m.origin for m in self._motions if isinstance(m, MoveMotion)}
        for motion in self._motions:
            if isinstance(motion, MoveMotion):
                motion.actual_destination = self._resolve_destination(
                    motion, board, in_flight_origins_live
                ) or motion.origin

        return captured, applied

    # ------------------------------------------------------------------
    # Internal resolution — board mutation lives here, not in Motion
    # ------------------------------------------------------------------

    def _resolve_move(self, motion: MoveMotion, board, captured: list, applied: list,
                      current_time: int, in_flight_origins: set) -> None:
        actual_dest = self._resolve_destination(motion, board, in_flight_origins)
        motion.actual_destination = actual_dest if actual_dest is not None else motion.origin
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
        motion.piece.state = PieceState.LONG_REST
        self._motions.append(CooldownMotion(motion.piece, current_time + config.LONG_REST_DURATION))

    def _resolve_destination(self, motion: MoveMotion, board, in_flight_origins: set):
        """
        Picks the cell a finishing MoveMotion actually lands on.

        Sliding pieces (rook/bishop/queen/king/pawn) walk a straight line from
        origin to destination, so _last_reachable_cell's step-by-step blocking
        check applies to them. A knight's move is an L-shape, not a straight
        line, so that same step-by-step walk does not trace the knight's real
        path at all - it was checking unrelated cells for "blocking" pieces
        and could wrongly cancel a perfectly legal knight move. Knights jump
        over everything in between, so only the destination square matters.
        """
        if motion.piece.piece_type == PieceType.KNIGHT:
            dest = motion.destination
            vacated = in_flight_origins | {motion.origin}
            dest_piece = board.get_piece(*dest)
            if dest_piece is not Piece.EMPTY and dest not in vacated:
                if motion.piece.is_same_color(dest_piece):
                    return None  # destination occupied by a friendly piece
            return dest

        return self._last_reachable_cell(
            motion.origin, motion.destination, motion.piece, board, in_flight_origins
        )

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
