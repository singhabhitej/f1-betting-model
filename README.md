# F1 2026 Betting Model

Quantitative prediction model for Formula 1 2026. Combines Elo ratings, circuit regression, team form analysis, season momentum, weather impact modeling, and Monte Carlo simulation to identify value bets against bookmaker odds using the Kelly Criterion.

Built for the 2026 regulation era: active aero, 50:50 ICE/electric split, flat floors, 22 cars across 11 teams (including new Cadillac entry and Sauber→Audi rebrand).

## Architecture

```
config.py         → Master configuration (race, teams, drivers, odds, weights)
                     ↓
elo_system.py     → Bayesian Elo ratings (pairwise head-to-head updates)
circuit_regression.py → Track DNA × team strength fit scoring
weather_engine.py → Cold tyre, crosswind, density, rain, high-temp modifiers
                     ↓
auto_predict.py   → Composite score builder (7 weighted factors)
                     ↓
monte_carlo.py    → 10,000-iteration race simulator (DNF, safety car, rain, T1 incidents)
                     ↓
kelly.py          → Kelly Criterion bet sizing (quarter-Kelly, BACK/FADE verdicts)
                     ↓
output/           → CSV predictions + JSON value bets
```

### Model Weights

| Factor | Weight | Description |
|--------|--------|-------------|
| Elo | 20% | Driver skill rating from pairwise race comparisons |
| Circuit Fit | 20% | Team power/aero/traction/tyre_deg vs circuit demands |
| Team Form | 15% | Constructor performance from actual 2026 results |
| Grid Position | 15% | Qualifying result (P1=100, diminishing) — redistributed when unavailable |
| Weather | 10% | Cold tyre + crosswind + air density + rain modifiers |
| Reliability | 10% | Team mechanical reliability rating |
| Season Momentum | 10% | Recent race form and consistency |

### Monte Carlo Simulation

Each of 10,000 iterations:
1. Apply Gaussian noise (σ=0.08) to composite scores
2. Roll for DNFs (5% base rate per driver)
3. Roll for Turn 1 incidents (15% chance, 1-3 cars)
4. Roll for safety car (55% chance, compresses field by 40%)
5. Roll for rain (uses actual forecast probability, team-specific modifiers)
6. Rank surviving drivers → aggregate win%, podium%, top6%

## Setup

```bash
pip install -r requirements.txt
```

Requirements: `numpy`, `pandas`, `requests`, `pytest`

No API keys needed — uses free OpenF1 and Open-Meteo APIs.

## Usage

### Generate predictions
```bash
python predict.py
```

### Run backtesting
```bash
python -m src.backtest
```

### Update Elo after a race
```bash
# Manual: edit RACE_RESULT in update_elo.py, then:
python update_elo.py

# Automatic (from GitHub Actions):
python update_elo.py --auto
```

### Fetch live weather data
```bash
python -m src.auto_ingest
```

### Run tests
```bash
python -m pytest tests/ -v
```

## Pre-Race Configuration

Before each race weekend, update `src/config.py`:

1. `RACE` — Round number, circuit name, lap count, sprint flag
2. `CIRCUIT_PROFILE` — Power/aero/traction/tyre_deg demands
3. `WEATHER` — Forecast (or let `auto_ingest.py` fetch it)
4. `BOOKIE_ODDS_RACE_WIN` / `BOOKIE_ODDS_PODIUM` — Current betting lines
5. `GRID_POSITION` — Post-qualifying grid (empty dict if quali hasn't happened)
6. `SEASON_MOMENTUM` — Update after each race
7. `DRIVER_ELO` — Update via `update_elo.py` after each race

## Automation

Three GitHub Actions workflows:

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| `weather_watch.yml` | Daily 08:00 UTC | Fetches weather forecast → regenerates predictions |
| `race_weekend.yml` | Every 6h Thu-Sun | Full data refresh + predictions |
| `post_race.yml` | Monday 06:00 UTC | Ingests results → updates Elo → regenerates predictions |

## Data Sources

- **OpenF1 API** — Race results, session data (free, no key)
- **Open-Meteo API** — 7-day weather forecasts (free, no key)
- **Manual** — Team pace attributes, bookie odds, circuit profiles
