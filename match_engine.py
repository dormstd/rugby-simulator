import random
from constants import TRY_POINTS, CONVERSION_POINTS


def calculate_team_ratings(team):
    """Calculates aggregated attack and defense ratings based on player attributes."""
    if not team.players:
        return {"attack": 0, "defense": 0, "kicking": 0}

    # --- Define how attributes contribute to attack and defense ---
    # These weights are arbitrary and can be tuned extensively!
    attack_rating = sum(
        p.passing * 0.3
        + p.speed * 0.3
        + p.strength * 0.2
        + p.kicking * 0.1
        + p.skill * 0.1
        for p in team.players
    )
    defense_rating = sum(
        p.tackling * 0.5
        + p.strength * 0.3
        + p.speed * 0.1
        + p.skill * 0.1  # Speed helps cover ground
        for p in team.players
    )
    kicking_rating = sum(p.kicking for p in team.players)

    num_players = len(team.players)
    return {
        "attack": attack_rating / num_players,
        "defense": defense_rating / num_players,
        "kicking": kicking_rating
        / num_players,  # Average kicking skill for penalties/drops
    }


def simulate_match(home_team, away_team):
    """
    Simulates a match result based on aggregated player attributes + randomness.
    More detailed simulation determining tries and penalties.
    """
    home_ratings = calculate_team_ratings(home_team)
    away_ratings = calculate_team_ratings(away_team)

    # --- Simulate Tries ---
    # Compare attack of one team vs defense of the other
    # The difference influences the *chance* and *number* of tries
    # Normalization factor (tune this): Lower value = higher scores generally
    NORMALIZATION = 75

    home_try_potential = (
        home_ratings["attack"] - away_ratings["defense"]
    ) / NORMALIZATION
    away_try_potential = (
        away_ratings["attack"] - home_ratings["defense"]
    ) / NORMALIZATION

    # Base number of tries + potential + randomness
    # Adjust base (e.g., 1.5) and random range for desired scoring levels
    num_tries_home = max(0, round(1.5 + home_try_potential + random.uniform(-1.0, 1.5)))
    num_tries_away = max(0, round(1.5 + away_try_potential + random.uniform(-1.0, 1.5)))

    home_score = 0
    for _ in range(num_tries_home):
        home_score += TRY_POINTS
        # Conversion success rate - slightly influenced by average kicking skill?
        conversion_chance = (
            0.65 + (home_ratings["kicking"] - 50) / 200
        )  # Small influence
        if random.random() < max(0.1, min(0.95, conversion_chance)):
            home_score += CONVERSION_POINTS

    away_score = 0
    for _ in range(num_tries_away):
        away_score += TRY_POINTS
        conversion_chance = 0.65 + (away_ratings["kicking"] - 50) / 200
        if random.random() < max(0.1, min(0.95, conversion_chance)):
            away_score += CONVERSION_POINTS

    # --- Simulate Penalties / Drop Goals ---
    # Give a base chance for penalties, influenced slightly by attack/defense difference and kicking skill
    penalty_factor = 0.1  # Base chance factor

    home_penalty_chance = (
        penalty_factor
        + (home_try_potential / 10)
        + (home_ratings["kicking"] - 50) / 500
    )
    away_penalty_chance = (
        penalty_factor
        + (away_try_potential / 10)
        + (away_ratings["kicking"] - 50) / 500
    )

    # Simulate a few penalty opportunities
    for _ in range(
        random.randint(3, 7)
    ):  # More opportunities than actual successful kicks
        if random.random() < home_penalty_chance:
            home_score += 3
        if random.random() < away_penalty_chance:
            away_score += 3

    # --- Final adjustments (optional) ---
    # Add slight home advantage?
    # if random.random() < 0.1: home_score += random.choice([0, 3])

    return home_score, away_score
