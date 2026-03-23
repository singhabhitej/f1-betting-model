"""
Automated Prediction Pipeline.
Called by GitHub Actions to generate predictions with latest data.
"""
import json
import os
import pandas as pd
from src.config import GRID, DRIVER_ELO, TEAM_PACE, MODEL_WEIGHTS, RACE, WEATHER
from src.circuit_regression import all_circuit_fits
from src.weather_engine import all_weather_modifiers
from src.monte_carlo import simulate_race
from src.kelly import find_value_bets
from src.elo_system import load_elo

def build_composites():
    elo = load_elo() or DRIVER_ELO
    circuit_fits = all_circuit_fits()
    weather_mods = all_weather_modifiers()
    w = MODEL_WEIGHTS
    composites = {}
    for driver, team in GRID.items():
        e = elo.get(driver, 1500)
        elo_norm = (e - 1400) / (2200 - 1400) * 100
        cf = circuit_fits.get(driver, 70)
        tp = TEAM_PACE.get(team, {})
        team_form = tp.get("reliability", 70)
        wm = weather_mods.get(driver, 0.95)
        rel = tp.get("reliability", 70)
        composite = (
            w["elo"] * elo_norm +
            w["circuit_fit"] * cf +
            w["team_form"] * team_form +
            w["weather"] * (wm * 100) +
            w["reliability"] * rel
        )
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
    df, bets = run_prediction()
    print(df.to_string(index=False))
    print("\nValue Bets:")
    for b in bets["win_bets"][:5]:
        print(f"  {b['verdict']} {b['driver']} Win @{b['bookie_odds']} | Model: {b['model_pct']}% | Edge: {b['edge_pp']}pp")
