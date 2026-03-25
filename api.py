"""
F1 Betting Model — REST API
Serves predictions, driver/constructor pricing, Elo ratings, and value bets.
Built for integration with fantasy apps, dashboards, and third-party services.

Run: uvicorn api:app --host 0.0.0.0 --port 5000 --reload
Docs: http://localhost:5000/docs (Swagger UI)
"""

import math
import time
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Model imports ──
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.config import (
    RACE, CALENDAR, CIRCUIT_PROFILE, WEATHER, GRID, DRIVER_ELO,
    TEAM_PACE, TEAM_FORM, SEASON_MOMENTUM, GRID_POSITION,
    BOOKIE_ODDS_RACE_WIN, BOOKIE_ODDS_PODIUM, MC_SETTINGS,
    MODEL_WEIGHTS, grid_position_score,
)
from src.auto_predict import build_composites
from src.monte_carlo import simulate_race
from src.kelly import find_value_bets
from src.performance_metrics import (
    get_pit_crew_rankings, get_pit_crew_for_team,
    get_fastest_lap_rankings, get_circuit_records,
    pit_stop_impact, get_race_fastest_laps,
    FASTEST_LAP_PROPENSITY, CIRCUIT_LAP_RECORDS,
)

# ═══════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="F1 Predictor API",
    description=(
        "Monte Carlo simulation engine for F1 race predictions. "
        "Provides driver/constructor rankings, performance metrics, "
        "Elo ratings, value bets, and team pace data. "
        "Designed for downstream pricing engines (fantasy apps, betting platforms). "
        "Backtested across 50 races — Win Brier 0.041, Top-3 accuracy 72%."
    ),
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# CACHE — pre-compute on startup, refresh on demand
# ═══════════════════════════════════════════════════════════════

_cache = {}

def _run_model():
    """Run the full prediction pipeline and cache results."""
    composites = build_composites()
    mc_results = simulate_race(composites)
    win_bets = find_value_bets(mc_results, "win")
    podium_bets = find_value_bets(mc_results, "podium")
    _cache["composites"] = composites
    _cache["mc_results"] = mc_results
    _cache["win_bets"] = win_bets
    _cache["podium_bets"] = podium_bets
    _cache["timestamp"] = time.time()
    return composites, mc_results, win_bets, podium_bets


def _get_cached():
    """Return cached results, running the model if needed."""
    if "mc_results" not in _cache:
        _run_model()
    return _cache["composites"], _cache["mc_results"], _cache["win_bets"], _cache["podium_bets"]


# ═══════════════════════════════════════════════════════════════
# DRIVER & CONSTRUCTOR METRICS BUILDERS
# ═══════════════════════════════════════════════════════════════
# These return raw rankings and metrics — NO prices.
# Your app's pricing engine consumes these to set its own prices.


def _build_driver_metrics(driver: str, composites: dict, mc_results: dict) -> dict:
    """Build raw performance metrics for a single driver."""
    team = GRID.get(driver, "Unknown")
    composite = composites.get(driver, 50)
    mc = mc_results.get(driver, {"win_pct": 0, "podium_pct": 0, "top6_pct": 0})
    tp = TEAM_PACE.get(team, {})
    pit = get_pit_crew_for_team(team) or {}

    # Normalized composite (0-100 scale relative to grid)
    all_composites = list(composites.values())
    max_comp = max(all_composites) if all_composites else 100
    min_comp = min(all_composites) if all_composites else 0
    comp_range = max_comp - min_comp if max_comp != min_comp else 1
    composite_normalized = round((composite - min_comp) / comp_range * 100, 1)

    return {
        "driver": driver,
        "team": team,
        # Core model outputs
        "composite": round(composite, 2),
        "composite_normalized": composite_normalized,
        "win_pct": mc["win_pct"],
        "podium_pct": mc["podium_pct"],
        "top6_pct": mc["top6_pct"],
        # Driver ratings
        "elo": DRIVER_ELO.get(driver, 1500),
        "momentum": SEASON_MOMENTUM.get(driver, 30),
        "fastest_lap_propensity": FASTEST_LAP_PROPENSITY.get(driver, 20),
        # Team metrics (relevant for this driver's car)
        "team_pace": {
            "power": tp.get("power", 0),
            "aero": tp.get("aero", 0),
            "traction": tp.get("traction", 0),
            "tyre_deg": tp.get("tyre_deg", 0),
            "reliability": tp.get("reliability", 0),
        },
        "team_form": TEAM_FORM.get(team, 50),
        "pit_crew_consistency": pit.get("consistency_score", 50),
        "pit_avg_time": pit.get("avg_time", 3.0),
    }


