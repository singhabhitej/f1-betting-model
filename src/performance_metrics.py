"""
F1 2026 Betting Model — Pit Crew & Fastest Lap Performance Metrics

Contains pit crew data (DHL rankings, median times, consistency scores, xPT),
fastest lap propensity ratings, and circuit lap records.
Sources: DHL Fastest Pit Stop Award, F1.com timing data, 2025–2026 race results.
"""

# ═══════════════════════════════════════════════════════════════
# PIT CREW DATA
# ═══════════════════════════════════════════════════════════════

PIT_CREW_STATS = {
    "Ferrari": {
        "avg_time": 2.31,
        "best_time": 2.00,
        "consistency_score": 97,
        "xpt": 2.50,
        "error_rate": 1.3,       # ~3 stops over 3.0s / ~230 total stops ≈ 1.3%
        "dhl_points_2025": 559,
        "dhl_points_2024": 364,
        "trend": "improving",
    },
    "Red Bull": {
        "avg_time": 2.42,
        "best_time": 1.95,
        "consistency_score": 88,
        "xpt": 2.65,
        "error_rate": 4.5,
        "dhl_points_2025": 362,
        "dhl_points_2024": 552,
        "trend": "declining",
    },
    "Racing Bulls": {
        "avg_time": 2.50,
        "best_time": 2.18,
        "consistency_score": 82,
        "xpt": 2.68,
        "error_rate": 5.0,
        "dhl_points_2025": 353,
        "dhl_points_2024": 253,
        "trend": "improving",
    },
    "Mercedes": {
        "avg_time": 2.53,
        "best_time": 2.12,
        "consistency_score": 80,
        "xpt": 2.72,
        "error_rate": 5.5,
        "dhl_points_2025": 253,
        "dhl_points_2024": 284,
        "trend": "stable",
    },
    "Sauber": {
        "avg_time": 2.63,
        "best_time": 2.13,
        "consistency_score": 72,
        "xpt": 2.81,
        "error_rate": 7.0,
        "dhl_points_2025": 195,
        "dhl_points_2024": 144,
        "trend": "improving",
    },
    "McLaren": {
        "avg_time": 2.75,
        "best_time": 1.91,
        "consistency_score": 65,
        "xpt": 2.85,
        "error_rate": 16.0,      # 16 stops over 3.0s — highest in field
        "dhl_points_2025": 410,
        "dhl_points_2024": 433,
        "trend": "stable",
    },
    "Alpine": {
        "avg_time": 2.85,
        "best_time": 2.30,
        "consistency_score": 60,
        "xpt": 2.88,
        "error_rate": 9.0,
        "dhl_points_2025": 99,
        "dhl_points_2024": 177,
        "trend": "declining",
    },
    "Williams": {
        "avg_time": 2.80,
        "best_time": 2.35,
        "consistency_score": 55,
        "xpt": 3.00,
        "error_rate": 11.0,
        "dhl_points_2025": 84,
        "dhl_points_2024": 38,
        "trend": "improving",
    },
    "Aston Martin": {
        "avg_time": 2.78,
        "best_time": 2.40,
        "consistency_score": 52,
        "xpt": 2.97,
        "error_rate": 12.0,
        "dhl_points_2025": 56,
        "dhl_points_2024": 117,
        "trend": "declining",
    },
    "Haas": {
        "avg_time": 2.92,
        "best_time": 2.50,
        "consistency_score": 50,
        "xpt": 3.05,
        "error_rate": 14.0,
        "dhl_points_2025": 53,
        "dhl_points_2024": 49,
        "trend": "stable",
    },
    "Cadillac": {
        "avg_time": 3.10,
        "best_time": 2.80,
        "consistency_score": 45,
        "xpt": 3.15,
        "error_rate": 18.0,
        "dhl_points_2025": 0,
        "dhl_points_2024": 0,
        "trend": "stable",
    },
}


# ═══════════════════════════════════════════════════════════════
# FASTEST LAP PROPENSITY
# ═══════════════════════════════════════════════════════════════

FASTEST_LAP_PROPENSITY = {
    "Russell": 90,
    "Antonelli": 88,
    "Leclerc": 75,
    "Hamilton": 72,
    "Norris": 65,
    "Verstappen": 55,
    "Bearman": 50,
    "Piastri": 40,
    "Gasly": 38,
    "Lawson": 35,
    "Lindblad": 33,
    "Hadjar": 32,
    "Ocon": 30,
    "Sainz": 28,
    "Hulkenberg": 27,
    "Colapinto": 25,
    "Bortoleto": 24,
    "Albon": 23,
    "Alonso": 22,
    "Bottas": 21,
    "Perez": 20,
    "Stroll": 20,
}


# ═══════════════════════════════════════════════════════════════
# CIRCUIT LAP RECORDS
# ═══════════════════════════════════════════════════════════════

