"""
Matchmaker Service — ELO-based queue stored in Redis.

POST   /queue              { name: str, rating: int }  → 202 enqueued
DELETE /queue/{name}                                   → 204 removed
GET    /queue/{name}/match                             → { matched: bool, opponent: str|null, opponent_rating: int|null }
"""
import os
import json
import threading
import time
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

_ELO_RANGE   = 100
_QUEUE_KEY   = "mm:queue"       # Redis list of JSON entries
_MATCH_KEY   = "mm:match:{}"   # Redis key per player → opponent JSON, TTL 60s
_MATCH_TTL   = 60


def _r() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


class EnqueueRequest(BaseModel):
    name: str
    rating: int


# ── background match loop ─────────────────────────────────────────────────────

def _match_loop():
    r = _r()
    while True:
        time.sleep(1)
        raw_entries = r.lrange(_QUEUE_KEY, 0, -1)
        entries = [json.loads(e) for e in raw_entries]
        matched: set[str] = set()

        for i, a in enumerate(entries):
            if a["name"] in matched:
                continue
            for b in entries[i + 1:]:
                if b["name"] in matched:
                    continue
                if abs(a["rating"] - b["rating"]) <= _ELO_RANGE:
                    matched.add(a["name"])
                    matched.add(b["name"])
                    r.set(_MATCH_KEY.format(a["name"]),
                          json.dumps({"opponent": b["name"], "opponent_rating": b["rating"]}),
                          ex=_MATCH_TTL)
                    r.set(_MATCH_KEY.format(b["name"]),
                          json.dumps({"opponent": a["name"], "opponent_rating": a["rating"]}),
                          ex=_MATCH_TTL)
                    break

        if matched:
            # remove matched players from the queue
            remaining = [e for e in raw_entries
                         if json.loads(e)["name"] not in matched]
            pipe = r.pipeline()
            pipe.delete(_QUEUE_KEY)
            for e in remaining:
                pipe.rpush(_QUEUE_KEY, e)
            pipe.execute()


@app.on_event("startup")
def startup():
    t = threading.Thread(target=_match_loop, daemon=True)
    t.start()


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.post("/queue", status_code=202)
def enqueue(req: EnqueueRequest):
    r = _r()
    # avoid duplicates
    for raw in r.lrange(_QUEUE_KEY, 0, -1):
        if json.loads(raw)["name"] == req.name:
            return {"status": "already queued"}
    r.rpush(_QUEUE_KEY, json.dumps({"name": req.name, "rating": req.rating}))
    return {"status": "queued"}


@app.delete("/queue/{name}", status_code=204)
def dequeue(name: str):
    r = _r()
    for raw in r.lrange(_QUEUE_KEY, 0, -1):
        if json.loads(raw)["name"] == name:
            r.lrem(_QUEUE_KEY, 1, raw)
            break
    r.delete(_MATCH_KEY.format(name))


@app.get("/queue/{name}/match")
def poll_match(name: str):
    raw = _r().get(_MATCH_KEY.format(name))
    if raw is None:
        return {"matched": False, "opponent": None, "opponent_rating": None}
    data = json.loads(raw)
    return {"matched": True, "opponent": data["opponent"],
            "opponent_rating": data["opponent_rating"]}
