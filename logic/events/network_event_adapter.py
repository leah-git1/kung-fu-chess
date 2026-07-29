from events.game_events import PieceMovedEvent, PieceCapturedEvent, GameOverEvent


class NetworkEventAdapter:
    """
    Translates incoming server messages and mirror callbacks into bus events.
    """

    def __init__(self, bus, mirror):
        self._bus    = bus
        self._mirror = mirror

    def on_move_ack(self, msg) -> None:
        piece = (self._mirror.get_piece_at(tuple(msg.from_cell))
                 or self._mirror.get_piece_at(tuple(msg.to_cell)))
        if piece is not None:
            self._bus.publish(PieceMovedEvent(
                color=piece.color,
                origin=tuple(msg.from_cell),
                destination=tuple(msg.to_cell),
                elapsed_ms=msg.time_ms,
                piece_name=piece.sprite_key[1],
            ))

    def on_jump_ack(self, msg) -> None:
        piece = self._mirror.get_piece_at(tuple(msg.cell))
        if piece is not None:
            self._bus.publish(PieceMovedEvent(
                color=piece.color,
                origin=tuple(msg.cell),
                destination=tuple(msg.cell),
                elapsed_ms=msg.time_ms,
                piece_name=piece.sprite_key[1],
            ))

    def on_capture(self, vm, at_cell: tuple, time_ms: int, by_color: str | None) -> None:
        self._bus.publish(PieceCapturedEvent(
            at_cell=at_cell,
            elapsed_ms=time_ms,
            piece_value=vm.value,
            by_color=by_color,
            captured_color=vm.color,
            captured_type=vm.sprite_key[1],
        ))

    def on_game_over(self, msg) -> None:
        self._bus.publish(GameOverEvent(winner_color=msg.winner))
