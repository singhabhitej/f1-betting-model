"""
Auto Data Ingestion from OpenF1 API + Open-Meteo Weather API.
Pulls race results, lap times, and weather forecasts automatically.
"""
import json
import logging
import os

import requests

from src.config import CALENDAR, RACE
from src.elo_system import update_elo, save_elo, load_elo

logger = logging.getLogger(__name__)

OPENF1_BASE = "https://api.openf1.org/v1"
METEO_BASE = "https://api.open-meteo.com/v1/forecast"

# B1 FIX: Map driver numbers to names for all 22 drivers on the 2026 grid
NUMBER_TO_NAME = {
    63: "Russell", 12: "Antonelli", 16: "Leclerc", 44: "Hamilton",
    1: "Norris", 81: "Piastri", 3: "Verstappen", 6: "Hadjar",
    14: "Alonso", 18: "Stroll", 10: "Gasly", 43: "Colapinto",
    87: "Bearman", 31: "Ocon", 30: "Lawson", 41: "Lindblad",
    27: "Hulkenberg", 5: "Bortoleto", 55: "Sainz", 23: "Albon",
    11: "Perez", 77: "Bottas",
}


def fetch_race_results(year, round_num):
    """Fetch race results from OpenF1 API, returning driver NAMES (not numbers)."""
    url = f"{OPENF1_BASE}/sessions?year={year}&session_type=Race"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        sessions = resp.json()
        if not isinstance(sessions, list) or not sessions:
            logger.warning("No sessions returned from OpenF1")
            return None
        session_key = sessions[min(round_num - 1, len(sessions) - 1)]["session_key"]
        pos_url = f"{OPENF1_BASE}/position?session_key={session_key}"
        pos_resp = requests.get(pos_url, timeout=30)
        pos_resp.raise_for_status()
        positions = pos_resp.json()
        if not isinstance(positions, list):
            logger.warning("Invalid positions response from OpenF1")
            return None
        final = {}
        for p in positions:
            driver_num = p.get("driver_number")
            pos = p.get("position")
            if driver_num is not None and pos is not None:
                final[driver_num] = pos
        sorted_drivers = sorted(final.items(), key=lambda x: x[1])
        # B1 FIX: Convert driver numbers to names
        result = []
        for num, _pos in sorted_drivers:
            name = NUMBER_TO_NAME.get(num)
            if name:
                result.append(name)
            else:
                logger.warning("Unknown driver number: %d", num)
        return result
    except requests.RequestException as e:
        logger.error("OpenF1 API error: %s", e)
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error("OpenF1 data parsing error: %s", e)
        return None


def fetch_weather(lat, lon):
    """Fetch 7-day weather forecast from Open-Meteo API."""
    if lat is None or lon is None:
        logger.error("fetch_weather requires lat and lon arguments")
        return None
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,relative_humidity_2m",
        "forecast_days": 7,
    }
    try:
        resp = requests.get(METEO_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data.get("hourly", {})
        temps = hourly.get("temperature_2m", [])
        rain = hourly.get("precipitation_probability", [])
        wind = hourly.get("wind_speed_10m", [])
        humidity = hourly.get("relative_humidity_2m", [])
        race_hour = 14 * 3  # approximate race start Sunday 2PM
        return {
            "air_temp_c": temps[race_hour] if len(temps) > race_hour else 20,
            "rain_prob": (rain[race_hour] / 100) if len(rain) > race_hour else 0.1,
            "wind_kph": wind[race_hour] if len(wind) > race_hour else 10,
            "humidity": (humidity[race_hour] / 100) if len(humidity) > race_hour else 0.5,
            "track_temp_c": (temps[race_hour] * 1.6) if len(temps) > race_hour else 30,
        }
    except requests.RequestException as e:
        logger.error("Weather API error: %s", e)
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error("Weather data parsing error: %s", e)
        return None


def auto_update_elo(race_result_names):
    elo = load_elo()
    if not elo:
        from src.config import DRIVER_ELO
        elo = dict(DRIVER_ELO)
    new_elo = update_elo(elo, race_result_names)
    save_elo(new_elo)
    return new_elo


def get_next_race():
    current = RACE["round"]
    for r in CALENDAR:
        if r["round"] >= current:
            return r
    return CALENDAR[-1]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    race = get_next_race()
    logger.info("Fetching weather for %s...", race["name"])
    weather = fetch_weather(race["lat"], race["lon"])
    if weather:
        os.makedirs("data", exist_ok=True)
        with open("data/weather.json", "w") as f:
            json.dump(weather, f, indent=2)
        logger.info("Weather saved: %s", weather)
    results = fetch_race_results(RACE["year"], RACE["round"] - 1)
    if results:
        logger.info("Previous race results: %s...", results[:5])
        new_elo = auto_update_elo(results)
        logger.info("Elo updated for %d drivers", len(new_elo))
