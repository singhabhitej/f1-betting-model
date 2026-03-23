#!/usr/bin/env python3
"""Post-race Elo updater. Edit RACE_RESULT below, then run: python update_elo.py"""
from src.elo_system import update_elo, save_elo, load_elo
from src.config import DRIVER_ELO

# Paste actual finishing order after each race (P1 first)
RACE_RESULT = [
    "Russell", "Antonelli", "Leclerc", "Hamilton",
    "Norris", "Verstappen", "Bearman", "Lindblad",
    "Bortoleto", "Gasly", "Tsunoda", "Lawson",
    "Piastri", "Doohan", "Sainz", "Albon",
    "Stroll", "Colapinto", "Pourchaire",
]
# DNF drivers are excluded from the list

if __name__ == "__main__":
    elo = load_elo()
    if not elo:
        elo = dict(DRIVER_ELO)
    new_elo = update_elo(elo, RACE_RESULT)
    save_elo(new_elo)
    print("Updated Elo Ratings:")
    for d, r in sorted(new_elo.items(), key=lambda x: x[1], reverse=True):
        print(f"  {d}: {r:.0f}")
