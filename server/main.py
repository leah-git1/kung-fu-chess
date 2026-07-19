"""
Server entry point.

Run with:
    python -m server.main [--port 5555]

Responsibilities:
- Accept incoming TCP connections
- Assign players to rooms (matchmaking)
- Drive the per-room tick loop
- Relay validated move/jump acknowledgements to both clients
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.constants import DEFAULT_PORT


def main(port: int = DEFAULT_PORT):
    print(f"[server] starting on port {port}  (not yet implemented)")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    main(**vars(p.parse_args()))
