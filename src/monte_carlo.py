"""
Monte Carlo Race Simulator - 10,000 iterations.
Models: variance, DNF, safety car, rain, T1 incidents.
"""
import logging

import numpy as np

from src.config import MC_SETTINGS, GRID, TEAM_PACE, WEATHER

logger = logging.getLogger(__name__)


def simulate_race(composites, n_sims=None):
    cfg = MC_SETTINGS
    n_sims = n_sims or cfg["n_simulations"]
    drivers = list(composites.keys())
    n_drivers = len(drivers)
    if n_drivers == 0:
        logger.warning("No drivers in composites, returning empty results")
        return {}
    base_scores = np.array([composites[d] for d in drivers])
    # B7 FIX: Use WEATHER["rain_prob"] instead of hardcoded 0.10
    rain_prob = WEATHER.get("rain_prob", 0.10)
    results = {d: {"wins": 0, "podiums": 0, "top6": 0, "positions": {}} for d in drivers}
    for _ in range(n_sims):
        noise = np.random.normal(0, cfg["variance_sigma"], n_drivers)
        sim_scores = base_scores * (1 + noise)
        dnf_mask = np.random.random(n_drivers) < cfg["dnf_base_rate"]
        if np.random.random() < cfg["t1_incident_prob"]:
            n_victims = np.random.randint(1, 4)
            victims = np.random.choice(n_drivers, size=min(n_victims, n_drivers), replace=False)
            dnf_mask[victims] = True
        if np.random.random() < cfg["safety_car_prob"]:
            alive = sim_scores[~dnf_mask]
            mean_score = np.mean(alive) if len(alive) > 0 else np.mean(sim_scores)
            sim_scores = sim_scores * (1 - cfg["sc_compression_factor"]) + mean_score * cfg["sc_compression_factor"]
        rain_roll = np.random.random()
        if rain_roll < rain_prob:
            for idx, d in enumerate(drivers):
                team = GRID.get(d, "")
                rain_skill = TEAM_PACE.get(team, {}).get("rain", 0.85)
                sim_scores[idx] *= (1.0 + (rain_skill - 0.85) * cfg["rain_amplifier"])
        sim_scores[dnf_mask] = 0
        ranking = np.argsort(-sim_scores)
        for pos, idx in enumerate(ranking):
            d = drivers[idx]
            finish = pos + 1
            results[d]["positions"][finish] = results[d]["positions"].get(finish, 0) + 1
            if finish == 1:
                results[d]["wins"] += 1
            if finish <= 3:
                results[d]["podiums"] += 1
            if finish <= 6:
                results[d]["top6"] += 1
    for d in drivers:
        results[d]["win_pct"] = round(results[d]["wins"] / n_sims * 100, 1)
        results[d]["podium_pct"] = round(results[d]["podiums"] / n_sims * 100, 1)
        results[d]["top6_pct"] = round(results[d]["top6"] / n_sims * 100, 1)
    return results
