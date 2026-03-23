"""
Bayesian Elo Rating System for F1.
Updates via all pairwise head-to-head comparisons per race.
"""
import json
import logging
import os

logger = logging.getLogger(__name__)


def expected_score(rating_a, rating_b):
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def update_elo(ratings, race_result, k_veteran=32, k_rookie=48):
    new_ratings = dict(ratings)
    n = len(race_result)
    if n < 2:
        logger.warning("Need at least 2 drivers for Elo update, got %d", n)
        return new_ratings
    for i in range(n):
        for j in range(i + 1, n):
            da, db = race_result[i], race_result[j]
            if da not in new_ratings or db not in new_ratings:
                continue
            ra, rb = new_ratings[da], new_ratings[db]
            ea = expected_score(ra, rb)
            eb = expected_score(rb, ra)
            k_a = k_rookie if ra < 1750 else k_veteran
            k_b = k_rookie if rb < 1750 else k_veteran
            scale = 1.0 / (n - 1)
            new_ratings[da] = ra + k_a * scale * (1.0 - ea)
            new_ratings[db] = rb + k_b * scale * (0.0 - eb)
    return new_ratings


def save_elo(ratings, path="data/elo_ratings.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(ratings, f, indent=2)
    logger.info("Elo ratings saved to %s", path)


def load_elo(path="data/elo_ratings.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.warning("Invalid elo data format in %s", path)
            return {}
        return data
    return {}
