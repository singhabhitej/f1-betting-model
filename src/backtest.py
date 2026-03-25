"""
50-Race Backtesting Engine for F1 Betting Model.
Validates the model methodology against historical data (2024-2026).
Runs sequentially through races, maintaining evolving Elo ratings and team pace estimates.
"""
import json
import logging
import math
import os
from collections import defaultdict

import numpy as np
from scipy import stats as scipy_stats

from src.elo_system import update_elo

logger = logging.getLogger(__name__)

# ── Constants ──
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "historical_races.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
DEFAULT_N_SIMS = 5000  # Faster than production 10k, configurable

# Model weights — same as config.py but redistribute grid_position weight
# since we don't have qualifying data for historical races
BASE_WEIGHTS = {
    "elo": 0.20,
    "circuit_fit": 0.20,
    "team_form": 0.15,
    "grid_position": 0.15,
    "weather": 0.10,
    "reliability": 0.10,
    "season_momentum": 0.10,
}

# Redistribute grid_position weight proportionally to other factors
_gp_w = BASE_WEIGHTS["grid_position"]
_remaining = {k: v for k, v in BASE_WEIGHTS.items() if k != "grid_position"}
_total_remaining = sum(_remaining.values())
WEIGHTS = {k: v + _gp_w * (v / _total_remaining) for k, v in _remaining.items()}

# MC simulation settings
MC_SETTINGS = {
    "dnf_base_rate": 0.05,
    "safety_car_prob": 0.55,
    "sc_compression_factor": 0.4,
    "t1_incident_prob": 0.15,
    "rain_amplifier": 1.8,
    "variance_sigma": 0.08,
}

