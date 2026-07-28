"""
Terminal auth prompt — calls the API Gateway over HTTP before opening the WebSocket.
Returns (username, rating, token).
"""
import getpass
import httpx


def shell_login(api_url: str) -> tuple[str, int, str]:
    while True:
        action = input("[L]ogin / [R]egister: ").strip().lower()
        if action not in ("l", "r", "login", "register"):
            continue
        register = action in ("r", "register")
        username = input("username: ").strip()
        password = getpass.getpass("password: ")

        endpoint = "/register" if register else "/login"
        try:
            resp = httpx.post(f"{api_url}{endpoint}",
                              json={"username": username, "password": password},
                              timeout=5.0)
        except httpx.RequestError as e:
            print(f"Cannot reach server: {e}")
            continue

        if resp.status_code == 200:
            data = resp.json()
            return data["username"], data["rating"], data["token"]
        else:
            print(f"Failed: {resp.json().get('error', 'unknown error')}")
