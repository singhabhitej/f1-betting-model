"""
F1 2026 Betting Model - Master Configuration
Update this file before each race weekend.
"""

RACE = {
    "year": 2026,
    "round": 3,
    "name": "Japanese Grand Prix",
    "circuit": "Suzuka International Racing Course",
    "laps": 53,
    "is_sprint": False,
    "sprint_laps": 0,
}

# Bahrain GP & Saudi Arabian GP CANCELLED (Middle East conflict) — 22 races remain
CALENDAR = [
    {"round": 1, "name": "Australian GP", "city": "Melbourne", "lat": -37.85, "lon": 144.97, "is_sprint": False},
    {"round": 2, "name": "Chinese GP", "city": "Shanghai", "lat": 31.34, "lon": 121.22, "is_sprint": True},
    {"round": 3, "name": "Japanese GP", "city": "Suzuka", "lat": 34.84, "lon": 136.54, "is_sprint": False},
    {"round": 4, "name": "Miami GP", "city": "Miami", "lat": 25.96, "lon": -80.24, "is_sprint": True},
    {"round": 5, "name": "Emilia Romagna GP", "city": "Imola", "lat": 44.34, "lon": 11.72, "is_sprint": False},
    {"round": 6, "name": "Monaco GP", "city": "Monaco", "lat": 43.73, "lon": 7.42, "is_sprint": False},
    {"round": 7, "name": "Spanish GP", "city": "Barcelona", "lat": 41.57, "lon": 2.26, "is_sprint": False},
    {"round": 8, "name": "Canadian GP", "city": "Montreal", "lat": 45.50, "lon": -73.52, "is_sprint": False},
    {"round": 9, "name": "Austrian GP", "city": "Spielberg", "lat": 47.22, "lon": 14.76, "is_sprint": True},
    {"round": 10, "name": "British GP", "city": "Silverstone", "lat": 52.07, "lon": -1.02, "is_sprint": False},
    {"round": 11, "name": "Belgian GP", "city": "Spa", "lat": 50.44, "lon": 5.97, "is_sprint": True},
    {"round": 12, "name": "Hungarian GP", "city": "Budapest", "lat": 47.58, "lon": 19.25, "is_sprint": False},
    {"round": 13, "name": "Dutch GP", "city": "Zandvoort", "lat": 52.39, "lon": 4.54, "is_sprint": False},
    {"round": 14, "name": "Italian GP", "city": "Monza", "lat": 45.62, "lon": 9.28, "is_sprint": False},
    {"round": 15, "name": "Azerbaijan GP", "city": "Baku", "lat": 40.37, "lon": 49.85, "is_sprint": False},
    {"round": 16, "name": "Singapore GP", "city": "Singapore", "lat": 1.29, "lon": 103.86, "is_sprint": True},
    {"round": 17, "name": "United States GP", "city": "Austin", "lat": 30.13, "lon": -97.64, "is_sprint": True},
    {"round": 18, "name": "Mexico City GP", "city": "Mexico City", "lat": 19.40, "lon": -99.09, "is_sprint": False},
    {"round": 19, "name": "Brazilian GP", "city": "Sao Paulo", "lat": -23.70, "lon": -46.70, "is_sprint": False},
    {"round": 20, "name": "Las Vegas GP", "city": "Las Vegas", "lat": 36.11, "lon": -115.17, "is_sprint": False},
    {"round": 21, "name": "Qatar GP", "city": "Lusail", "lat": 25.49, "lon": 51.45, "is_sprint": False},
    {"round": 22, "name": "Abu Dhabi GP", "city": "Abu Dhabi", "lat": 24.47, "lon": 54.60, "is_sprint": False},
]

# Suzuka: aero/high-speed corner dominated circuit
CIRCUIT_PROFILE = {
    "power": 75,
    "aero": 92,
    "traction": 85,
    "tyre_deg": 70,
}

