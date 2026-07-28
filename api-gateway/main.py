"""
API Gateway — HTTP entry point for login/register.

POST /login    { username, password }  → { token, username, rating }
POST /register { username, password }  → { token, username, rating }

On success a session token is written to Redis so the WS server can
validate it without calling back here.
"""
import os
import uuid
import httpx
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

_AUTH_URL  = f"http://{os.getenv('AUTH_HOST', 'localhost')}:{os.getenv('AUTH_PORT', '8000')}"
_SESSION_TTL = 300  # seconds — token must be used within 5 minutes


def _redis() -> redis.Redis:
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379,
                       decode_responses=True)


class AuthRequest(BaseModel):
    username: str
    password: str


def _auth(endpoint: str, req: AuthRequest) -> JSONResponse | dict:
    try:
        resp = httpx.post(f"{_AUTH_URL}{endpoint}",
                          json={"username": req.username, "password": req.password},
                          timeout=5.0)
    except httpx.RequestError as e:
        return JSONResponse(status_code=503, content={"error": f"auth service unavailable: {e}"})

    if resp.status_code != 200:
        return JSONResponse(status_code=resp.status_code, content=resp.json())

    data = resp.json()
    token = uuid.uuid4().hex
    _redis().set(f"session:{token}", data["username"], ex=_SESSION_TTL)
    return {"token": token, "username": data["username"], "rating": data["rating"]}


@app.post("/login")
def login(req: AuthRequest):
    return _auth("/login", req)


@app.post("/register")
def register(req: AuthRequest):
    return _auth("/register", req)
