"""
Client entry point.

Offline (local, unchanged behaviour):
    python -m client.main

Online (connect to server):
    python -m client.main --host 127.0.0.1 --port 5555 --name Alice
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main(host: str = None, port: int = None, name: str = "Player"):
    if host:
        from client.game_client_app import GameClientApp
        from client.auth.shell_login import shell_login
        from shared.constants import DEFAULT_PORT
        username, password, register = shell_login()
        GameClientApp(host=host, port=port or DEFAULT_PORT,
                      player_name=username, password=password, register=register).run()
    else:
        from client.graphics.app import GraphicsApp
        GraphicsApp().run()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--name", default="Player")
    main(**vars(p.parse_args()))
