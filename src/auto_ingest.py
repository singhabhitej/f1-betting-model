"""
Auto Data Ingestion from OpenF1 API + Open-Meteo Weather API.
Pulls race results, lap times, and weather forecasts automatically.
"""
import json
import os
import requests
from src.config import CALENDAR, RACE
from src.elo_system import update_elo, save_elo, load_elo

OPENF1_BASE = "https://api.openf1.org/v1"
METEO_BASE = "https://api.open-meteo.com/v1/forecast"

def fetch_race_results(year, round_num):
    url = f"{OPENF1_BASE}/sessions?year={year}&session_type=Race"
    try:
        resp = requests.get(url, timeout=30)
        sessions = resp.json()
        if not sessions:
            return None
        session_key = sessions[min(round_num - 1, len(sessions) - 1)]["session_key"]
        pos_url = f"{OPENF1_BASE}/position?session_key={session_key}"
        positions = requests.get(pos_url, timeout=30).json()
        final = {}
        for p in positions:
            driver = p.get("driver_number")
            pos = p.get("position")
            if driver and pos:
                final[driver] = pos
        sorted_drivers = sorted(final.items(), key=lambda x: x[1])
        return [str(d[0]) for d in sorted_drivers]
    except Exception as e:
        print(f"OpenF1 error: {e}")
        return None

def fetch_weather(lat, lon):
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,relative_humidity_2m",
        "forecast_days": 7,
    }
    try:
        resp = requests.get(METEO_BASE, params=params, timeout=30)
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
    except Exception as e:
        print(f"Weather API error: {e}")
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
    race = get_next_race()
    print(f"Fetching weather for {race['name']}...")
    weather = fetch_weather(race["lat"], race["lon"])
    if weather:
        os.makedirs("data", exist_ok=True)
        with open("data/weather.json", "w") as f:
            json.dump(weather, f, indent=2)
        print(f"Weather saved: {weather}")
    results = fetch_race_results(RACE["year"], RACE["round"] - 1)
    if results:
        print(f"Previous race results: {results[:5]}...")
        new_elo = auto_update_elo(results)
        print(f"Elo updated for {len(new_elo)} drivers")
