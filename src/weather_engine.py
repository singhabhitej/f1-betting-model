"""
Weather Impact Engine.
Applies cold-tyre, crosswind, air density, high-temp degradation, and rain modifiers.
"""
import logging

from src.config import WEATHER, TEAM_PACE, GRID

logger = logging.getLogger(__name__)


def weather_modifier(team_name):
    w = WEATHER
    team = TEAM_PACE.get(team_name, {})
    track_temp = w["track_temp_c"]
    opt_min = w["optimal_track_temp_min"]
    opt_max = w["optimal_track_temp_max"]

    # Cold tyre penalty
    if track_temp < opt_min:
        cold_gap = (opt_min - track_temp) / opt_min
        cold_factor = 1.0 - cold_gap * (1.0 - team.get("cold_tyre", 0.85))
    # B6 FIX: High-temp degradation using optimal_track_temp_max
    elif track_temp > opt_max:
        hot_gap = (track_temp - opt_max) / opt_max
        tyre_deg = team.get("tyre_deg", 70) / 100.0
        cold_factor = 1.0 - hot_gap * (1.0 - tyre_deg)
    else:
        cold_factor = 1.0

    wind = w["wind_kph"]
    wind_factor = team.get("crosswind", 0.99) ** ((wind - 10) / 10) if wind > 10 else 1.0

    air_temp = w["air_temp_c"]
    density_bonus = 1.0 + max(0, (20 - air_temp)) * 0.001

    rain_prob = w["rain_prob"]
    rain_factor = 1.0 - rain_prob * (1.0 - team.get("rain", 0.85))

    return round(cold_factor * wind_factor * density_bonus * rain_factor, 4)


def all_weather_modifiers():
    mods = {}
    for driver, team in GRID.items():
        mods[driver] = weather_modifier(team)
    return mods
