"""
Game Allocator — assigns a matched pair to the least-loaded game-shard worker.

POST /allocate  { white: str, black: str }
  → calls rooms-api for a room_id
  → reads shard:worker:* heartbeat keys from Redis, picks least-loaded worker
  → writes shard:{room_id} = {host, port, pid, white, black} into Redis
  → returns { room_id, shard_url }
"""
import os
import json
import httpx
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

_ROOMS_URL = f"http://{os.getenv('ROOMS_HOST', 'localhost')}:{os.getenv('ROOMS_PORT', '8001')}"
_SHARD_TTL = 7200


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


def _pick_worker(r: redis.Redis) -> dict | None:
    """Return the heartbeat payload of the least-loaded live worker, or None."""
    keys = r.keys("shard:worker:*")
    if not keys:
        return None
    workers = []
    for key in keys:
        raw = r.get(key)
        if raw:
            workers.append(json.loads(raw))
    if not workers:
        return None
    return min(workers, key=lambda w: w["rooms"])


class AllocateRequest(BaseModel):
    white: str
    black: str


@app.post("/allocate")
def allocate(req: AllocateRequest):
    try:
        resp = httpx.post(f"{_ROOMS_URL}/rooms",
                          json={"creator": req.white}, timeout=5.0)
        resp.raise_for_status()
    except httpx.RequestError as e:
        return JSONResponse(status_code=503, content={"error": f"rooms-api unavailable: {e}"})

    room_id = resp.json()["room_id"]

    r = _r()
    worker = _pick_worker(r)
    if worker is None:
        return JSONResponse(status_code=503, content={"error": "no live shard workers"})

    r.set(f"shard:{room_id}",
          json.dumps({"host": worker["host"], "port": worker["port"],
                      "white": req.white, "black": req.black}),
          ex=_SHARD_TTL)

    shard_url = f"ws://{worker['host']}:{worker['port']}"
    return {"room_id": room_id, "shard_url": shard_url}
