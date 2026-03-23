#!/usr/bin/env python3
"""Post-race Elo updater. Edit RACE_RESULT below, then run: python update_elo.py"""
from src.elo_system import update_elo, save_elo, load_elo
from src.config import DRIVER_ELO

# ── China GP 2026 (Round 2) ── Race Result ──
# P1-P15 classified finishers. DNF/DNS excluded.
RACE_RESULT = [
    "Antonelli", "Russell", "Hamilton", "Leclerc",
    "Bearman", "Gasly", "Lawson", "Hadjar",
    "Sainz", "Colapinto", "Hulkenberg", "Lindblad",
    "Bottas", "Ocon", "Perez",
]
# DNF: Verstappen, Alonso, Stroll
# DNS: Norris, Piastri, Bortoleto, Albon

# ── China GP 2026 (Round 2) ── Sprint Result ──
SPRINT_RESULT = [
    "Russell", "Leclerc", "Hamilton", "Norris",
    "Antonelli", "Piastri", "Lawson",
]

if __name__ == "__main__":
    elo = load_elo()
    if not elo:
        elo = dict(DRIVER_ELO)

    # Update from sprint first, then race
    elo = update_elo(elo, SPRINT_RESULT)
    elo = update_elo(elo, RACE_RESULT)

    save_elo(elo)
    print("Updated Elo Ratings (post-China GP):")
    for d, r in sorted(elo.items(), key=lambda x: x[1], reverse=True):
        print(f"  {d}: {r:.0f}")
