#!/usr/bin/env python3
"""Post-race Elo updater. Edit RACE_RESULT below, then run: python update_elo.py"""
import argparse
import logging

from src.elo_system import update_elo, save_elo, load_elo
from src.config import DRIVER_ELO

logger = logging.getLogger(__name__)

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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # B4 FIX: Add argparse so --auto flag works from GitHub Actions
    parser = argparse.ArgumentParser(description="Post-race Elo updater")
    parser.add_argument("--auto", action="store_true",
                        help="Run with auto-ingested results (from auto_ingest.py)")
    args = parser.parse_args()

    elo = load_elo()
    if not elo:
        elo = dict(DRIVER_ELO)

    if args.auto:
        # In auto mode, fetch results from the API
        from src.auto_ingest import fetch_race_results
        from src.config import RACE
        results = fetch_race_results(RACE["year"], RACE["round"] - 1)
        if results:
            elo = update_elo(elo, results)
            save_elo(elo)
            logger.info("Auto-updated Elo from API results")
        else:
            logger.warning("No results from API, Elo unchanged")
    else:
        # Manual mode: use hardcoded results above
        elo = update_elo(elo, SPRINT_RESULT)
        elo = update_elo(elo, RACE_RESULT)
        save_elo(elo)
        logger.info("Updated Elo Ratings (post-China GP):")
        for d, r in sorted(elo.items(), key=lambda x: x[1], reverse=True):
            logger.info("  %s: %.0f", d, r)
