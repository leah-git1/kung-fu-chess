"""Applies ELO changes after a game result."""
from server.db import user_repository as repo
from server.rating.elo import calculate_elo


def apply_game_result(winner_name: str, loser_name: str) -> None:
    winner = repo.get(winner_name)
    loser  = repo.get(loser_name)
    if winner is None or loser is None:
        return
    new_winner, new_loser = calculate_elo(winner.rating, loser.rating)
    repo.update_rating(winner_name, new_winner)
    repo.update_rating(loser_name,  new_loser)
