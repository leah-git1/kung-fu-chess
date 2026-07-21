"""Standard ELO rating calculation."""
from shared.constants import ELO_K_FACTOR, ELO_SCALE


def calculate_elo(winner_rating: int, loser_rating: int, k: int = ELO_K_FACTOR) -> tuple[int, int]:
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / ELO_SCALE))
    delta = round(k * (1 - expected_winner))
    return winner_rating + delta, loser_rating - delta