def _build_constructor_metrics(team: str, composites: dict, mc_results: dict) -> dict:
    """Build raw performance metrics for a constructor."""
    drivers = [d for d, t in GRID.items() if t == team]
    if not drivers:
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found")

    tp = TEAM_PACE.get(team, {})
    pit = get_pit_crew_for_team(team) or {}

    # Aggregate driver probabilities
    combined_win = round(sum(mc_results.get(d, {}).get("win_pct", 0) for d in drivers), 1)
    combined_podium = round(sum(mc_results.get(d, {}).get("podium_pct", 0) for d in drivers), 1)
    combined_top6 = round(sum(mc_results.get(d, {}).get("top6_pct", 0) for d in drivers), 1)
    avg_composite = round(sum(composites.get(d, 50) for d in drivers) / len(drivers), 2)
    avg_elo = round(sum(DRIVER_ELO.get(d, 1500) for d in drivers) / len(drivers))

    # Pace aggregate
    pace_overall = round(sum(tp.get(k, 50) for k in ["power", "aero", "traction", "tyre_deg", "reliability"]) / 5, 1)

    return {
        "team": team,
        "drivers": drivers,
        # Combined probabilities
        "combined_win_pct": combined_win,
        "combined_podium_pct": combined_podium,
        "combined_top6_pct": combined_top6,
        # Team-level metrics
        "avg_composite": avg_composite,
        "avg_elo": avg_elo,
        "team_form": TEAM_FORM.get(team, 50),
        # Pace profile
        "pace": {
            "power": tp.get("power", 0),
            "aero": tp.get("aero", 0),
            "traction": tp.get("traction", 0),
            "tyre_deg": tp.get("tyre_deg", 0),
            "reliability": tp.get("reliability", 0),
            "overall": pace_overall,
        },
        # Pit crew
        "pit_crew": {
            "consistency_score": pit.get("consistency_score", 50),
            "avg_time": pit.get("avg_time", 3.0),
            "best_time": pit.get("best_time", 2.5),
            "error_rate": pit.get("error_rate", 5.0),
            "trend": pit.get("trend", "stable"),
        },
        # Weather traits
        "weather_traits": {
            "cold_tyre": tp.get("cold_tyre", 0.85),
            "crosswind": tp.get("crosswind", 0.98),
            "rain": tp.get("rain", 0.80),
        },
    }


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

# ── Health & Info ──

@app.get("/", tags=["Info"])
def root():
    """API root — returns model info and available endpoints."""
    return {
        "name": "F1 Predictor API",
        "version": "2.1.0",
        "season": RACE["year"],
        "current_race": RACE["name"],
        "round": RACE["round"],
        "circuit": RACE["circuit"],
        "model": {
            "simulations": MC_SETTINGS["n_simulations"],
            "backtest_races": 50,
            "win_brier": 0.0407,
            "winner_top3_pct": 72.0,
            "spearman": 0.8585,
        },
        "endpoints": {
            "predictions": "/api/predictions",
            "predictions_driver": "/api/predictions/{driver}",
            "value_bets": "/api/value-bets",
            "rankings_drivers": "/api/rankings/drivers",
            "rankings_driver": "/api/rankings/drivers/{driver}",
            "rankings_constructors": "/api/rankings/constructors",
            "rankings_constructor": "/api/rankings/constructors/{team}",
            "rankings_all": "/api/rankings/all",
            "team_pace": "/api/teams/pace",
            "elo_ratings": "/api/drivers/elo",
            "pitstops": "/api/pitstops",
            "pitstops_team": "/api/pitstops/{team}",
            "fastest_laps": "/api/fastest-laps",
            "fastest_laps_records": "/api/fastest-laps/records",
            "fastest_laps_records_circuit": "/api/fastest-laps/records/{circuit}",
            "fastest_laps_driver": "/api/fastest-laps/{driver}",
            "performance_summary": "/api/performance/summary",
            "circuit": "/api/circuit",
            "model_config": "/api/model/config",
            "calendar": "/api/calendar",
            "docs": "/docs",
        }
    }


