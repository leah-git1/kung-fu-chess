import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
import bcrypt
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from server.db import database as db
from server.db.user_repository import User
from server.db.database import init_db

app = FastAPI()


class AuthRequest(BaseModel):
    username: str
    password: str


def _get_user(username: str) -> User | None:
    row = db.fetch_user(username)
    return User(row["user_id"], row["username"], row["password_hash"], row["rating"]) if row else None


@app.on_event("startup")
def startup():
    init_db()


@app.post("/register")
def register(req: AuthRequest):
    if _get_user(req.username) is not None:
        return JSONResponse(status_code=400, content={"error": "username already taken"})
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    try:
        user_id = db.insert_user(req.username, hashed)
        return {"username": req.username, "rating": 1200}
    except sqlite3.IntegrityError:
        return JSONResponse(status_code=400, content={"error": "username already taken"})
    except sqlite3.Error as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/login")
def login(req: AuthRequest):
    user = _get_user(req.username)
    if user is None or not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        return JSONResponse(status_code=401, content={"error": "invalid credentials"})
    return {"username": user.username, "rating": user.rating}
