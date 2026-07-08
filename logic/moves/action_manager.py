from moves.move_action import MoveAction
from moves.jump_action import JumpAction


class ActionManager:

    def __init__(self):
        self.actions = []


    def add(self, action):
        self.actions.append(action)


    def is_any_moving(self) -> bool:
        return any(isinstance(a, MoveAction) for a in self.actions)


    def is_airborne(self, cell) -> bool:
        return any(isinstance(a, JumpAction) and a.cell == cell
                   for a in self.actions)


    def update(self, current_time, board):

        captured = []
        applied = []

        for action in self.actions:
            if not action.is_finished(current_time):
                continue

            action.completed = True

            if isinstance(action, MoveAction):
                if self._intercepted_by_airborne_enemy(action):
                    # Airborne enemy captures the arriving piece
                    captured.append(action.piece)
                    board.grid[action.origin[0]][action.origin[1]] = "."
                else:
                    action.resolve(board, captured, applied)
            else:
                action.resolve(board, captured, applied)

        self.actions = [a for a in self.actions if not a.completed]

        return captured, applied


    def _intercepted_by_airborne_enemy(self, move_action: MoveAction) -> bool:
        return any(
            isinstance(a, JumpAction)
            and a.cell == move_action.destination
            and a.piece[0] != move_action.piece[0]
            for a in self.actions
        )
