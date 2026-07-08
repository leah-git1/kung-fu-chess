from piece.piece import Piece

class PieceRegistry:
    """
    Central place that manages supported piece tokens.

    Future extensions:
    - Add new pieces
    - Load custom pieces
    - Replace text tokens with binary identifiers
    """

    _valid_tokens = {".", "w", "b"}
    _valid_piece_types = {"K", "Q", "R", "B", "N", "P"}

    @classmethod
    def is_valid(cls, token):
        """
        Checks whether a token/piece is valid.
        Only accepts Piece objects, not string tokens.
        """
        if not hasattr(token, 'color') or not hasattr(token, 'piece_type'):
            return False
        if token is Piece.EMPTY:
            return True
        color_valid = token.color in cls._valid_tokens
        if token.piece_type is None:
            return color_valid
        piece_type_str = token.piece_type.value if hasattr(token.piece_type, 'value') else str(token.piece_type)
        return color_valid and piece_type_str in cls._valid_piece_types

    @classmethod
    def get_valid_tokens(cls):
        """
        Returns all supported base tokens.
        """
        return cls._valid_tokens.copy()

    @classmethod
    def register_color(cls, color: str):
        """
        Allows adding new piece colors dynamically.
        """
        if not isinstance(color, str) or len(color) != 1:
            raise TypeError("Color must be a single character string")
        cls._valid_tokens.add(color)

    @classmethod
    def register_piece(cls, token: str):
        """
        Allows adding new piece types dynamically.
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