"""
Converts between logic-layer objects and wire-protocol dicts.

board_to_json  : Game → list[list[str|None]]   (used in STATE_UPDATE)
apply_move     : MoveMsg  + Game → bool
apply_jump     : JumpMsg  + Game → bool
"""
from __future__ import annotations
from shared.enums import RestType


def board_to_json(game) -> list:
    cooldown_finish = {}
    for m in game._arbiter._motions:
        from realtime.motion import CooldownMotion
        if isinstance(m, CooldownMotion):
            cooldown_finish[id(m.piece)] = m.finish_time

    return [
        [None if piece is None else {
            "k": piece.sprite_key,
            "s": piece.state_name,
            "cd_finish": cooldown_finish.get(id(piece)),
         }
         for piece in row]
        for row in game.snapshot()
    ]


def motions_to_json(game) -> dict:
    """Serialise active moves and jumps for client-side animation."""
    moves = [
        {
            "key":         m.piece.sprite_key,
            "origin":      list(m.origin),
            "destination": list(m.destination),
            "actual_dest": list(m.actual_destination),
            "start_time":  m.finish_time - _move_duration(m.origin, m.destination),
            "finish_time": m.finish_time,
        }
        for m in game.active_moves()
    ]
    jumps = [
        {
            "key":        m.piece.sprite_key,
            "cell":       list(m.cell),
            "finish_time": m.finish_time,
        }
        for m in game.active_jumps()
    ]
    return {"moves": moves, "jumps": jumps}


def cooldowns_to_json(game) -> list:
    """Serialise active cooldowns (CooldownMotion) for client-side progress bars."""
    from realtime.motion import CooldownMotion
    import config

    # build a reverse map: piece id → (row, col) from the current board snapshot
    piece_cell = {
        id(p): (r, c)
        for r, row in enumerate(game.snapshot())
        for c, p in enumerate(row)
        if p is not None
    }

    result = []
    for m in game._arbiter._motions:
        if isinstance(m, CooldownMotion):
            state = m.piece.state.value
            from board.piece import PieceState
            if state == PieceState.LONG_REST.value:
                duration = config.LONG_REST_DURATION
            elif state == PieceState.SHORT_REST.value:
                duration = config.SHORT_REST_DURATION
            else:
                continue
            cell = piece_cell.get(id(m.piece))
            if cell is None:
                continue
            result.append({
                "key":          m.piece.sprite_key,
                "cell":         list(cell),
                "rest_type":    RestType.LONG.value if state == PieceState.LONG_REST.value else RestType.SHORT.value,
                "start_time":   m.finish_time - duration,
                "finish_time":  m.finish_time,
            })
    return result


def _move_duration(origin, destination) -> int:
    import config
    return max(abs(destination[0] - origin[0]), abs(destination[1] - origin[1])) * config.MOVE_DURATION_PER_CELL


def apply_move(msg, game) -> bool:
    """Translate a MoveMsg into a game.request_move call.

    Returns True if the move was accepted by the game engine.
    """
    from_cell = tuple(msg.from_cell)
    to_cell   = tuple(msg.to_cell)
    piece = game.get_piece_at(from_cell)
    return game.request_move(piece, from_cell, to_cell)


def apply_jump(msg, game) -> bool:
    """Translate a JumpMsg into a game.request_jump call."""
    cell  = tuple(msg.cell)
    piece = game.get_piece_at(cell)
    return game.request_jump(piece, cell)