@app.get("/api/health", tags=["Info"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "model_version": "2.1.0", "season": RACE["year"]}


# ── Race Predictions ──

@app.get("/api/predictions", tags=["Predictions"])
def get_predictions(
    sort_by: str = Query("composite", description="Sort by: composite, win_pct, podium_pct, top6_pct, elo"),
    limit: Optional[int] = Query(None, description="Limit results (e.g. top 10)"),
):
    """Get race win/podium/top6 probabilities for all drivers.
    
    Returns Monte Carlo simulation results from 10,000 iterations.
    """
    composites, mc_results, _, _ = _get_cached()
    
    drivers = []
    for driver, team in GRID.items():
        mc = mc_results.get(driver, {"win_pct": 0, "podium_pct": 0, "top6_pct": 0})
        drivers.append({
            "driver": driver,
            "team": team,
            "composite": round(composites.get(driver, 0), 2),
            "win_pct": mc["win_pct"],
            "podium_pct": mc["podium_pct"],
            "top6_pct": mc["top6_pct"],
            "elo": DRIVER_ELO.get(driver, 1500),
            "momentum": SEASON_MOMENTUM.get(driver, 30),
        })

    valid_sorts = {"composite", "win_pct", "podium_pct", "top6_pct", "elo"}
    key = sort_by if sort_by in valid_sorts else "composite"
    drivers.sort(key=lambda x: x[key], reverse=True)
    
    if limit:
        drivers = drivers[:limit]

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "season": RACE["year"],
        "circuit": RACE["circuit"],
        "simulations": MC_SETTINGS["n_simulations"],
        "drivers": drivers,
    }


@app.get("/api/predictions/{driver}", tags=["Predictions"])
def get_driver_prediction(driver: str):
    """Get detailed prediction for a specific driver."""
    # Case-insensitive lookup
    match = None
    for d in GRID:
        if d.lower() == driver.lower():
            match = d
            break
    if not match:
        raise HTTPException(status_code=404, detail=f"Driver '{driver}' not found. Available: {list(GRID.keys())}")

    composites, mc_results, _, _ = _get_cached()
    mc = mc_results.get(match, {"win_pct": 0, "podium_pct": 0, "top6_pct": 0, "positions": {}})
    team = GRID[match]
    tp = TEAM_PACE.get(team, {})

    return {
        "driver": match,
        "team": team,
        "composite": round(composites.get(match, 0), 2),
        "win_pct": mc["win_pct"],
        "podium_pct": mc["podium_pct"],
        "top6_pct": mc["top6_pct"],
        "elo": DRIVER_ELO.get(match, 1500),
        "momentum": SEASON_MOMENTUM.get(match, 30),
        "team_pace": {
            "power": tp.get("power", 0),
            "aero": tp.get("aero", 0),
            "traction": tp.get("traction", 0),
            "tyre_deg": tp.get("tyre_deg", 0),
            "reliability": tp.get("reliability", 0),
        },
        "position_distribution": {
            str(k): v for k, v in sorted(mc.get("positions", {}).items())
        },
        "race": RACE["name"],
        "circuit": RACE["circuit"],
    }


# ── Value Bets ──

@app.get("/api/value-bets", tags=["Betting"])
def get_value_bets(
    bet_type: str = Query("all", description="Filter: win, podium, or all"),
    verdict: Optional[str] = Query(None, description="Filter by verdict: BACK, FADE, NEUTRAL"),
):
    """Get value bet analysis comparing model probabilities to bookmaker odds.
    
    Uses Kelly Criterion for optimal bet sizing.
    """
    _, _, win_bets, podium_bets = _get_cached()
    
    result = {}
    if bet_type in ("win", "all"):
        bets = win_bets
        if verdict:
            bets = [b for b in bets if b["verdict"].upper() == verdict.upper()]
        result["win_bets"] = bets
    if bet_type in ("podium", "all"):
        bets = podium_bets
        if verdict:
            bets = [b for b in bets if b["verdict"].upper() == verdict.upper()]
        result["podium_bets"] = bets

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        **result,
    }


