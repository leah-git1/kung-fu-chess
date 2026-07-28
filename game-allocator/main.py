"""
Game Allocator — assigns a matched pair to a game shard.

POST /allocate  { white: str, black: str }
  → calls rooms-api for a room_id
  → writes shard:{room_id} = <shard_host:port> into Redis
  → returns { room_id, shard }
"""
import os
import json
import httpx
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

_ROOMS_URL  = f"http://{os.getenv('ROOMS_HOST', 'localhost')}:{os.getenv('ROOMS_PORT', '8001')}"
_SHARD_ADDR = os.getenv("SHARD_ADDR", "kfc-server:5555")  # only one shard for now
_SHARD_TTL  = 7200


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


class AllocateRequest(BaseModel):
    white: str
    black: str


@app.post("/allocate")
def allocate(req: AllocateRequest):
    # get a unique room_id from the rooms-api
    try:
        resp = httpx.post(f"{_ROOMS_URL}/rooms",
                          json={"creator": req.white}, timeout=5.0)
        resp.raise_for_status()
    except httpx.RequestError as e:
        return JSONResponse(status_code=503, content={"error": f"rooms-api unavailable: {e}"})

    room_id = resp.json()["room_id"]

    # write room_id → shard mapping into Redis
    _r().set(f"shard:{room_id}",
             json.dumps({"host": _SHARD_ADDR, "white": req.white, "black": req.black}),
             ex=_SHARD_TTL)

    return {"room_id": room_id, "shard": _SHARD_ADDR}
