"""
Converts between logic-layer objects and wire-protocol dicts.

board_to_json  : Game → list[list[str|None]]   (used in STATE_UPDATE)
apply_move     : MoveMsg  + Game → bool
apply_jump     : JumpMsg  + Game → bool
"""
from __future__ import annotations


def board_to_json(game) -> list:
    """Serialise the current board snapshot to a JSON-safe nested list.

    Each cell is either None (empty) or a two-character string like "wR", "bK".
    """
    return [
        [None if piece is None else piece.sprite_key for piece in row]
        for row in game.snapshot()
    ]


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
