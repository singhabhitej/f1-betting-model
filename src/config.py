"""
F1 2026 Betting Model - Master Configuration
Update this file before each race weekend.
"""

RACE = {
    "year": 2026,
    "round": 2,
    "name": "Chinese Grand Prix",
    "circuit": "Shanghai International Circuit",
    "laps": 56,
    "is_sprint": True,
    "sprint_laps": 19,
}

CALENDAR = [
    {"round": 1, "name": "Australian GP", "city": "Melbourne", "lat": -37.85, "lon": 144.97, "is_sprint": False},
    {"round": 2, "name": "Chinese GP", "city": "Shanghai", "lat": 31.34, "lon": 121.22, "is_sprint": True},
    {"round": 3, "name": "Japanese GP", "city": "Suzuka", "lat": 34.84, "lon": 136.54, "is_sprint": False},
    {"round": 4, "name": "Bahrain GP", "city": "Sakhir", "lat": 26.03, "lon": 50.51, "is_sprint": False},
    {"round": 5, "name": "Saudi Arabian GP", "city": "Jeddah", "lat": 21.63, "lon": 39.10, "is_sprint": False},
    {"round": 6, "name": "Miami GP", "city": "Miami", "lat": 25.96, "lon": -80.24, "is_sprint": True},
    {"round": 7, "name": "Emilia Romagna GP", "city": "Imola", "lat": 44.34, "lon": 11.72, "is_sprint": False},
    {"round": 8, "name": "Monaco GP", "city": "Monaco", "lat": 43.73, "lon": 7.42, "is_sprint": False},
    {"round": 9, "name": "Spanish GP", "city": "Barcelona", "lat": 41.57, "lon": 2.26, "is_sprint": False},
    {"round": 10, "name": "Canadian GP", "city": "Montreal", "lat": 45.50, "lon": -73.52, "is_sprint": False},
    {"round": 11, "name": "Austrian GP", "city": "Spielberg", "lat": 47.22, "lon": 14.76, "is_sprint": True},
    {"round": 12, "name": "British GP", "city": "Silverstone", "lat": 52.07, "lon": -1.02, "is_sprint": False},
    {"round": 13, "name": "Belgian GP", "city": "Spa", "lat": 50.44, "lon": 5.97, "is_sprint": True},
    {"round": 14, "name": "Hungarian GP", "city": "Budapest", "lat": 47.58, "lon": 19.25, "is_sprint": False},
    {"round": 15, "name": "Dutch GP", "city": "Zandvoort", "lat": 52.39, "lon": 4.54, "is_sprint": False},
    {"round": 16, "name": "Italian GP", "city": "Monza", "lat": 45.62, "lon": 9.28, "is_sprint": False},
    {"round": 17, "name": "Azerbaijan GP", "city": "Baku", "lat": 40.37, "lon": 49.85, "is_sprint": False},
    {"round": 18, "name": "Singapore GP", "city": "Singapore", "lat": 1.29, "lon": 103.86, "is_sprint": True},
    {"round": 19, "name": "United States GP", "city": "Austin", "lat": 30.13, "lon": -97.64, "is_sprint": True},
    {"round": 20, "name": "Mexico City GP", "city": "Mexico City", "lat": 19.40, "lon": -99.09, "is_sprint": False},
    {"round": 21, "name": "Brazilian GP", "city": "Sao Paulo", "lat": -23.70, "lon": -46.70, "is_sprint": False},
    {"round": 22, "name": "Las Vegas GP", "city": "Las Vegas", "lat": 36.11, "lon": -115.17, "is_sprint": False},
    {"round": 23, "name": "Qatar GP", "city": "Lusail", "lat": 25.49, "lon": 51.45, "is_sprint": False},
    {"round": 24, "name": "Abu Dhabi GP", "city": "Abu Dhabi", "lat": 24.47, "lon": 54.60, "is_sprint": False},
]

CIRCUIT_PROFILE = {
    "power": 85,
    "aero": 70,
    "traction": 80,
    "tyre_deg": 75,
}

WEATHER = {
    "air_temp_c": 12,
    "track_temp_c": 18,
    "rain_prob": 0.10,
    "wind_kph": 18,
    "humidity": 0.65,
    "optimal_track_temp_min": 28,
    "optimal_track_temp_max": 45,
}

