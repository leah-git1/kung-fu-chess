"""
Terminal auth prompt — runs before the OpenCV window opens.
No networking here; credentials are sent on the real persistent connection.
Returns (username, password, register) for GameClientApp to use.
"""
import getpass


def shell_login() -> tuple[str, str, bool]:
    while True:
        action = input("[L]ogin / [R]egister: ").strip().lower()
        if action not in ("l", "r", "login", "register"):
            continue
        register = action in ("r", "register")
        username = input("username: ").strip()
        password = getpass.getpass("password: ")
        return username, password, register
