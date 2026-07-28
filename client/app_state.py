from shared.enums import Color


class AppState:
    """Mutable session state shared across views via context dicts."""
    def __init__(self, player_name: str, rating: int, token: str):
        self.player_name = player_name
        self.rating      = rating
        self.token       = token
        self.color       = Color.WHITE
        self.white_name  = "White"
        self.black_name  = "Black"
        self.room_id     = ""