# ── Pre-season team pace baselines ──
PRESEASON_PACE = {
    2024: {
        "Red Bull": {"power": 95, "aero": 90, "traction": 88, "tyre_deg": 85, "reliability": 92, "cold_tyre": 0.90, "crosswind": 0.995, "rain": 0.90},
        "Ferrari": {"power": 90, "aero": 88, "traction": 85, "tyre_deg": 82, "reliability": 85, "cold_tyre": 0.86, "crosswind": 0.992, "rain": 0.88},
        "McLaren": {"power": 88, "aero": 85, "traction": 82, "tyre_deg": 80, "reliability": 88, "cold_tyre": 0.85, "crosswind": 0.990, "rain": 0.86},
        "Mercedes": {"power": 85, "aero": 82, "traction": 80, "tyre_deg": 78, "reliability": 90, "cold_tyre": 0.84, "crosswind": 0.988, "rain": 0.85},
        "Aston Martin": {"power": 80, "aero": 78, "traction": 76, "tyre_deg": 74, "reliability": 82, "cold_tyre": 0.82, "crosswind": 0.985, "rain": 0.80},
        "Alpine": {"power": 78, "aero": 72, "traction": 72, "tyre_deg": 70, "reliability": 78, "cold_tyre": 0.80, "crosswind": 0.982, "rain": 0.78},
        "Williams": {"power": 76, "aero": 68, "traction": 70, "tyre_deg": 68, "reliability": 75, "cold_tyre": 0.79, "crosswind": 0.980, "rain": 0.76},
        "Haas": {"power": 74, "aero": 70, "traction": 72, "tyre_deg": 72, "reliability": 76, "cold_tyre": 0.78, "crosswind": 0.978, "rain": 0.75},
        "Racing Bulls": {"power": 78, "aero": 72, "traction": 74, "tyre_deg": 72, "reliability": 78, "cold_tyre": 0.80, "crosswind": 0.982, "rain": 0.78},
        "Sauber": {"power": 70, "aero": 65, "traction": 65, "tyre_deg": 65, "reliability": 70, "cold_tyre": 0.76, "crosswind": 0.975, "rain": 0.72},
    },
    2025: {
        "Red Bull": {"power": 93, "aero": 88, "traction": 85, "tyre_deg": 82, "reliability": 90, "cold_tyre": 0.89, "crosswind": 0.994, "rain": 0.89},
        "McLaren": {"power": 92, "aero": 90, "traction": 88, "tyre_deg": 85, "reliability": 90, "cold_tyre": 0.88, "crosswind": 0.993, "rain": 0.88},
        "Ferrari": {"power": 88, "aero": 86, "traction": 84, "tyre_deg": 80, "reliability": 88, "cold_tyre": 0.86, "crosswind": 0.991, "rain": 0.87},
        "Mercedes": {"power": 86, "aero": 84, "traction": 82, "tyre_deg": 80, "reliability": 90, "cold_tyre": 0.85, "crosswind": 0.990, "rain": 0.86},
        "Racing Bulls": {"power": 80, "aero": 74, "traction": 74, "tyre_deg": 72, "reliability": 78, "cold_tyre": 0.81, "crosswind": 0.983, "rain": 0.79},
        "Aston Martin": {"power": 78, "aero": 76, "traction": 74, "tyre_deg": 72, "reliability": 80, "cold_tyre": 0.81, "crosswind": 0.984, "rain": 0.79},
        "Alpine": {"power": 76, "aero": 72, "traction": 70, "tyre_deg": 68, "reliability": 76, "cold_tyre": 0.79, "crosswind": 0.981, "rain": 0.77},
        "Haas": {"power": 75, "aero": 72, "traction": 72, "tyre_deg": 70, "reliability": 78, "cold_tyre": 0.79, "crosswind": 0.980, "rain": 0.76},
        "Williams": {"power": 74, "aero": 70, "traction": 70, "tyre_deg": 68, "reliability": 75, "cold_tyre": 0.78, "crosswind": 0.979, "rain": 0.75},
        "Sauber": {"power": 72, "aero": 68, "traction": 66, "tyre_deg": 66, "reliability": 72, "cold_tyre": 0.77, "crosswind": 0.977, "rain": 0.73},
    },
    2026: {
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
}

# Initial Elo ratings (reasonable pre-2024 estimates)
INITIAL_ELO = {
    # 2024 grid
    "Verstappen": 2200, "Perez": 1850, "Norris": 1950, "Piastri": 1880,
    "Leclerc": 2000, "Sainz": 1920, "Hamilton": 2050, "Russell": 1980,
    "Alonso": 1900, "Stroll": 1720, "Ocon": 1780, "Gasly": 1800,
    "Magnussen": 1700, "Hulkenberg": 1750, "Tsunoda": 1760, "Ricciardo": 1800,
    "Zhou": 1650, "Bottas": 1730, "Albon": 1780, "Sargeant": 1550,
    # Mid-season 2024 additions
    "Colapinto": 1600, "Lawson": 1700, "Bearman": 1650,
    # 2025 rookies
    "Antonelli": 1700, "Hadjar": 1650, "Bortoleto": 1600, "Doohan": 1600,
    # 2026 additions
    "Lindblad": 1600, "Bottas": 1730,
}


# ── Helper Functions ──

def load_historical_races(path=None):
    """Load races from the historical data JSON file."""
    if path is None:
        path = DATA_PATH
    with open(path) as f:
        return json.load(f)


def brier_score(predicted_probs, actual_outcomes):
    """Calculate Brier score: lower is better (0 = perfect, 1 = worst).

    Args:
        predicted_probs: list of predicted probabilities (0-1)
        actual_outcomes: list of actual binary outcomes (0 or 1)

    Returns:
        Brier score (float)
    """
    if not predicted_probs:
        return 1.0
    return sum((p - a) ** 2 for p, a in zip(predicted_probs, actual_outcomes)) / len(predicted_probs)


def log_loss(predicted_probs, actual_outcomes, eps=1e-15):
    """Calculate log loss (cross-entropy loss).

    Args:
        predicted_probs: list of predicted probabilities (0-1)
        actual_outcomes: list of actual binary outcomes (0 or 1)
        eps: small constant to avoid log(0)

    Returns:
        Log loss (float), lower is better
    """
    if not predicted_probs:
        return float("inf")
    total = 0.0
    for p, a in zip(predicted_probs, actual_outcomes):
        p_clipped = max(eps, min(1 - eps, p))
        total += -(a * math.log(p_clipped) + (1 - a) * math.log(1 - p_clipped))
    return total / len(predicted_probs)


def calibration_buckets(predicted_probs, actual_outcomes, bucket_edges=None):
    """Calculate calibration by probability bucket.

    Returns list of dicts with keys: range, avg_predicted, avg_actual, count.
    """
    if bucket_edges is None:
        bucket_edges = [(0, 0.05), (0.05, 0.15), (0.15, 0.30), (0.30, 0.50), (0.50, 1.0)]

    buckets = []
    for low, high in bucket_edges:
        indices = [i for i, p in enumerate(predicted_probs) if low <= p < high]
        if indices:
            avg_pred = np.mean([predicted_probs[i] for i in indices])
            avg_actual = np.mean([actual_outcomes[i] for i in indices])
            buckets.append({
                "range": f"{low:.0%}-{high:.0%}",
                "avg_predicted": round(float(avg_pred), 4),
                "avg_actual": round(float(avg_actual), 4),
                "count": len(indices),
            })
    return buckets


def spearman_correlation(predicted_order, actual_order):
    """Calculate Spearman rank correlation between predicted and actual finish orders.

    Args:
        predicted_order: list of driver names in predicted order (best first)
        actual_order: list of driver names in actual finish order (best first)

    Returns:
        Spearman correlation coefficient (-1 to 1), higher is better
    """
    # Find common drivers
    common = [d for d in predicted_order if d in actual_order]
    if len(common) < 3:
        return 0.0

    pred_ranks = []
    actual_ranks = []
    for d in common:
        pred_ranks.append(predicted_order.index(d) + 1)
        actual_ranks.append(actual_order.index(d) + 1)

    corr, _ = scipy_stats.spearmanr(pred_ranks, actual_ranks)
    return round(float(corr), 4) if not np.isnan(corr) else 0.0


def podium_overlap(predicted_top3, actual_top3):
    """Count how many of predicted top 3 appeared in actual top 3.

    Returns int (0-3).
    """
    return len(set(predicted_top3[:3]) & set(actual_top3[:3]))


# ── Team Pace Estimation ──

class TeamPaceTracker:
    """Tracks team pace using exponential moving average of results.
    Starts from pre-season baselines and adapts based on race outcomes.
    """

    def __init__(self, alpha=0.15):
        """
        Args:
            alpha: EMA smoothing factor (0-1). Higher = more weight on recent results.
        """
        self.alpha = alpha
        self.current_pace = {}
        self._initialized_year = None

    def initialize(self, year):
        """Set up pre-season baselines for a given year."""
        if year in PRESEASON_PACE:
            self.current_pace = {
                team: dict(pace) for team, pace in PRESEASON_PACE[year].items()
            }
        self._initialized_year = year

    def get_pace(self, team):
        """Get current team pace estimate."""
        return self.current_pace.get(team, {
            "power": 70, "aero": 70, "traction": 70, "tyre_deg": 70,
            "reliability": 70, "cold_tyre": 0.80, "crosswind": 0.980, "rain": 0.75,
        })

    def update_from_result(self, result_order, grid_map):
        """Update team pace estimates based on race results.

        Uses finishing position to derive a performance signal and applies EMA.
        """
        if not result_order:
            return

        n = len(result_order)
        # Calculate team performance scores from result
        team_scores = defaultdict(list)
        for pos, driver in enumerate(result_order):
            team = grid_map.get(driver)
            if team:
                # Convert position to 0-100 performance score
                score = max(0, 100 * (1 - pos / n))
                team_scores[team].append(score)

        # Update pace for each team with EMA
        for team, scores in team_scores.items():
            avg_score = np.mean(scores)
            if team not in self.current_pace:
                continue

            pace = self.current_pace[team]
            # Adjust core metrics based on performance signal
            # Positive result nudges pace up slightly, negative nudges down
            adjustment = (avg_score - 50) / 50 * 3  # ±3 points max per race

            for key in ["power", "aero", "traction", "tyre_deg"]:
                if key in pace:
                    old_val = pace[key]
                    new_signal = max(40, min(100, old_val + adjustment))
                    pace[key] = round(old_val * (1 - self.alpha) + new_signal * self.alpha, 1)

            # Don't adjust weather-related or reliability from results as aggressively
            if avg_score > 70:
                pace["reliability"] = min(98, pace.get("reliability", 70) + 0.5)
            elif avg_score < 30:
                pace["reliability"] = max(50, pace.get("reliability", 70) - 0.5)


# ── Team Form Tracker ──

class TeamFormTracker:
    """Tracks rolling 5-race constructor form."""

    def __init__(self, window=5):
        self.window = window
        self.history = defaultdict(list)  # team -> list of recent scores

    def get_form(self, team):
        """Get team form score (0-100) based on recent results."""
        history = self.history.get(team, [])
        if not history:
            return 50.0
        return round(np.mean(history[-self.window:]), 1)

    def update(self, result_order, grid_map):
        """Update form from race result."""
        n = len(result_order)
        team_points = defaultdict(float)

        # F1 points system (top 10 score)
        points = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

        for pos, driver in enumerate(result_order):
            team = grid_map.get(driver)
            if team:
                team_points[team] += points.get(pos + 1, 0)

        # Normalize to 0-100 scale (max possible = 43 for 1-2)
        max_possible = 43
        for team in set(grid_map.values()):
            score = min(100, team_points.get(team, 0) / max_possible * 100)
            self.history[team].append(score)


# ── Season Momentum Tracker ──

class MomentumTracker:
    """Tracks individual driver momentum over recent races."""

    def __init__(self, window=5):
        self.window = window
        self.history = defaultdict(list)

    def get_momentum(self, driver):
        """Get driver momentum score (0-100)."""
        history = self.history.get(driver, [])
        if not history:
            return 50.0
        # Weight recent results more heavily
        recent = history[-self.window:]
        weights = np.linspace(0.5, 1.0, len(recent))
        return round(float(np.average(recent, weights=weights)), 1)

    def update(self, result_order):
        """Update momentum from race result."""
        n = len(result_order)
        for pos, driver in enumerate(result_order):
            score = max(0, 100 * (1 - pos / max(n, 1)))
            self.history[driver].append(score)


# ── Monte Carlo Simulation (self-contained for backtest) ──

def simulate_race_backtest(composites, grid_map, team_pace, rain_prob, n_sims=DEFAULT_N_SIMS):
    """Run Monte Carlo simulation for a single race.

    Self-contained version that doesn't depend on global config (unlike src.monte_carlo).
    Uses the team_pace and weather data specific to this historical race.
    """
    cfg = MC_SETTINGS
    drivers = list(composites.keys())
    n_drivers = len(drivers)
    if n_drivers == 0:
        return {}

    base_scores = np.array([composites[d] for d in drivers])
    results = {d: {"wins": 0, "podiums": 0, "top6": 0, "positions": {}} for d in drivers}

    for _ in range(n_sims):
        noise = np.random.normal(0, cfg["variance_sigma"], n_drivers)
        sim_scores = base_scores * (1 + noise)

        # DNF
        dnf_mask = np.random.random(n_drivers) < cfg["dnf_base_rate"]

        # T1 incidents
        if np.random.random() < cfg["t1_incident_prob"]:
            n_victims = np.random.randint(1, 4)
            victims = np.random.choice(n_drivers, size=min(n_victims, n_drivers), replace=False)
            dnf_mask[victims] = True

        # Safety car compression
        if np.random.random() < cfg["safety_car_prob"]:
            alive = sim_scores[~dnf_mask]
            mean_score = np.mean(alive) if len(alive) > 0 else np.mean(sim_scores)
            sim_scores = sim_scores * (1 - cfg["sc_compression_factor"]) + mean_score * cfg["sc_compression_factor"]

        # Rain
        if np.random.random() < rain_prob:
            for idx, d in enumerate(drivers):
                team = grid_map.get(d, "")
                tp = team_pace.get(team, {})
                rain_skill = tp.get("rain", 0.85)
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


# ── Core Backtest Logic ──

def build_composites_for_race(
    elo_ratings, circuit_profile, weather, team_pace_map,
    team_form_map, momentum_map, grid_map
):
    """Build composite scores for a historical race.

    Same formula as auto_predict.py but uses race-specific data instead of globals.
    """
    composites = {}

    for driver in grid_map:
        team = grid_map[driver]
        tp = team_pace_map.get(team, {})

        # Elo normalized to 0-100
        e = elo_ratings.get(driver, 1500)
        elo_norm = min(100, max(0, (e - 1400) / (2200 - 1400) * 100))

        # Circuit fit: weighted average of team pace × circuit demands
        cp = circuit_profile
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

        # Team form
        tf = team_form_map.get(team, 50)

        # Reliability
        rel = tp.get("reliability", 70)

        # Weather modifier
        track_temp = weather.get("track_temp_c", 35)
        opt_min = 28  # Standard optimal range
        opt_max = 45
        if track_temp < opt_min:
            cold_gap = (opt_min - track_temp) / opt_min
            cold_factor = 1.0 - cold_gap * (1.0 - tp.get("cold_tyre", 0.85))
        elif track_temp > opt_max:
            hot_gap = (track_temp - opt_max) / opt_max
            tyre_deg = tp.get("tyre_deg", 70) / 100.0
            cold_factor = 1.0 - hot_gap * (1.0 - tyre_deg)
        else:
            cold_factor = 1.0

        wind = weather.get("wind_kph", 10)
        wind_factor = tp.get("crosswind", 0.99) ** ((wind - 10) / 10) if wind > 10 else 1.0

        air_temp = weather.get("air_temp_c", 25)
        density_bonus = 1.0 + max(0, (20 - air_temp)) * 0.001

        rain_prob = weather.get("rain_prob", 0.05)
        rain_factor = 1.0 - rain_prob * (1.0 - tp.get("rain", 0.85))

        wm = cold_factor * wind_factor * density_bonus * rain_factor

        # Season momentum
        momentum = momentum_map.get(driver, 50)

        # Composite
        composite = (
            WEIGHTS["elo"] * elo_norm +
            WEIGHTS["circuit_fit"] * cf +
            WEIGHTS["team_form"] * tf +
            WEIGHTS["weather"] * (wm * 100) +
            WEIGHTS["reliability"] * rel +
            WEIGHTS["season_momentum"] * momentum
        )

        composites[driver] = round(composite, 2)

    return composites


def run_backtest(n_sims=DEFAULT_N_SIMS, data_path=None, verbose=True):
    """Run the full 50-race backtest.

    Args:
        n_sims: Number of Monte Carlo simulations per race
        data_path: Path to historical_races.json (uses default if None)
        verbose: Whether to print detailed progress

    Returns:
        dict with all metrics and race-by-race results
    """
    np.random.seed(42)  # Reproducible results

    # Load data
    races = load_historical_races(data_path)
    if verbose:
        logger.info("Loaded %d historical races for backtest", len(races))

    # Initialize trackers
    elo_ratings = dict(INITIAL_ELO)
    pace_tracker = TeamPaceTracker(alpha=0.15)
    form_tracker = TeamFormTracker(window=5)
    momentum_tracker = MomentumTracker(window=5)

    current_year = None

    # Collectors for aggregate metrics
    all_win_probs = []
    all_win_outcomes = []
    all_podium_probs = []
    all_podium_outcomes = []
    all_top6_probs = []
    all_top6_outcomes = []
    race_results = []
    spearman_correlations = []
    podium_overlaps = []
    winner_in_top_n = {1: 0, 3: 0, 5: 0}

    for race_idx, race in enumerate(races):
        year = race["year"]
        name = race["name"]
        circuit = race.get("circuit", "Unknown")
        result = race["result"]
        winner = race["winner"]
        actual_podium = result[:3] if len(result) >= 3 else result
        circuit_profile = race["circuit_profile"]
        weather = race["weather"]
        grid_map = race.get("grid", {})

        # Initialize team pace for new season
        if year != current_year:
            pace_tracker.initialize(year)
            current_year = year
            if verbose:
                logger.info("\n{'='*60}")
                logger.info("  SEASON %d — Initializing pre-season baselines", year)
                logger.info("{'='*60}")

        # Get current state for this race
        team_pace_map = {team: pace_tracker.get_pace(team) for team in set(grid_map.values())}
        team_form_map = {team: form_tracker.get_form(team) for team in set(grid_map.values())}
        momentum_map = {d: momentum_tracker.get_momentum(d) for d in grid_map}

        # Build composites
        composites = build_composites_for_race(
            elo_ratings, circuit_profile, weather,
            team_pace_map, team_form_map, momentum_map, grid_map
        )

        if not composites:
            if verbose:
                logger.warning("Skipping race %s — no composites generated", name)
            continue

        # Run Monte Carlo simulation
        rain_prob = weather.get("rain_prob", 0.05)
        mc_results = simulate_race_backtest(composites, grid_map, team_pace_map, rain_prob, n_sims)

        # Rank drivers by predicted win probability
        predicted_order = sorted(mc_results.keys(), key=lambda d: mc_results[d]["win_pct"], reverse=True)
        predicted_top3 = predicted_order[:3]

        # ── Collect metrics ──

        # Win/podium/top6 probabilities vs actuals
        for driver in mc_results:
            win_prob = mc_results[driver]["win_pct"] / 100.0
            podium_prob = mc_results[driver]["podium_pct"] / 100.0
            top6_prob = mc_results[driver]["top6_pct"] / 100.0

            all_win_probs.append(win_prob)
            all_win_outcomes.append(1.0 if driver == winner else 0.0)
            all_podium_probs.append(podium_prob)
            all_podium_outcomes.append(1.0 if driver in actual_podium else 0.0)
            all_top6_probs.append(top6_prob)
            all_top6_outcomes.append(1.0 if driver in result[:6] else 0.0)

        # Winner in top N
        for n in [1, 3, 5]:
            if winner in predicted_order[:n]:
                winner_in_top_n[n] += 1

        # Podium overlap
        overlap = podium_overlap(predicted_top3, actual_podium)
        podium_overlaps.append(overlap)

        # Spearman correlation
        corr = spearman_correlation(predicted_order, result)
        spearman_correlations.append(corr)

        # Store race result details
        winner_rank = predicted_order.index(winner) + 1 if winner in predicted_order else len(predicted_order)
        winner_prob = mc_results.get(winner, {}).get("win_pct", 0)

        race_detail = {
            "sequence": race.get("sequence", race_idx + 1),
            "year": year,
            "round": race["round"],
            "name": name,
            "circuit": circuit,
            "actual_winner": winner,
            "predicted_top3": predicted_top3,
            "actual_top3": actual_podium,
            "winner_predicted_rank": winner_rank,
            "winner_predicted_prob": winner_prob,
            "podium_overlap": overlap,
            "spearman_corr": corr,
        }
        race_results.append(race_detail)

        if verbose:
            logger.info(
                "Race %2d: %-30s | Winner: %-12s (Model rank #%d, %.1f%%) | Podium overlap: %d/3 | Spearman: %.3f",
                race_idx + 1, name, winner, winner_rank, winner_prob, overlap, corr
            )

        # ── Update state for next race ──
        # Update Elo from actual results
        finishers_with_elo = [d for d in result if d in elo_ratings]
        elo_ratings = update_elo(elo_ratings, finishers_with_elo)

        # Ensure all drivers in grid have Elo ratings
        for driver in grid_map:
            if driver not in elo_ratings:
                elo_ratings[driver] = 1600

        # Update trackers
        pace_tracker.update_from_result(result, grid_map)
        form_tracker.update(result, grid_map)
        momentum_tracker.update(result)

    # ── Calculate aggregate metrics ──
    n_races = len(race_results)

    win_brier = brier_score(all_win_probs, all_win_outcomes)
    podium_brier = brier_score(all_podium_probs, all_podium_outcomes)
    win_log_loss = log_loss(all_win_probs, all_win_outcomes)
    podium_log_loss = log_loss(all_podium_probs, all_podium_outcomes)

    win_calibration = calibration_buckets(all_win_probs, all_win_outcomes)
    podium_calibration = calibration_buckets(all_podium_probs, all_podium_outcomes)

    avg_spearman = float(np.mean(spearman_correlations)) if spearman_correlations else 0
    avg_podium_overlap = float(np.mean(podium_overlaps)) if podium_overlaps else 0

    # Era breakdowns
    eras = {
        "2024_early": [r for r in race_results if r["year"] == 2024 and r["round"] <= 10],
        "2024_late": [r for r in race_results if r["year"] == 2024 and r["round"] > 10],
        "2025_early": [r for r in race_results if r["year"] == 2025 and r["round"] <= 10],
        "2025_late": [r for r in race_results if r["year"] == 2025 and r["round"] > 10],
        "2026": [r for r in race_results if r["year"] == 2026],
    }

    era_metrics = {}
    for era_name, era_races in eras.items():
        if not era_races:
            continue
        era_metrics[era_name] = {
            "races": len(era_races),
            "avg_winner_rank": round(np.mean([r["winner_predicted_rank"] for r in era_races]), 2),
            "avg_winner_prob": round(np.mean([r["winner_predicted_prob"] for r in era_races]), 2),
            "avg_podium_overlap": round(np.mean([r["podium_overlap"] for r in era_races]), 2),
            "avg_spearman": round(np.mean([r["spearman_corr"] for r in era_races]), 4),
            "winner_top1_pct": round(sum(1 for r in era_races if r["winner_predicted_rank"] == 1) / len(era_races) * 100, 1),
            "winner_top3_pct": round(sum(1 for r in era_races if r["winner_predicted_rank"] <= 3) / len(era_races) * 100, 1),
        }

    # Compile full results
    results = {
        "n_races": n_races,
        "n_sims_per_race": n_sims,
        "metrics": {
            "win_brier_score": round(win_brier, 4),
            "podium_brier_score": round(podium_brier, 4),
            "win_log_loss": round(win_log_loss, 4),
            "podium_log_loss": round(podium_log_loss, 4),
            "winner_in_top1": round(winner_in_top_n[1] / n_races * 100, 1),
            "winner_in_top3": round(winner_in_top_n[3] / n_races * 100, 1),
            "winner_in_top5": round(winner_in_top_n[5] / n_races * 100, 1),
            "avg_podium_overlap": round(avg_podium_overlap, 2),
            "avg_spearman_correlation": round(avg_spearman, 4),
        },
        "win_calibration": win_calibration,
        "podium_calibration": podium_calibration,
        "era_breakdown": era_metrics,
        "race_results": race_results,
    }

    # ── Save outputs ──
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results_path = os.path.join(OUTPUT_DIR, "backtest_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    if verbose:
        logger.info("\nResults saved to %s", results_path)

    # Generate report
    report = generate_report(results)
    report_path = os.path.join(OUTPUT_DIR, "backtest_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    if verbose:
        logger.info("Report saved to %s", report_path)

    # Print summary
    if verbose:
        logger.info("\n" + "=" * 60)
        logger.info("BACKTEST SUMMARY — %d Races", n_races)
        logger.info("=" * 60)
        logger.info("Win Brier Score:       %.4f (lower is better)", win_brier)
        logger.info("Podium Brier Score:    %.4f", podium_brier)
        logger.info("Win Log Loss:          %.4f", win_log_loss)
        logger.info("Winner in Top 1:       %.1f%%", results["metrics"]["winner_in_top1"])
        logger.info("Winner in Top 3:       %.1f%%", results["metrics"]["winner_in_top3"])
        logger.info("Winner in Top 5:       %.1f%%", results["metrics"]["winner_in_top5"])
        logger.info("Avg Podium Overlap:    %.2f / 3", avg_podium_overlap)
        logger.info("Avg Spearman Corr:     %.4f", avg_spearman)

    return results


# ── Report Generator ──

def generate_report(results):
    """Generate a detailed Markdown backtest report."""
    m = results["metrics"]
    lines = [
        "# F1 Betting Model — 50-Race Backtest Report",
        "",
        "## Overview",
        f"- **Races evaluated:** {results['n_races']}",
        f"- **Monte Carlo simulations per race:** {results['n_sims_per_race']}",
        "- **Period:** 2024 Season + 2025 Season + 2026 Rounds 1-2",
        "- **Methodology:** Sequential backtest — model predictions use only data available at race time",
        "",
        "> **Note:** 2024 and 2025 data is under the previous (2022-2025) technical regulations.",
        "> 2026 Rounds 1-2 use the new 2026 regulations (active aero, new PU formula).",
        "> The backtest validates the *model methodology*, not specific config values.",
        "",
        "---",
        "",
        "## Key Metrics",
        "",
        "| Metric | Value | Interpretation |",
        "|--------|-------|----------------|",
        f"| Win Brier Score | {m['win_brier_score']:.4f} | Lower is better (0=perfect, 1=worst) |",
        f"| Podium Brier Score | {m['podium_brier_score']:.4f} | Lower is better |",
        f"| Win Log Loss | {m['win_log_loss']:.4f} | Lower is better |",
        f"| Podium Log Loss | {m['podium_log_loss']:.4f} | Lower is better |",
        f"| Winner in Top 1 | {m['winner_in_top1']:.1f}% | Model's #1 pick = actual winner |",
        f"| Winner in Top 3 | {m['winner_in_top3']:.1f}% | Actual winner in model's top 3 |",
        f"| Winner in Top 5 | {m['winner_in_top5']:.1f}% | Actual winner in model's top 5 |",
        f"| Avg Podium Overlap | {m['avg_podium_overlap']:.2f} / 3 | Model's top 3 vs actual podium |",
        f"| Avg Spearman Correlation | {m['avg_spearman_correlation']:.4f} | Predicted vs actual order (-1 to 1) |",
        "",
        "### Reference Benchmarks",
        "| Metric | Random Model | Good Model | Our Model |",
        "|--------|-------------|------------|-----------|",
        f"| Win Brier | ~0.090 | <0.060 | {m['win_brier_score']:.4f} |",
        f"| Winner Top 3 | ~15% | >50% | {m['winner_in_top3']:.1f}% |",
        f"| Spearman | ~0.00 | >0.30 | {m['avg_spearman_correlation']:.4f} |",
        "",
        "---",
        "",
        "## Win Probability Calibration",
        "",
        "| Predicted Range | Avg Predicted | Avg Actual | Count |",
        "|----------------|---------------|------------|-------|",
    ]

    for bucket in results.get("win_calibration", []):
        lines.append(
            f"| {bucket['range']} | {bucket['avg_predicted']:.4f} | {bucket['avg_actual']:.4f} | {bucket['count']} |"
        )

    lines.extend([
        "",
        "## Podium Probability Calibration",
        "",
        "| Predicted Range | Avg Predicted | Avg Actual | Count |",
        "|----------------|---------------|------------|-------|",
    ])

    for bucket in results.get("podium_calibration", []):
        lines.append(
            f"| {bucket['range']} | {bucket['avg_predicted']:.4f} | {bucket['avg_actual']:.4f} | {bucket['count']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Performance by Era",
        "",
        "| Era | Races | Avg Winner Rank | Winner Top 1% | Winner Top 3% | Avg Podium Overlap | Avg Spearman |",
        "|-----|-------|-----------------|----------------|----------------|--------------------|--------------| ",
    ])

    for era_name, em in results.get("era_breakdown", {}).items():
        lines.append(
            f"| {era_name} | {em['races']} | {em['avg_winner_rank']:.2f} | "
            f"{em['winner_top1_pct']:.1f}% | {em['winner_top3_pct']:.1f}% | "
            f"{em['avg_podium_overlap']:.2f} | {em['avg_spearman']:.4f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Race-by-Race Results",
        "",
        "| # | Year | Race | Circuit | Winner | Model Rank | Win% | Podium Overlap | Spearman |",
        "|---|------|------|---------|--------|------------|------|----------------|----------|",
    ])

    for r in results.get("race_results", []):
        lines.append(
            f"| {r['sequence']} | {r['year']} | {r['name'][:25]} | {r['circuit'][:12]} | "
            f"{r['actual_winner'][:10]} | #{r['winner_predicted_rank']} | "
            f"{r['winner_predicted_prob']:.1f}% | {r['podium_overlap']}/3 | {r['spearman_corr']:.3f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Methodology Notes",
        "",
        "### Model Pipeline (per race)",
        "1. **Elo Ratings**: Start from pre-season estimates, update after each race using pairwise head-to-head comparisons",
        "2. **Circuit Fit**: Team pace × circuit profile (power, aero, traction, tyre degradation)",
        "3. **Weather Modifiers**: Cold tyre penalty, crosswind sensitivity, rain competence, air density",
        "4. **Team Form**: Rolling 5-race window of constructor points performance",
        "5. **Season Momentum**: Driver-level exponentially weighted recent results",
        "6. **Composite Score**: Weighted combination of all factors",
        f"   - Elo: {WEIGHTS['elo']:.1%}, Circuit: {WEIGHTS['circuit_fit']:.1%}, "
        f"Form: {WEIGHTS['team_form']:.1%}, Weather: {WEIGHTS['weather']:.1%}, "
        f"Reliability: {WEIGHTS['reliability']:.1%}, Momentum: {WEIGHTS['season_momentum']:.1%}",
        "   - (grid_position weight redistributed since qualifying data not available in backtest)",
        "7. **Monte Carlo**: N simulations modeling variance, DNF, safety car, rain, T1 incidents",
        "",
        "### Fairness Constraints",
        "- Model uses only information available *at the time* of each race prediction",
        "- Elo and team pace evolve naturally through race results (no hindsight)",
        "- Pre-season baselines reset at each new season",
        "- Team pace uses EMA (α=0.15) for gradual adaptation",
        "",
        "### Regulation Note",
        "- 2024-2025: Previous technical regulations (2022-2025 era)",
        "- 2026 R1-R2: New 2026 regulations (active aero, simplified PU, new aero philosophy)",
        "- Cross-era team pace is not directly comparable — pre-season baselines account for regulation changes",
        "",
        f"*Report generated from {results['n_races']}-race backtest with {results['n_sims_per_race']} MC simulations per race.*",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_backtest()