CIRCUIT_LAP_RECORDS = {
    "Suzuka": {
        "race_record": {
            "time": "1:30.965",
            "driver": "Antonelli",
            "year": 2025,
            "team": "Mercedes",
        },
        "qualifying_record": {
            "time": "1:26.983",
            "driver": "Verstappen",
            "year": 2025,
            "team": "Red Bull",
        },
    },
    "Melbourne": {
        "race_record": {
            "time": "1:22.091",
            "driver": "Verstappen",
            "year": 2026,
            "team": "Red Bull",
        },
        "qualifying_record": {
            "time": "1:15.096",
            "driver": "Norris",
            "year": 2025,
            "team": "McLaren",
        },
    },
    "Shanghai": {
        "race_record": {
            "time": "1:35.275",
            "driver": "Antonelli",
            "year": 2026,
            "team": "Mercedes",
        },
        "qualifying_record": {
            "time": "1:33.660",
            "driver": "Russell",
            "year": 2025,
            "team": "Mercedes",
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# RACE FASTEST LAPS 2026
# ═══════════════════════════════════════════════════════════════

RACE_FASTEST_LAPS_2026 = [
    {
        "round": 1,
        "race": "Australian GP",
        "circuit": "Melbourne",
        "driver": "Verstappen",
        "team": "Red Bull",
        "time": "1:22.091",
    },
    {
        "round": 2,
        "race": "Chinese GP",
        "circuit": "Shanghai",
        "driver": "Antonelli",
        "team": "Mercedes",
        "time": "1:35.275",
        "top_10": [
            {"pos": 1, "driver": "Antonelli", "team": "Mercedes", "time": "1:35.275"},
            {"pos": 2, "driver": "Russell", "team": "Mercedes", "time": "1:35.400"},
            {"pos": 3, "driver": "Ocon", "team": "Haas", "time": "1:35.964"},
            {"pos": 4, "driver": "Leclerc", "team": "Ferrari", "time": "1:36.011"},
            {"pos": 5, "driver": "Hamilton", "team": "Ferrari", "time": "1:36.092"},
            {"pos": 6, "driver": "Lindblad", "team": "Racing Bulls", "time": "1:36.099"},
            {"pos": 7, "driver": "Hulkenberg", "team": "Audi", "time": "1:36.180"},
            {"pos": 8, "driver": "Bearman", "team": "Haas", "time": "1:36.429"},
            {"pos": 9, "driver": "Gasly", "team": "Alpine", "time": "1:36.505"},
            {"pos": 10, "driver": "Colapinto", "team": "Alpine", "time": "1:36.783"},
        ],
    },
]


# ═══════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_pit_crew_rankings():
    """Return all teams sorted by consistency_score descending."""
    rankings = []
    for team, stats in PIT_CREW_STATS.items():
        rankings.append({"team": team, **stats})
    rankings.sort(key=lambda x: x["consistency_score"], reverse=True)
    return rankings


def get_pit_crew_for_team(team_name):
    """Return detailed pit crew stats for a specific team, or None if not found."""
    # Case-insensitive / partial match
    for team, stats in PIT_CREW_STATS.items():
        if team.lower() == team_name.lower() or team.lower().replace(" ", "") == team_name.lower().replace(" ", ""):
            return {"team": team, **stats}
    return None


def get_fastest_lap_rankings():
    """Return all drivers sorted by fastest lap propensity descending."""
    rankings = []
    for driver, score in FASTEST_LAP_PROPENSITY.items():
        rankings.append({"driver": driver, "propensity": score})
    rankings.sort(key=lambda x: x["propensity"], reverse=True)
    return rankings


def get_circuit_records(circuit_name):
    """Return race and qualifying records for a circuit, or None if not found."""
    # Case-insensitive lookup
    for circuit, records in CIRCUIT_LAP_RECORDS.items():
        if circuit.lower() == circuit_name.lower():
            return {"circuit": circuit, **records}
    return None


def pit_stop_impact(team_name):
    """
    Estimated seconds gained/lost per race vs grid average.
    Positive = time saved (better than average).
    Assumes ~2 pit stops per race.
    """
    stats = get_pit_crew_for_team(team_name)
    if stats is None:
        return None

    # Calculate grid average
    all_times = [s["avg_time"] for s in PIT_CREW_STATS.values()]
    grid_avg = sum(all_times) / len(all_times)

    # Impact per race (assume 2 stops)
    delta_per_stop = grid_avg - stats["avg_time"]
    stops_per_race = 2
    impact = round(delta_per_stop * stops_per_race, 2)
    return impact


def get_race_fastest_laps(year=2026):
    """Return list of race fastest lap results for the given year."""
    if year == 2026:
        return RACE_FASTEST_LAPS_2026
    return []