# Suzuka late March weather
WEATHER = {
    "air_temp_c": 15,
    "track_temp_c": 22,
    "rain_prob": 0.20,
    "wind_kph": 15,
    "humidity": 0.55,
    "optimal_track_temp_min": 28,
    "optimal_track_temp_max": 45,
}

# ── 2026 Grid: 22 drivers, 11 teams ──
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
    "Colapinto": "Alpine",
    "Bearman": "Haas",
    "Ocon": "Haas",
    "Lawson": "Racing Bulls",
    "Lindblad": "Racing Bulls",
    "Hulkenberg": "Audi",
    "Bortoleto": "Audi",
    "Sainz": "Williams",
    "Albon": "Williams",
    "Perez": "Cadillac",
    "Bottas": "Cadillac",
}

# ── Elo ratings updated for 2026 form (post Round 2) ──
DRIVER_ELO = {
    "Russell": 2170, "Antonelli": 2130, "Leclerc": 2040, "Hamilton": 2020,
    "Norris": 1980, "Verstappen": 1950, "Piastri": 1920, "Bearman": 1870,
    "Gasly": 1820, "Lawson": 1800, "Lindblad": 1790, "Hadjar": 1780,
    "Sainz": 1760, "Hulkenberg": 1750, "Albon": 1740, "Ocon": 1730,
    "Bortoleto": 1720, "Colapinto": 1710, "Alonso": 1700, "Bottas": 1680,
    "Perez": 1670, "Stroll": 1650,
}

# ── Team pace profiles for 2026 regs (active aero + energy management era) ──
# Updated pre-Japanese GP with latest team intel (upgrades, reliability, aero developments)
TEAM_PACE = {
    # Mercedes: "party mode" energy advantage confirmed staying for Suzuka, FIA review won't apply until June 1
    "Mercedes": {"power": 95, "aero": 96, "traction": 93, "tyre_deg": 92, "reliability": 97, "cold_tyre": 0.92, "crosswind": 0.998, "rain": 0.94},
    # Ferrari: "Macarena wing" experimental only (FP1), but excellent chassis/aero — strong at Suzuka corners
    "Ferrari": {"power": 90, "aero": 93, "traction": 89, "tyre_deg": 85, "reliability": 88, "cold_tyre": 0.88, "crosswind": 0.994, "rain": 0.90},
    # McLaren: DNS crisis (both cars in China), Mercedes PU electrical fault under investigation, fix uncertain
    "McLaren": {"power": 88, "aero": 88, "traction": 84, "tyre_deg": 82, "reliability": 55, "cold_tyre": 0.85, "crosswind": 0.990, "rain": 0.86},
    # Red Bull: confirmed Suzuka updates for handling/graining, but high-speed corners still expose weakness
    "Red Bull": {"power": 82, "aero": 82, "traction": 80, "tyre_deg": 76, "reliability": 72, "cold_tyre": 0.83, "crosswind": 0.986, "rain": 0.82},
    # Haas: surprise package, cornering-focused chassis excels at Suzuka's demands
    "Haas": {"power": 80, "aero": 80, "traction": 78, "tyre_deg": 74, "reliability": 82, "cold_tyre": 0.82, "crosswind": 0.984, "rain": 0.78},
    # Racing Bulls: solid, no major changes — Lindblad/Lawson both performing
    "Racing Bulls": {"power": 78, "aero": 76, "traction": 74, "tyre_deg": 72, "reliability": 78, "cold_tyre": 0.81, "crosswind": 0.982, "rain": 0.77},
    # Alpine: resurgence with Mercedes PU, Gasly P6 in China, only 0.3s off McLaren in sessions
    "Alpine": {"power": 78, "aero": 77, "traction": 74, "tyre_deg": 70, "reliability": 76, "cold_tyre": 0.80, "crosswind": 0.980, "rain": 0.76},
    # Audi: no major updates, still finding feet
    "Audi": {"power": 74, "aero": 72, "traction": 70, "tyre_deg": 68, "reliability": 72, "cold_tyre": 0.79, "crosswind": 0.978, "rain": 0.74},
    # Williams: Mercedes PU but chassis deficit
    "Williams": {"power": 72, "aero": 70, "traction": 68, "tyre_deg": 66, "reliability": 68, "cold_tyre": 0.78, "crosswind": 0.976, "rain": 0.72},
    # Aston Martin: Honda engine upgrade at Suzuka (reliability + vibration fix), small chassis change too
    "Aston Martin": {"power": 70, "aero": 66, "traction": 64, "tyre_deg": 62, "reliability": 62, "cold_tyre": 0.76, "crosswind": 0.972, "rain": 0.70},
    # Cadillac: rookie team, still at the back
    "Cadillac": {"power": 65, "aero": 62, "traction": 60, "tyre_deg": 60, "reliability": 58, "cold_tyre": 0.74, "crosswind": 0.970, "rain": 0.68},
}