# ── Rankings & Metrics (for downstream pricing engines) ──

@app.get("/api/rankings/drivers", tags=["Rankings"])
def get_driver_rankings(
    sort_by: str = Query("composite", description="Sort by: composite, win_pct, podium_pct, top6_pct, elo, momentum"),
):
    """Get ranked driver metrics for all 22 drivers.
    
    Returns raw model outputs — composite score, MC probabilities, Elo,
    momentum, fastest lap propensity, team pace, pit crew data.
    No pricing — your app's pricing engine uses these metrics as inputs.
    """
    composites, mc_results, _, _ = _get_cached()
    
    drivers = []
    for driver in GRID:
        drivers.append(_build_driver_metrics(driver, composites, mc_results))

    valid_sorts = {"composite", "win_pct", "podium_pct", "top6_pct", "elo", "momentum"}
    key = sort_by if sort_by in valid_sorts else "composite"
    drivers.sort(key=lambda x: x[key], reverse=True)

    # Add rank
    for i, d in enumerate(drivers):
        d["rank"] = i + 1

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "season": RACE["year"],
        "circuit": RACE["circuit"],
        "sorted_by": key,
        "drivers": drivers,
    }


@app.get("/api/rankings/drivers/{driver}", tags=["Rankings"])
def get_driver_ranking(driver: str):
    """Get full metrics for a specific driver."""
    match = None
    for d in GRID:
        if d.lower() == driver.lower():
            match = d
            break
    if not match:
        raise HTTPException(status_code=404, detail=f"Driver '{driver}' not found. Available: {list(GRID.keys())}")

    composites, mc_results, _, _ = _get_cached()
    metrics = _build_driver_metrics(match, composites, mc_results)

    # Add position distribution from MC
    mc = mc_results.get(match, {})
    metrics["position_distribution"] = {
        str(k): v for k, v in sorted(mc.get("positions", {}).items())
    }
    metrics["race"] = RACE["name"]
    metrics["circuit"] = RACE["circuit"]
    return metrics


@app.get("/api/rankings/constructors", tags=["Rankings"])
def get_constructor_rankings(
    sort_by: str = Query("combined_win_pct", description="Sort by: combined_win_pct, combined_podium_pct, avg_composite, avg_elo, team_form"),
):
    """Get ranked constructor metrics for all 11 teams.
    
    Returns combined driver probabilities, team pace profile, pit crew stats,
    weather traits, and form. No pricing — feed into your pricing engine.
    """
    composites, mc_results, _, _ = _get_cached()
    
    teams = list(set(GRID.values()))
    constructors = []
    for team in teams:
        constructors.append(_build_constructor_metrics(team, composites, mc_results))

    valid_sorts = {"combined_win_pct", "combined_podium_pct", "avg_composite", "avg_elo", "team_form"}
    key = sort_by if sort_by in valid_sorts else "combined_win_pct"
    constructors.sort(key=lambda x: x[key], reverse=True)

    for i, c in enumerate(constructors):
        c["rank"] = i + 1

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "season": RACE["year"],
        "circuit": RACE["circuit"],
        "sorted_by": key,
        "constructors": constructors,
    }


@app.get("/api/rankings/constructors/{team}", tags=["Rankings"])
def get_constructor_ranking(team: str):
    """Get full metrics for a specific constructor."""
    match = None
    for t in set(GRID.values()):
        if t.lower().replace(" ", "") == team.lower().replace(" ", ""):
            match = t
            break
    if not match:
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found. Available: {list(set(GRID.values()))}")

    composites, mc_results, _, _ = _get_cached()
    return _build_constructor_metrics(match, composites, mc_results)


@app.get("/api/rankings/all", tags=["Rankings"])
def get_all_rankings():
    """Get complete driver and constructor metrics in one call.
    
    Designed for downstream pricing engines that need the full dataset.
    Drivers sorted by composite (descending), constructors by combined win %.
    """
    composites, mc_results, _, _ = _get_cached()

    drivers = []
    for driver in GRID:
        drivers.append(_build_driver_metrics(driver, composites, mc_results))
    drivers.sort(key=lambda x: x["composite"], reverse=True)
    for i, d in enumerate(drivers):
        d["rank"] = i + 1

    teams = list(set(GRID.values()))
    constructors = []
    for team in teams:
        constructors.append(_build_constructor_metrics(team, composites, mc_results))
    constructors.sort(key=lambda x: x["combined_win_pct"], reverse=True)
    for i, c in enumerate(constructors):
        c["rank"] = i + 1

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "season": RACE["year"],
        "circuit": RACE["circuit"],
        "simulations": MC_SETTINGS["n_simulations"],
        "drivers": drivers,
        "constructors": constructors,
    }


