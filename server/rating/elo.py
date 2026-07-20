"""Standard ELO rating calculation."""


def calculate_elo(winner_rating: int, loser_rating: int, k: int = 32) -> tuple[int, int]:
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    delta = round(k * (1 - expected_winner))
    return winner_rating + delta, loser_rating - delta