# ── B2 FIX: Real team form metric based on actual 2026 constructor results ──
TEAM_FORM = {
    "Mercedes": 98,
    "Ferrari": 80,
    "Haas": 65,
    "McLaren": 55,
    "Red Bull": 50,
    "Racing Bulls": 55,
    "Alpine": 48,
    "Audi": 38,
    "Williams": 35,
    "Cadillac": 25,
    "Aston Martin": 20,
}

# ── Season momentum based on 2026 Rounds 1-2 results ──
SEASON_MOMENTUM = {
    "Russell": 95,
    "Antonelli": 92,
    "Hamilton": 75,
    "Leclerc": 73,
    "Bearman": 70,
    "Norris": 45,
    "Gasly": 42,
    "Lawson": 40,
    "Verstappen": 30,
    "Lindblad": 38,
    "Hadjar": 28,
    "Piastri": 20,
    "Sainz": 25,
    "Bortoleto": 25,
    "Colapinto": 22,
    "Hulkenberg": 18,
    "Ocon": 15,
    "Albon": 12,
    "Bottas": 10,
    "Perez": 8,
    "Alonso": 8,
    "Stroll": 5,
}

# ── Grid position from qualifying (empty = qualifying hasn't happened yet) ──
GRID_POSITION = {}

# ── Japanese GP betting odds (Oddschecker/Polymarket) ──
BOOKIE_ODDS_RACE_WIN = {
    "Russell": 1.70, "Antonelli": 4.75, "Hamilton": 11.00, "Leclerc": 12.00,
    "Verstappen": 31.00, "Norris": 51.00, "Piastri": 51.00, "Bearman": 67.00,
    "Hadjar": 101.00, "Gasly": 101.00, "Lawson": 151.00,
}

BOOKIE_ODDS_PODIUM = {
    "Russell": 1.20, "Antonelli": 1.80, "Hamilton": 3.00, "Leclerc": 3.50,
    "Verstappen": 8.00, "Norris": 12.00, "Piastri": 15.00, "Bearman": 20.00,
    "Gasly": 30.00, "Hadjar": 35.00,
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

# ── Model weights (updated with grid_position + season_momentum) ──
MODEL_WEIGHTS = {
    "elo": 0.20,
    "circuit_fit": 0.20,
    "team_form": 0.15,
    "grid_position": 0.15,
    "weather": 0.10,
    "reliability": 0.10,
    "season_momentum": 0.10,
}


def grid_position_score(position):
    """Convert grid position (1-22) to a 0-100 score.
    P1=100, P2=96, P3=92, diminishing from there."""
    if position <= 0:
        return 0
    if position == 1:
        return 100
    if position == 2:
        return 96
    if position == 3:
        return 92
    # Diminishing returns: P4=88, P5=84, ..., then slower falloff past P10
    if position <= 10:
        return max(0, 92 - (position - 3) * 4)
    # P11+ drops more slowly
    return max(0, 64 - (position - 10) * 3)
