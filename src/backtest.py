"""
Backtesting Module.
Runs the model against historical race results from Rounds 1-2 to evaluate accuracy.
Calculates Brier score and calibration metrics.
"""
import logging

import numpy as np

from src.config import GRID
from src.elo_system import expected_score
from src.circuit_regression import circuit_fit_score
from src.weather_engine import weather_modifier
from src.monte_carlo import simulate_race

logger = logging.getLogger(__name__)

# ── Historical race data: Rounds 1-2 of 2026 season ──
HISTORICAL_RACES = [
    {
        "round": 1,
        "name": "Australian Grand Prix",
        "circuit_profile": {"power": 85, "aero": 70, "traction": 80, "tyre_deg": 75},
        "weather": {
            "air_temp_c": 22, "track_temp_c": 35, "rain_prob": 0.05,
            "wind_kph": 12, "humidity": 0.45,
            "optimal_track_temp_min": 28, "optimal_track_temp_max": 45,
        },
        "elo_snapshot": {
            "Verstappen": 2169, "Norris": 2053, "Leclerc": 2031,
            "Russell": 2000, "Hamilton": 1998, "Piastri": 1957,
            "Alonso": 1899, "Sainz": 1880, "Antonelli": 1847,
            "Gasly": 1810, "Albon": 1775, "Hulkenberg": 1743,
            "Bearman": 1720, "Stroll": 1710, "Lawson": 1700,
            "Bortoleto": 1690, "Hadjar": 1670, "Lindblad": 1660,
            "Colapinto": 1650, "Ocon": 1700, "Bottas": 1680, "Perez": 1670,
        },
        "team_pace": {
            "Mercedes": {"power": 95, "aero": 93, "traction": 90, "tyre_deg": 88, "reliability": 95, "cold_tyre": 0.90, "crosswind": 0.998, "rain": 0.92},
            "Ferrari": {"power": 88, "aero": 90, "traction": 85, "tyre_deg": 82, "reliability": 90, "cold_tyre": 0.82, "crosswind": 0.990, "rain": 0.88},
            "McLaren": {"power": 82, "aero": 85, "traction": 80, "tyre_deg": 80, "reliability": 85, "cold_tyre": 0.87, "crosswind": 0.992, "rain": 0.85},
            "Red Bull": {"power": 90, "aero": 82, "traction": 75, "tyre_deg": 78, "reliability": 80, "cold_tyre": 0.95, "crosswind": 0.988, "rain": 0.90},
            "Haas": {"power": 78, "aero": 70, "traction": 70, "tyre_deg": 70, "reliability": 78, "cold_tyre": 0.83, "crosswind": 0.985, "rain": 0.76},
            "Racing Bulls": {"power": 82, "aero": 70, "traction": 72, "tyre_deg": 72, "reliability": 76, "cold_tyre": 0.85, "crosswind": 0.986, "rain": 0.79},
            "Alpine": {"power": 80, "aero": 72, "traction": 72, "tyre_deg": 74, "reliability": 75, "cold_tyre": 0.84, "crosswind": 0.988, "rain": 0.80},
            "Audi": {"power": 76, "aero": 68, "traction": 68, "tyre_deg": 68, "reliability": 72, "cold_tyre": 0.81, "crosswind": 0.984, "rain": 0.74},
            "Williams": {"power": 80, "aero": 65, "traction": 65, "tyre_deg": 66, "reliability": 70, "cold_tyre": 0.82, "crosswind": 0.983, "rain": 0.75},
            "Aston Martin": {"power": 78, "aero": 75, "traction": 70, "tyre_deg": 72, "reliability": 60, "cold_tyre": 0.80, "crosswind": 0.982, "rain": 0.78},
            "Cadillac": {"power": 70, "aero": 60, "traction": 60, "tyre_deg": 62, "reliability": 65, "cold_tyre": 0.78, "crosswind": 0.980, "rain": 0.70},
        },
        "team_form": {
            "Mercedes": 90, "Ferrari": 75, "McLaren": 70, "Red Bull": 65,
            "Haas": 55, "Racing Bulls": 50, "Alpine": 48, "Audi": 40,
            "Williams": 38, "Aston Martin": 30, "Cadillac": 25,
        },
        "result": [
            "Russell", "Antonelli", "Leclerc", "Hamilton", "Norris",
            "Verstappen", "Bearman", "Lindblad", "Bortoleto", "Gasly",
            "Ocon", "Albon", "Lawson", "Colapinto", "Sainz", "Perez",
        ],
        # DNF: Stroll, Alonso, Bottas, Hadjar; DNS: Piastri
        "winner": "Russell",
    },
    {
        "round": 2,
        "name": "Chinese Grand Prix",
        "circuit_profile": {"power": 85, "aero": 70, "traction": 80, "tyre_deg": 75},
        "weather": {
            "air_temp_c": 12, "track_temp_c": 18, "rain_prob": 0.10,
            "wind_kph": 18, "humidity": 0.65,
            "optimal_track_temp_min": 28, "optimal_track_temp_max": 45,
        },
        "elo_snapshot": {
            "Russell": 2050, "Antonelli": 1920, "Leclerc": 2031,
            "Hamilton": 1998, "Norris": 2040, "Verstappen": 2140,
            "Piastri": 1957, "Bearman": 1760, "Gasly": 1810,
            "Lawson": 1700, "Lindblad": 1700, "Hadjar": 1650,
            "Sainz": 1860, "Colapinto": 1650, "Hulkenberg": 1743,
            "Ocon": 1700, "Bortoleto": 1690, "Alonso": 1880,
            "Bottas": 1680, "Perez": 1670, "Stroll": 1700, "Albon": 1775,
        },
        "team_pace": {
            "Mercedes": {"power": 95, "aero": 96, "traction": 93, "tyre_deg": 92, "reliability": 97, "cold_tyre": 0.92, "crosswind": 0.998, "rain": 0.94},
            "Ferrari": {"power": 90, "aero": 91, "traction": 88, "tyre_deg": 85, "reliability": 88, "cold_tyre": 0.88, "crosswind": 0.994, "rain": 0.90},
            "McLaren": {"power": 88, "aero": 88, "traction": 84, "tyre_deg": 82, "reliability": 60, "cold_tyre": 0.85, "crosswind": 0.990, "rain": 0.86},
            "Red Bull": {"power": 82, "aero": 80, "traction": 78, "tyre_deg": 76, "reliability": 70, "cold_tyre": 0.83, "crosswind": 0.986, "rain": 0.82},
            "Haas": {"power": 80, "aero": 78, "traction": 76, "tyre_deg": 74, "reliability": 82, "cold_tyre": 0.82, "crosswind": 0.984, "rain": 0.78},
            "Racing Bulls": {"power": 78, "aero": 76, "traction": 74, "tyre_deg": 72, "reliability": 78, "cold_tyre": 0.81, "crosswind": 0.982, "rain": 0.77},
            "Alpine": {"power": 76, "aero": 75, "traction": 72, "tyre_deg": 70, "reliability": 76, "cold_tyre": 0.80, "crosswind": 0.980, "rain": 0.76},
            "Audi": {"power": 74, "aero": 72, "traction": 70, "tyre_deg": 68, "reliability": 72, "cold_tyre": 0.79, "crosswind": 0.978, "rain": 0.74},
            "Williams": {"power": 72, "aero": 70, "traction": 68, "tyre_deg": 66, "reliability": 68, "cold_tyre": 0.78, "crosswind": 0.976, "rain": 0.72},
            "Aston Martin": {"power": 68, "aero": 66, "traction": 64, "tyre_deg": 62, "reliability": 55, "cold_tyre": 0.76, "crosswind": 0.972, "rain": 0.70},
            "Cadillac": {"power": 65, "aero": 62, "traction": 60, "tyre_deg": 60, "reliability": 58, "cold_tyre": 0.74, "crosswind": 0.970, "rain": 0.68},
        },
        "team_form": {
            "Mercedes": 95, "Ferrari": 78, "McLaren": 55, "Red Bull": 50,
            "Haas": 60, "Racing Bulls": 52, "Alpine": 48, "Audi": 38,
            "Williams": 35, "Aston Martin": 22, "Cadillac": 25,
        },
        "result": [
            "Antonelli", "Russell", "Hamilton", "Leclerc",
            "Bearman", "Gasly", "Lawson", "Hadjar",
            "Sainz", "Colapinto", "Hulkenberg", "Lindblad",
            "Bottas", "Ocon", "Perez",
        ],
        # DNF: Verstappen, Alonso, Stroll; DNS: Piastri, Norris, Bortoleto, Albon
        "winner": "Antonelli",
    },
]