# ── Team & Driver Data ──

@app.get("/api/teams/pace", tags=["Teams"])
def get_team_pace():
    """Get team pace profiles — power, aero, traction, tyre degradation, reliability.
    
    Updated with latest paddock intelligence before each race.
    """
    teams = []
    for team, pace in TEAM_PACE.items():
        teams.append({
            "team": team,
            "power": pace.get("power", 0),
            "aero": pace.get("aero", 0),
            "traction": pace.get("traction", 0),
            "tyre_deg": pace.get("tyre_deg", 0),
            "reliability": pace.get("reliability", 0),
            "overall": round(sum(pace.get(k, 0) for k in ["power", "aero", "traction", "tyre_deg", "reliability"]) / 5, 1),
            "form": TEAM_FORM.get(team, 50),
            "drivers": [d for d, t in GRID.items() if t == team],
            "weather_traits": {
                "cold_tyre": pace.get("cold_tyre", 0.85),
                "crosswind": pace.get("crosswind", 0.98),
                "rain": pace.get("rain", 0.80),
            },
        })
    teams.sort(key=lambda x: x["overall"], reverse=True)
    return {"teams": teams}


@app.get("/api/drivers/elo", tags=["Drivers"])
def get_elo_ratings():
    """Get Elo ratings for all drivers, updated after each race.
    
    Elo is calculated from pairwise head-to-head comparisons.
    Higher = stronger recent race performance.
    """
    ratings = []
    for driver, elo in sorted(DRIVER_ELO.items(), key=lambda x: -x[1]):
        ratings.append({
            "driver": driver,
            "team": GRID.get(driver, "Unknown"),
            "elo": elo,
            "momentum": SEASON_MOMENTUM.get(driver, 30),
        })
    return {"ratings": ratings}


# ── Circuit & Weather ──

@app.get("/api/circuit", tags=["Circuit"])
def get_circuit():
    """Get current circuit profile and weather conditions."""
    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "circuit": RACE["circuit"],
        "profile": CIRCUIT_PROFILE,
        "weather": WEATHER,
        "characteristics": {
            "dominant_factor": max(CIRCUIT_PROFILE, key=CIRCUIT_PROFILE.get),
            "aero_demand": "High" if CIRCUIT_PROFILE["aero"] >= 85 else "Medium" if CIRCUIT_PROFILE["aero"] >= 70 else "Low",
            "power_demand": "High" if CIRCUIT_PROFILE["power"] >= 85 else "Medium" if CIRCUIT_PROFILE["power"] >= 70 else "Low",
            "rain_risk": "High" if WEATHER["rain_prob"] >= 0.3 else "Medium" if WEATHER["rain_prob"] >= 0.15 else "Low",
        },
    }


# ── Model Config ──

@app.get("/api/model/config", tags=["Model"])
def get_model_config():
    """Get current model configuration — weights, MC settings, backtest performance."""
    return {
        "weights": MODEL_WEIGHTS,
        "monte_carlo": MC_SETTINGS,
        "backtest": {
            "races": 50,
            "win_brier": 0.0407,
            "podium_brier": 0.0846,
            "winner_top1_pct": 32.0,
            "winner_top3_pct": 72.0,
            "winner_top5_pct": 86.0,
            "avg_spearman": 0.8585,
            "avg_podium_overlap": 1.72,
        },
        "season": RACE["year"],
        "current_round": RACE["round"],
    }


@app.get("/api/model/refresh", tags=["Model"])
def refresh_model():
    """Force re-run the Monte Carlo simulation and refresh all cached predictions."""
    composites, mc_results, win_bets, podium_bets = _run_model()
    return {
        "status": "refreshed",
        "timestamp": _cache.get("timestamp"),
        "simulations": MC_SETTINGS["n_simulations"],
        "top_3": [
            {"driver": d, "win_pct": mc_results[d]["win_pct"]}
            for d in sorted(mc_results, key=lambda x: mc_results[x]["win_pct"], reverse=True)[:3]
        ],
    }