GRID = {
    "Russell": "Mercedes",
    "Antonelli": "Mercedes",
    "Leclerc": "Ferrari",
    "Hamilton": "Ferrari",
    "Verstappen": "Red Bull",
    "Hadjar": "Red Bull",
    "Norris": "McLaren",
    "Piastri": "McLaren",
    "Alonso": "Aston Martin",
    "Stroll": "Aston Martin",
    "Gasly": "Alpine",
    "Doohan": "Alpine",
    "Bearman": "Haas",
    "Bortoleto": "Sauber",
    "Hulkenberg": "Sauber",
    "Lawson": "Racing Bulls",
    "Tsunoda": "Racing Bulls",
    "Sainz": "Williams",
    "Albon": "Williams",
    "Colapinto": "Cadillac",
    "Pourchaire": "Cadillac",
    "Lindblad": "Racing Bulls",
}

DRIVER_ELO = {
    "Verstappen": 2169, "Norris": 2053, "Leclerc": 2031,
    "Russell": 2000, "Hamilton": 1998, "Piastri": 1957,
    "Alonso": 1899, "Sainz": 1880, "Antonelli": 1847,
    "Gasly": 1810, "Tsunoda": 1790, "Albon": 1775,
    "Hulkenberg": 1743, "Bearman": 1720, "Stroll": 1710,
    "Lawson": 1700, "Bortoleto": 1690, "Doohan": 1680,
    "Hadjar": 1670, "Lindblad": 1660, "Colapinto": 1650,
    "Pourchaire": 1640,
}

TEAM_PACE = {
    "Mercedes":      {"power": 95, "aero": 93, "traction": 90, "tyre_deg": 88, "reliability": 95, "cold_tyre": 0.90, "crosswind": 0.998, "rain": 0.92},
    "Ferrari":       {"power": 88, "aero": 90, "traction": 85, "tyre_deg": 82, "reliability": 90, "cold_tyre": 0.82, "crosswind": 0.990, "rain": 0.88},
    "McLaren":       {"power": 82, "aero": 85, "traction": 80, "tyre_deg": 80, "reliability": 85, "cold_tyre": 0.87, "crosswind": 0.992, "rain": 0.85},
    "Red Bull":      {"power": 90, "aero": 82, "traction": 75, "tyre_deg": 78, "reliability": 80, "cold_tyre": 0.95, "crosswind": 0.988, "rain": 0.90},
    "Aston Martin":  {"power": 78, "aero": 75, "traction": 70, "tyre_deg": 72, "reliability": 60, "cold_tyre": 0.80, "crosswind": 0.982, "rain": 0.78},
    "Alpine":        {"power": 80, "aero": 72, "traction": 72, "tyre_deg": 74, "reliability": 75, "cold_tyre": 0.84, "crosswind": 0.988, "rain": 0.80},
    "Haas":          {"power": 78, "aero": 70, "traction": 70, "tyre_deg": 70, "reliability": 78, "cold_tyre": 0.83, "crosswind": 0.985, "rain": 0.76},
    "Sauber":        {"power": 76, "aero": 68, "traction": 68, "tyre_deg": 68, "reliability": 72, "cold_tyre": 0.81, "crosswind": 0.984, "rain": 0.74},
    "Racing Bulls":  {"power": 82, "aero": 70, "traction": 72, "tyre_deg": 72, "reliability": 76, "cold_tyre": 0.85, "crosswind": 0.986, "rain": 0.79},
    "Williams":      {"power": 80, "aero": 65, "traction": 65, "tyre_deg": 66, "reliability": 70, "cold_tyre": 0.82, "crosswind": 0.983, "rain": 0.75},
    "Cadillac":      {"power": 70, "aero": 60, "traction": 60, "tyre_deg": 62, "reliability": 65, "cold_tyre": 0.78, "crosswind": 0.980, "rain": 0.70},
}

BOOKIE_ODDS_RACE_WIN = {
    "Russell": 2.50, "Verstappen": 5.00, "Leclerc": 6.00,
    "Antonelli": 8.50, "Norris": 7.00, "Hamilton": 12.00,
    "Piastri": 15.00, "Alonso": 80.00, "Sainz": 50.00, "Gasly": 100.00,
}

BOOKIE_ODDS_PODIUM = {
    "Russell": 1.35, "Verstappen": 2.20, "Leclerc": 2.00,
    "Antonelli": 2.50, "Norris": 3.00, "Hamilton": 3.50, "Piastri": 5.00,
}

MC_SETTINGS = {
    "n_simulations": 10000,
    "dnf_base_rate": 0.05,
    "safety_car_prob": 0.55,
    "sc_compression_factor": 0.4,
    "t1_incident_prob": 0.15,
    "rain_amplifier": 1.8,
    "variance_sigma": 0.08,
}

MODEL_WEIGHTS = {
    "elo": 0.30,
    "circuit_fit": 0.25,
    "team_form": 0.25,
    "weather": 0.10,
    "reliability": 0.10,
}
