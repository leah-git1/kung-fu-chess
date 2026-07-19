"""
Converts between logic-layer objects and wire-protocol dicts.

board_to_json  : Game → list[list[str|None]]   (used in STATE_UPDATE)
apply_move     : MoveMsg  + Game → bool
apply_jump     : JumpMsg  + Game → bool
"""
from __future__ import annotations


def board_to_json(game) -> list:
    # build a lookup: piece id -> cooldown finish_time
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
            "key":   m.piece.sprite_key,
            "origin":      list(m.origin),
            "destination": list(m.destination),
            "actual_dest": list(m.actual_destination),
            "finish_time": m.finish_time,
        }
        for m in game.active_moves()
    ]
    jumps = [
        {
            "key":  m.piece.sprite_key,
            "cell": list(m.cell),
        }
        for m in game.active_jumps()
    ]
    return {"moves": moves, "jumps": jumps}


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
