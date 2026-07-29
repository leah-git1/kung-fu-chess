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
from websockets.exceptions import ConnectionClosed, WebSocketException

from shared.messages import parse
from client.log_utils.client_logger import log


class WsClient:
    def __init__(self, url: str):
        self._url = url
        self.inbound: queue.Queue = queue.Queue()
        self._outbound: asyncio.Queue | None = None
        self._pending_outbound: queue.Queue = queue.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._reconnect_event: asyncio.Event | None = None
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

    def reconnect(self, url: str, first_msg: dict | None = None) -> None:
        """Drop the current connection and open a new one to url.
        first_msg is sent as the very first message on the new socket (raw dict).
        """
        self._url = url
        if first_msg:
            self._pending_outbound.put_nowait(first_msg)
        if self._loop:
            self._loop.call_soon_threadsafe(self._reconnect_event.set)

    # ── background thread ─────────────────────────────────────────────────────

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._outbound = asyncio.Queue()
        self._reconnect_event = asyncio.Event()
        self._loop.run_until_complete(self._connect_loop())

    async def _connect_loop(self) -> None:
        while True:
            self._reconnect_event.clear()
            await self._connect()
            if not self._reconnect_event.is_set():
                # Connection dropped without an explicit reconnect request.
                # Wait briefly in case the main thread is about to call reconnect()
                # (e.g. server closed the socket right before ShardConnectMsg was processed).
                try:
                    await asyncio.wait_for(self._reconnect_event.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    break  # no reconnect requested within 2s — truly done
            self._outbound = asyncio.Queue()  # fresh queue for new connection

    async def _connect(self) -> None:
        try:
            async with websockets.connect(self._url) as ws:
                self.connected = True
                log(f"connected to {self._url}")
                self._flush_pending_outbound()
                done, pending = await asyncio.wait(
                    [asyncio.ensure_future(self._receive_loop(ws)),
                     asyncio.ensure_future(self._send_loop(ws)),
                     asyncio.ensure_future(self._reconnect_event.wait())],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for t in pending:
                    t.cancel()
        except (OSError, WebSocketException) as e:
            self.error = str(e)
            self.connected = False
            log(f"connection failed: {e}", level="error")

    def _flush_pending_outbound(self) -> None:
        if self._outbound is None:
            return
        while not self._pending_outbound.empty():
            self._outbound.put_nowait(self._pending_outbound.get_nowait())

    async def _receive_loop(self, ws) -> None:
        async for raw in ws:
            try:
                msg = parse(json.loads(raw))
                log(f"recv: {msg}", level="debug")
                self.inbound.put_nowait(msg)
            except (json.JSONDecodeError, ValueError) as e:
                log(f"recv parse error: {e}", level="warning")

    async def _send_loop(self, ws) -> None:
        while True:
            d = await self._outbound.get()
            try:
                log(f"send: {d}", level="debug")
                await ws.send(json.dumps(d))
            except ConnectionClosed:
                log("connection closed while sending", level="warning")
                break
