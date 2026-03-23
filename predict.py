#!/usr/bin/env python3
"""One-click race prediction. Run: python predict.py"""
from src.auto_predict import run_prediction

if __name__ == "__main__":
    df, bets = run_prediction()
    print("\n=== RACE PREDICTIONS ===")
    print(df.to_string(index=False))
    print("\n=== VALUE BETS (Win) ===")
    for b in bets["win_bets"][:5]:
        print(f"  {b['verdict']} {b['driver']} @{b['bookie_odds']} | Model: {b['model_pct']}% | Edge: {b['edge_pp']}pp | Kelly: {b['kelly_fraction']}")
    print("\n=== VALUE BETS (Podium) ===")
    for b in bets["podium_bets"][:5]:
        print(f"  {b['verdict']} {b['driver']} @{b['bookie_odds']} | Model: {b['model_pct']}% | Edge: {b['edge_pp']}pp | Kelly: {b['kelly_fraction']}")
    print("\nPredictions saved to output/ folder.")
