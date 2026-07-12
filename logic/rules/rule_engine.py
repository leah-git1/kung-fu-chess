from rules.piece_rules import MovementStrategyFactory


class RuleEngine:
    """Validates move legality by delegating to the appropriate MovementStrategy."""

    def is_legal_move(self, piece, start, end, board) -> bool:
        strategy = MovementStrategyFactory.for_piece(piece)
        if strategy is None:
            return False
        return strategy.is_legal(piece, start, end, board)

    def strategy_for(self, piece):
        return MovementStrategyFactory.for_piece(piece)
