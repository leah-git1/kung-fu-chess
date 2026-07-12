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
        """
        captured = []
        applied = []

        for motion in self._motions:
            if not motion.is_finished(current_time):
                continue
            motion._done = True

            if isinstance(motion, MoveMotion):
                if self._intercepted(motion):
                    motion.piece.state = PieceState.CAPTURED
                    captured.append(motion.piece)
                    board.set_piece(motion.origin[0], motion.origin[1], Piece.EMPTY)
                else:
                    self._resolve_move(motion, board, captured, applied, current_time)

            elif isinstance(motion, CooldownMotion):
                motion.piece.state = PieceState.IDLE

        self._motions = [m for m in self._motions if not getattr(m, "_done", False)]
        return captured, applied

    # ------------------------------------------------------------------
    # Internal resolution — board mutation lives here, not in Motion
    # ------------------------------------------------------------------

    def _resolve_move(self, motion: MoveMotion, board, captured: list, applied: list, current_time: int) -> None:
        destination_piece = board.get_piece(*motion.destination)
        if destination_piece is not Piece.EMPTY and destination_piece.is_same_color(motion.piece):
            motion.piece.state = PieceState.IDLE
            return
        if destination_piece is not Piece.EMPTY:
            destination_piece.state = PieceState.CAPTURED
            captured.append(destination_piece)
        board.move(motion.origin, motion.destination)
        applied.append(motion)
        motion.piece.state = PieceState.COOLDOWN
        self._motions.append(CooldownMotion(motion.piece, current_time + config.COOLDOWN_DURATION))

    def _intercepted(self, motion: MoveMotion) -> bool:
        return any(
            isinstance(m, JumpMotion)
            and m.cell == motion.destination
            and m.piece.color != motion.piece.color
            for m in self._motions
        )