def _build_composites_for_race(race_data):
    """Build composite scores using historical config for a specific race."""
    elo_snap = race_data["elo_snapshot"]
    cp = race_data["circuit_profile"]
    w_data = race_data["weather"]
    tp_data = race_data["team_pace"]
    tf_data = race_data["team_form"]

    weights = {"elo": 0.25, "circuit_fit": 0.25, "team_form": 0.20,
               "weather": 0.10, "reliability": 0.10, "season_momentum": 0.10}

    composites = {}
    for driver, team in GRID.items():
        e = elo_snap.get(driver, 1500)
        elo_norm = min(100, max(0, (e - 1400) / (2200 - 1400) * 100))

        tp = tp_data.get(team, {})
        total_w = cp["power"] + cp["aero"] + cp["traction"] + cp["tyre_deg"]
        if total_w > 0:
            cf = (
                cp["power"] * tp.get("power", 50) +
                cp["aero"] * tp.get("aero", 50) +
                cp["traction"] * tp.get("traction", 50) +
                cp["tyre_deg"] * tp.get("tyre_deg", 50)
            ) / total_w
        else:
            cf = 50.0

        tf = tf_data.get(team, 50)
        rel = tp.get("reliability", 70)

        # Simple weather modifier
        track_temp = w_data["track_temp_c"]
        opt_min = w_data["optimal_track_temp_min"]
        if track_temp < opt_min:
            cold_gap = (opt_min - track_temp) / opt_min
            wm = 1.0 - cold_gap * (1.0 - tp.get("cold_tyre", 0.85))
        else:
            wm = 1.0

        composite = (
            weights["elo"] * elo_norm +
            weights["circuit_fit"] * cf +
            weights["team_form"] * tf +
            weights["weather"] * (wm * 100) +
            weights["reliability"] * rel +
            weights["season_momentum"] * 50  # neutral baseline for backtest
        )
        composites[driver] = round(composite, 2)
    return composites