# ── Pit Crew Performance ──

@app.get("/api/pitstops", tags=["Performance"])
def get_pitstops():
    """Get all teams pit crew rankings sorted by consistency score.

    Includes average pit stop time, best time, consistency score,
    expected pit time (xPT), error rate, and DHL points.
    """
    rankings = get_pit_crew_rankings()
    for entry in rankings:
        entry["pit_stop_impact"] = pit_stop_impact(entry["team"])
    return {
        "race": RACE["name"],
        "season": RACE["year"],
        "teams": rankings,
    }


@app.get("/api/pitstops/{team}", tags=["Performance"])
def get_pitstop_team(team: str):
    """Get detailed pit crew data for a specific team."""
    data = get_pit_crew_for_team(team)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found")
    data["pit_stop_impact"] = pit_stop_impact(team)
    return data


# ── Fastest Laps ──

@app.get("/api/fastest-laps", tags=["Performance"])
def get_fastest_laps():
    """Get fastest lap propensity rankings for all drivers.

    Propensity score (0-100) reflects car pace, tyre management,
    and late-race fresh tyre strategy likelihood.
    """
    rankings = get_fastest_lap_rankings()
    return {
        "race": RACE["name"],
        "season": RACE["year"],
        "drivers": rankings,
    }


@app.get("/api/fastest-laps/records", tags=["Performance"])
def get_fastest_lap_records():
    """Get circuit lap records (race + qualifying) for all circuits."""
    records = {}
    for circuit, data in CIRCUIT_LAP_RECORDS.items():
        records[circuit] = data
    return {
        "season": RACE["year"],
        "circuits": records,
    }


@app.get("/api/fastest-laps/records/{circuit}", tags=["Performance"])
def get_fastest_lap_record_circuit(circuit: str):
    """Get lap records for a specific circuit."""
    data = get_circuit_records(circuit)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit '{circuit}' not found. Available: {list(CIRCUIT_LAP_RECORDS.keys())}",
        )
    return data


@app.get("/api/fastest-laps/{driver}", tags=["Performance"])
def get_fastest_lap_driver(driver: str):
    """Get fastest lap propensity stats for a specific driver."""
    # Case-insensitive lookup
    match = None
    for d in FASTEST_LAP_PROPENSITY:
        if d.lower() == driver.lower():
            match = d
            break
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Driver '{driver}' not found. Available: {list(FASTEST_LAP_PROPENSITY.keys())}",
        )
    return {
        "driver": match,
        "propensity": FASTEST_LAP_PROPENSITY[match],
        "team": GRID.get(match, "Unknown"),
    }


# ── Performance Summary ──

@app.get("/api/performance/summary", tags=["Performance"])
def get_performance_summary():
    """Combined pit crew + fastest lap overview for the current race.

    Useful for a dashboard that wants both datasets in one call.
    """
    pit_rankings = get_pit_crew_rankings()
    for entry in pit_rankings:
        entry["pit_stop_impact"] = pit_stop_impact(entry["team"])

    fl_rankings = get_fastest_lap_rankings()

    # Current circuit records
    current_circuit = "Suzuka"  # derived from RACE config
    circuit_records = get_circuit_records(current_circuit)

    # 2026 race fastest laps so far
    race_fl = get_race_fastest_laps(2026)

    return {
        "race": RACE["name"],
        "round": RACE["round"],
        "season": RACE["year"],
        "pit_crew_rankings": pit_rankings,
        "fastest_lap_rankings": fl_rankings,
        "circuit_records": circuit_records,
        "race_fastest_laps_2026": race_fl,
    }


# ── Calendar ──

@app.get("/api/calendar", tags=["Info"])
def get_calendar():
    """Get the 2026 F1 race calendar (22 races, Bahrain+Saudi cancelled)."""
    return {
        "season": RACE["year"],
        "total_races": len(CALENDAR),
        "current_round": RACE["round"],
        "races": CALENDAR,
    }


# ═══════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Pre-compute predictions on startup."""
    _run_model()
