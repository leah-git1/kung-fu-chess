from shared.enums import Color


class AppState:
    """Mutable session state shared across views via context dicts."""
    player_name: str = "Player"
    password:    str = ""
    register:    bool = False
    rating:      int  = 1200
    color:       Color = Color.SPECTATOR
    white_name:  str = "White"
    black_name:  str = "Black"
    room_id:     str = ""

    def __init__(self, player_name: str, password: str, register: bool, rating: int):
        self.player_name = player_name
        self.password    = password
        self.register    = register
        self.rating      = rating
        self.color       = Color.WHITE
        self.white_name  = "White"
        self.black_name  = "Black"
        self.room_id     = ""
