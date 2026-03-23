"""
Kelly Criterion Bet Sizing.
Identifies value bets where model probability exceeds bookmaker implied probability.
Uses quarter-Kelly for conservative sizing.
"""
from src.config import BOOKIE_ODDS_RACE_WIN, BOOKIE_ODDS_PODIUM

def kelly_fraction(model_prob, decimal_odds):
    b = decimal_odds - 1
    p = model_prob
    q = 1 - p
    if b <= 0:
        return 0.0
    f = (b * p - q) / b
    return round(max(0, f) * 0.25, 4)  # quarter-Kelly

def find_value_bets(mc_results, bet_type="win"):
    odds_dict = BOOKIE_ODDS_RACE_WIN if bet_type == "win" else BOOKIE_ODDS_PODIUM
    pct_key = "win_pct" if bet_type == "win" else "podium_pct"
    bets = []
    for driver, odds in odds_dict.items():
        if driver not in mc_results:
            continue
        model_pct = mc_results[driver][pct_key]
        model_prob = model_pct / 100.0
        implied_prob = 1.0 / odds
        edge = model_prob - implied_prob
        kelly = kelly_fraction(model_prob, odds)
        bets.append({
            "driver": driver,
            "bet_type": bet_type,
            "model_pct": model_pct,
            "bookie_odds": odds,
            "implied_pct": round(implied_prob * 100, 1),
            "edge_pp": round(edge * 100, 1),
            "kelly_fraction": kelly,
            "verdict": "BACK" if edge > 0.02 else ("FADE" if edge < -0.02 else "NEUTRAL"),
        })
    return sorted(bets, key=lambda x: x["edge_pp"], reverse=True)