def brier_score(predicted_probs, actual_outcomes):
    """Calculate Brier score: lower is better (0 = perfect, 1 = worst)."""
    if not predicted_probs:
        return 1.0
    return sum((p - a) ** 2 for p, a in zip(predicted_probs, actual_outcomes)) / len(predicted_probs)


def run_backtest():
    """Run the model against historical race results and calculate accuracy metrics."""
    all_win_probs = []
    all_win_outcomes = []
    all_podium_probs = []
    all_podium_outcomes = []

    for race in HISTORICAL_RACES:
        logger.info("=" * 60)
        logger.info("BACKTEST: Round %d - %s", race["round"], race["name"])
        logger.info("=" * 60)

        composites = _build_composites_for_race(race)
        mc_results = simulate_race(composites, n_sims=10000)

        winner = race["winner"]
        result = race["result"]
        podium = result[:3] if len(result) >= 3 else result

        # Log top predictions vs actual result
        sorted_by_win = sorted(mc_results.keys(),
                               key=lambda d: mc_results[d]["win_pct"], reverse=True)

        logger.info("\nModel Top 5 vs Actual:")
        for i, d in enumerate(sorted_by_win[:5]):
            actual_pos = result.index(d) + 1 if d in result else "DNF/DNS"
            logger.info("  Model #%d: %s (Win: %.1f%%) — Actual: P%s",
                        i + 1, d, mc_results[d]["win_pct"], actual_pos)

        logger.info("\nActual Winner: %s (Model win%%: %.1f%%, Model rank: #%d)",
                    winner,
                    mc_results.get(winner, {}).get("win_pct", 0),
                    sorted_by_win.index(winner) + 1 if winner in sorted_by_win else -1)

        # Collect probabilities for Brier score
        for driver in mc_results:
            win_prob = mc_results[driver]["win_pct"] / 100.0
            all_win_probs.append(win_prob)
            all_win_outcomes.append(1.0 if driver == winner else 0.0)

            podium_prob = mc_results[driver]["podium_pct"] / 100.0
            all_podium_probs.append(podium_prob)
            all_podium_outcomes.append(1.0 if driver in podium else 0.0)

    # Calculate aggregate metrics
    win_brier = brier_score(all_win_probs, all_win_outcomes)
    podium_brier = brier_score(all_podium_probs, all_podium_outcomes)

    logger.info("\n" + "=" * 60)
    logger.info("BACKTEST SUMMARY (Rounds 1-2)")
    logger.info("=" * 60)
    logger.info("Win Brier Score:    %.4f (lower is better, 0=perfect)", win_brier)
    logger.info("Podium Brier Score: %.4f", podium_brier)

    # Calibration: how well do predicted probabilities match observed frequencies
    # Bucket predictions into ranges and check calibration
    buckets = [(0, 0.05), (0.05, 0.15), (0.15, 0.30), (0.30, 0.50), (0.50, 1.0)]
    logger.info("\nWin Probability Calibration:")
    logger.info("  %-15s %-10s %-10s %-10s", "Range", "Predicted", "Actual", "Count")
    for low, high in buckets:
        indices = [i for i, p in enumerate(all_win_probs) if low <= p < high]
        if indices:
            avg_pred = np.mean([all_win_probs[i] for i in indices])
            avg_actual = np.mean([all_win_outcomes[i] for i in indices])
            logger.info("  %-15s %-10.3f %-10.3f %-10d",
                        f"{low:.0%}-{high:.0%}", avg_pred, avg_actual, len(indices))

    return {
        "win_brier": win_brier,
        "podium_brier": podium_brier,
        "races_evaluated": len(HISTORICAL_RACES),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_backtest()
