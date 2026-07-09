from rules.movement_strategy import MovementStrategyFactory


class RuleEngine:

    def is_legal_move(self, piece, start, end, board) -> bool:
        strategy = MovementStrategyFactory.for_piece(piece)
        if strategy is None:
            return False
        return strategy.is_legal(piece, start, end, board)
