class PieceRegistry:
    """
    Central place that manages supported piece tokens.

    Future extensions:
    - Add new pieces
    - Load custom pieces
    - Replace text tokens with binary identifiers
    """

    _valid_tokens = {
        ".",

        # White pieces
        "wK",
        "wQ",
        "wR",
        "wB",
        "wN",
        "wP",

        # Black pieces
        "bK",
        "bQ",
        "bR",
        "bB",
        "bN",
        "bP",
    }

    @classmethod
    def is_valid(cls, token: str) -> bool:
        """
        Checks whether a token represents a known piece.
        """
        return token in cls._valid_tokens


    @classmethod
    def get_valid_tokens(cls):
        """
        Returns all supported tokens.

        Returning a copy prevents external modification.
        """
        return cls._valid_tokens.copy()


    @classmethod
    def register_piece(cls, token: str):
        """
        Allows adding new pieces dynamically.

        Example future:
        PieceRegistry.register_piece("wD")
        PieceRegistry.register_piece("bD")
        """

        if not isinstance(token, str):
            raise TypeError("Piece token must be a string")

        cls._valid_tokens.add(token)


    @classmethod
    def remove_piece(cls, token: str):
        """
        Allows removing a piece type if needed.
        """

        cls._valid_tokens.discard(token)