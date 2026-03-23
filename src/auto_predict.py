"""
Automated Prediction Pipeline.
Called by GitHub Actions to generate predictions with latest data.
"""
import json
import logging
import os

import pandas as pd

from src.config import (
    GRID, DRIVER_ELO, TEAM_PACE, TEAM_FORM, MODEL_WEIGHTS, RACE, WEATHER,
    SEASON_MOMENTUM, GRID_POSITION, grid_position_score,
)
from src.circuit_regression import all_circuit_fits
from src.weather_engine import all_weather_modifiers
from src.monte_carlo import simulate_race
from src.kelly import find_value_bets
from src.elo_system import load_elo

logger = logging.getLogger(__name__)


def build_composites():
    elo = load_elo() or DRIVER_ELO
    circuit_fits = all_circuit_fits()
    weather_mods = all_weather_modifiers()
    w = dict(MODEL_WEIGHTS)

    # When GRID_POSITION is empty, redistribute its weight proportionally
    has_grid = bool(GRID_POSITION)
    if not has_grid and "grid_position" in w:
        gp_weight = w.pop("grid_position")
        remaining = sum(w.values())
        if remaining > 0:
            for k in w:
                w[k] = w[k] + gp_weight * (w[k] / remaining)

    composites = {}
    for driver, team in GRID.items():
        e = elo.get(driver, 1500)
        elo_norm = min(100, max(0, (e - 1400) / (2200 - 1400) * 100))
        cf = circuit_fits.get(driver, 70)
        # B2 FIX: Use actual TEAM_FORM dict instead of duplicating reliability
        tf = TEAM_FORM.get(team, 50)
        wm = weather_mods.get(driver, 0.95)
        tp = TEAM_PACE.get(team, {})
        rel = tp.get("reliability", 70)
        momentum = SEASON_MOMENTUM.get(driver, 30)

        composite = (
            w["elo"] * elo_norm +
            w["circuit_fit"] * cf +
            w["team_form"] * tf +
            w["weather"] * (wm * 100) +
            w["reliability"] * rel +
            w["season_momentum"] * momentum
        )

        if has_grid and "grid_position" in w:
            gp = GRID_POSITION.get(driver, 22)
            composite += w["grid_position"] * grid_position_score(gp)

        composites[driver] = round(composite, 2)
    return composites


def run_prediction():
    composites = build_composites()
    results = simulate_race(composites)
    win_bets = find_value_bets(results, "win")
    podium_bets = find_value_bets(results, "podium")
    rows = []
    for driver in sorted(results.keys(), key=lambda d: results[d]["win_pct"], reverse=True):
        r = results[driver]
        rows.append({
            "Driver": driver,
            "Team": GRID.get(driver, ""),
            "Composite": composites.get(driver, 0),
            "Win%": r["win_pct"],
            "Podium%": r["podium_pct"],
            "Top6%": r["top6_pct"],
        })
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(rows)
    race_name = RACE["name"].replace(" ", "_")
    df.to_csv(f"output/{race_name}_predictions.csv", index=False)
    bets_data = {"win_bets": win_bets, "podium_bets": podium_bets}
    with open(f"output/{race_name}_kelly.json", "w") as f:
        json.dump(bets_data, f, indent=2)
    return df, bets_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    df, bets = run_prediction()
    logger.info("\n%s", df.to_string(index=False))
    logger.info("\nValue Bets:")
    for b in bets["win_bets"][:5]:
        logger.info("  %s %s Win @%s | Model: %s%% | Edge: %spp",
                     b["verdict"], b["driver"], b["bookie_odds"], b["model_pct"], b["edge_pp"])
