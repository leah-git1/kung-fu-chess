class AuthError(Exception):
    """Raised by auth_service when login or registration fails for a business reason."""


class DatabaseError(Exception):
    """Raised when a database operation fails unexpectedly (constraint violation, IO error, etc.)."""
