"""
Server entry point.

Run with:
    python -m server.main
    python -m server.main --port 5555
"""
import asyncio
import argparse
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.constants import DEFAULT_PORT
from server.app_server import AppServer


def main(port: int = DEFAULT_PORT) -> None:
    asyncio.run(AppServer(port).start())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    main(**vars(p.parse_args()))
