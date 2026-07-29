"""
Rooms API — room_id registry in Redis.

POST   /rooms              { creator }  → { room_id }
GET    /rooms/{room_id}                 → { exists: bool }
DELETE /rooms/{room_id}                 → 204
"""
import os
import uuid
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

_ROOM_ID_LENGTH = 4
_ROOM_TTL_S     = 7200


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


class CreateRequest(BaseModel):
    creator: str


@app.post("/rooms", status_code=201)
def create_room(req: CreateRequest):
    r = _r()
    for _ in range(20):
        room_id = uuid.uuid4().hex[:_ROOM_ID_LENGTH].upper()
        if not r.exists(f"room:{room_id}"):
            r.set(f"room:{room_id}", req.creator, ex=_ROOM_TTL_S)
            return {"room_id": room_id}
    return JSONResponse(status_code=500, content={"error": "could not generate unique room id"})


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    exists = _r().exists(f"room:{room_id.upper()}") == 1
    return {"exists": exists}


@app.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: str):
    _r().delete(f"room:{room_id.upper()}")
