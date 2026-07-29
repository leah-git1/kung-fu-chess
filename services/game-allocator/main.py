"""
Game Allocator — assigns a matched pair to the least-loaded game-shard worker.

Subscribes to NATS subject kfc.matched:
  { white, black, white_rating, black_rating }
  → picks least-loaded worker from Redis shard:worker:* heartbeats
  → writes shard:{room_id} into Redis
  → publishes kfc.allocated: { room_id, shard_url, white, black }

Also exposes POST /allocate for direct HTTP calls (room-create path).
"""
import os
import json
import asyncio
import httpx
import redis
import nats
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from contextlib import asynccontextmanager

_ROOMS_URL          = f"http://{os.getenv('ROOMS_HOST', 'localhost')}:{os.getenv('ROOMS_PORT', '8001')}"
_NATS_URL           = os.getenv("NATS_URL", "nats://localhost:4222")
_SHARD_PUBLIC_HOST  = os.getenv("SHARD_PUBLIC_HOST", "localhost")
_SHARD_TTL          = 7200
_SUB_SUBJECT = "kfc.matched"
_PUB_SUBJECT = "kfc.allocated"

_nc = None   # nats client, set on startup


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


def _pick_worker(r: redis.Redis) -> dict | None:
    keys = r.keys("shard:worker:*")
    if not keys:
        return None
    workers = [json.loads(v) for k in keys if (v := r.get(k))]
    return min(workers, key=lambda w: w["rooms"]) if workers else None


def _do_allocate(white: str, black: str) -> dict | None:
    """Create room, pick worker, write Redis. Returns allocation dict or None."""
    try:
        resp = httpx.post(f"{_ROOMS_URL}/rooms",
                          json={"creator": white}, timeout=5.0)
        resp.raise_for_status()
    except httpx.RequestError:
        return None

    room_id = resp.json()["room_id"]
    r = _r()
    worker = _pick_worker(r)
    if worker is None:
        return None

    r.set(f"shard:{room_id}",
          json.dumps({"host": worker["host"], "port": worker["port"],
                      "white": white, "black": black}),
          ex=_SHARD_TTL)

    return {"room_id": room_id,
            "shard_url": f"ws://{_SHARD_PUBLIC_HOST}:{worker['port']}",
            "white": white, "black": black}


async def _on_matched(msg) -> None:
    data = json.loads(msg.data.decode())
    white, black = data["white"], data["black"]
    alloc = await asyncio.get_event_loop().run_in_executor(
        None, _do_allocate, white, black
    )
    if alloc and _nc:
        await _nc.publish(_PUB_SUBJECT, json.dumps(alloc).encode())


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _nc
    _nc = await nats.connect(_NATS_URL)
    await _nc.subscribe(_SUB_SUBJECT, cb=_on_matched)
    yield
    await _nc.drain()


app = FastAPI(lifespan=lifespan)


class AllocateRequest(BaseModel):
    white: str
    black: str


@app.post("/allocate")
async def allocate(req: AllocateRequest):
    alloc = await asyncio.get_event_loop().run_in_executor(
        None, _do_allocate, req.white, req.black
    )
    if alloc is None:
        return JSONResponse(status_code=503, content={"error": "allocation failed"})
    if _nc:
        await _nc.publish(_PUB_SUBJECT, json.dumps(alloc).encode())
    return {"room_id": alloc["room_id"], "shard_url": alloc["shard_url"]}
