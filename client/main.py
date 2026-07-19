"""
Client entry point.

Offline (local, current behaviour):
    python -m client.main

Online (connect to server — not yet implemented):
    python -m client.main --host 127.0.0.1 --port 5555
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main(host: str = None, port: int = None):
    if host:
        print(f"[client] network mode → {host}:{port}  (not yet implemented)")
        return
    from client.graphics.app import GraphicsApp
    GraphicsApp().run()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    main(**vars(p.parse_args()))
