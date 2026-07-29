"""
Auth Service — login / register.

POST /login    { username, password }  → { username, rating }
POST /register { username, password }  → { username, rating }
"""
import sqlite3
import bcrypt
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from server.db import database as db
from server.db.database import init_db

app = FastAPI()


class AuthRequest(BaseModel):
    username: str
    password: str


@app.on_event("startup")
def startup():
    init_db()


@app.post("/register")
def register(req: AuthRequest):
    if db.fetch_user(req.username) is not None:
        return JSONResponse(status_code=400, content={"error": "username already taken"})
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    try:
        db.insert_user(req.username, hashed)
        return {"username": req.username, "rating": 1200}
    except sqlite3.IntegrityError:
        return JSONResponse(status_code=400, content={"error": "username already taken"})
    except sqlite3.Error as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/login")
def login(req: AuthRequest):
    row = db.fetch_user(req.username)
    if row is None or not bcrypt.checkpw(req.password.encode(), row["password_hash"].encode()):
        return JSONResponse(status_code=401, content={"error": "invalid credentials"})
    return {"username": row["username"], "rating": row["rating"]}
