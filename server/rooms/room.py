import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "logic"))

from game.game import Game


class Room:
    """Holds two connected players and one authoritative Game instance."""

    def __init__(self, room_id: str, board):
        self.room_id = room_id
        self.game = Game(board)
        self.players: dict[str, object] = {}  # player_name -> connection
        self.started = False

    def add_player(self, name: str, conn) -> bool:
        if len(self.players) >= 2:
            return False
        self.players[name] = conn
        return True

    def is_full(self) -> bool:
        return len(self.players) == 2

    def tick(self, elapsed_ms: int):
        if self.started and not self.game.game_over:
            self.game.advance_time(elapsed_ms)
