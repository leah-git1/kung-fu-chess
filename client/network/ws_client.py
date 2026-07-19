"""
WsClient — runs an asyncio event loop in a daemon thread.

The synchronous cv2 render loop interacts with it through two thread-safe queues:
  inbound  : queue.Queue  — parsed message dataclasses pushed by the receive coroutine
  _outbound: asyncio.Queue — raw dicts put by send(), drained by the send coroutine

Usage:
    client = WsClient("ws://127.0.0.1:5555")
    client.start()
    client.send(HelloMsg(protocol_version=1))

    # in the render loop:
    while not client.inbound.empty():
        msg = client.inbound.get_nowait()
        ...
"""
from __future__ import annotations
import asyncio
import json
import queue
import threading

import websockets

from shared.messages import parse


class WsClient:
    def __init__(self, url: str):
        self._url = url
        self.inbound: queue.Queue = queue.Queue()
        self._outbound: asyncio.Queue | None = None
        self._pending_outbound: queue.Queue = queue.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None
        self.connected = False
        self.error: str | None = None

    # ── public API (called from the render thread) ────────────────────────────

    def start(self) -> None:
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def send(self, msg) -> None:
        payload = msg.to_json()
        if self._loop and self._outbound:
            self._loop.call_soon_threadsafe(self._outbound.put_nowait, payload)
        else:
            self._pending_outbound.put_nowait(payload)

    # ── background thread ─────────────────────────────────────────────────────

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._outbound = asyncio.Queue()
        self._loop.run_until_complete(self._connect())

    async def _connect(self) -> None:
        try:
            async with websockets.connect(self._url) as ws:
                self.connected = True
                self._flush_pending_outbound()
                await asyncio.gather(
                    self._receive_loop(ws),
                    self._send_loop(ws),
                )
        except Exception as e:
            self.error = str(e)
            self.connected = False

    def _flush_pending_outbound(self) -> None:
        if self._outbound is None:
            return
        while not self._pending_outbound.empty():
            self._outbound.put_nowait(self._pending_outbound.get_nowait())

    async def _receive_loop(self, ws) -> None:
        async for raw in ws:
            try:
                msg = parse(json.loads(raw))
                self.inbound.put_nowait(msg)
            except Exception:
                pass

    async def _send_loop(self, ws) -> None:
        while True:
            d = await self._outbound.get()
            try:
                await ws.send(json.dumps(d))
            except Exception:
                pass
