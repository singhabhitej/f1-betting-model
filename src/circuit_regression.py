"""
Circuit Regression Model.
Maps track DNA (power, aero, traction, tyre_deg) to team strengths.
"""
from src.config import CIRCUIT_PROFILE, TEAM_PACE, GRID

def circuit_fit_score(team_name):
    team = TEAM_PACE.get(team_name, {})
    cp = CIRCUIT_PROFILE
    total_weight = cp["power"] + cp["aero"] + cp["traction"] + cp["tyre_deg"]
    if total_weight == 0:
        return 50.0
    score = (
        cp["power"] * team.get("power", 50) +
        cp["aero"] * team.get("aero", 50) +
        cp["traction"] * team.get("traction", 50) +
        cp["tyre_deg"] * team.get("tyre_deg", 50)
    ) / total_weight
    return round(score, 2)

def all_circuit_fits():
    fits = {}
    for driver, team in GRID.items():
        fits[driver] = circuit_fit_score(team)
    return fits
