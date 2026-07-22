"""Applies ELO changes after a game result."""
import sqlite3
from server.db import user_repository as repo
from server.rating.elo import calculate_elo
from server.errors import DatabaseError
from server.logging.server_logger import log


def apply_game_result(winner_name: str, loser_name: str) -> None:
    try:
        winner = repo.get(winner_name)
        loser  = repo.get(loser_name)
        if winner is None or loser is None:
            return
        new_winner, new_loser = calculate_elo(winner.rating, loser.rating)
        repo.update_rating(winner_name, new_winner)
        repo.update_rating(loser_name,  new_loser)
    except sqlite3.Error as e:
        log(f"failed to update ratings for {winner_name} vs {loser_name}: {e}")
