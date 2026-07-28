"""
Rating Service — updates ELO after a game result.

POST /rate   { winner: str, loser: str }  → { winner_rating: int, loser_rating: int }
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from server.db import database as db
from server.db.database import init_db
from shared.constants import ELO_K_FACTOR, ELO_SCALE

app = FastAPI()


class RateRequest(BaseModel):
    winner: str
    loser: str


def _calculate_elo(winner_rating: int, loser_rating: int) -> tuple[int, int]:
    expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / ELO_SCALE))
    delta = round(ELO_K_FACTOR * (1 - expected))
    return winner_rating + delta, loser_rating - delta


@app.on_event("startup")
def startup():
    init_db()


@app.post("/rate")
def rate(req: RateRequest):
    try:
        winner_row = db.fetch_user(req.winner)
        loser_row  = db.fetch_user(req.loser)
        if winner_row is None or loser_row is None:
            return JSONResponse(status_code=404, content={"error": "user not found"})
        new_winner, new_loser = _calculate_elo(winner_row["rating"], loser_row["rating"])
        db.set_rating(req.winner, new_winner)
        db.set_rating(req.loser,  new_loser)
        return {"winner_rating": new_winner, "loser_rating": new_loser}
    except sqlite3.Error as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
