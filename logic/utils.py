import os


def safe_join(base: str, *parts: str) -> str:
    """Join path parts and raise ValueError if the result escapes base."""
    base = os.path.realpath(base)
    path = os.path.realpath(os.path.join(base, *parts))
    if not path.startswith(base + os.sep) and path != base:
        raise ValueError(f"Path traversal detected: {path!r} is outside {base!r}")
    return path
