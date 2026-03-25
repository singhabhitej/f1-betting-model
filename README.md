# F1 2026 Betting Model

Quantitative prediction model for Formula 1 2026. Combines Elo ratings, circuit regression, team form analysis, season momentum, weather impact modeling, and Monte Carlo simulation to identify value bets against bookmaker odds using the Kelly Criterion.

Built for the 2026 regulation era: active aero, 50:50 ICE/electric split, flat floors, 22 cars across 11 teams (including new Cadillac entry and Sauber→Audi rebrand).

**Backtested across 50 races** — Win Brier 0.041, Winner Top-3 accuracy 72%, Spearman rank correlation 0.86.

## Architecture

```
config.py              → Master configuration (race, teams, drivers, odds, weights)
                         ↓
elo_system.py          → Bayesian Elo ratings (pairwise head-to-head updates)
circuit_regression.py  → Track DNA × team strength fit scoring
weather_engine.py      → Cold tyre, crosswind, density, rain, high-temp modifiers
performance_metrics.py → Pit crew consistency + fastest lap propensity
                         ↓
auto_predict.py        → Composite score builder (7 weighted factors)
                         ↓
monte_carlo.py         → 10,000-iteration race simulator (DNF, safety car, rain, T1 incidents)
                         ↓
kelly.py               → Kelly Criterion bet sizing (quarter-Kelly, BACK/FADE verdicts)
                         ↓
api.py                 → FastAPI REST API (20+ endpoints, fantasy pricing, CORS)
                         ↓
output/                → CSV predictions, JSON value bets, backtest reports
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

## Quick Start

```bash
pip install -r requirements.txt
```

### Generate predictions
```bash
python predict.py
```

### Run the API locally
```bash
pip install fastapi uvicorn
uvicorn api:app --host 0.0.0.0 --port 5000
# Swagger docs at http://localhost:5000/docs
```

### Run backtesting (50 races)
```bash
python -m src.backtest
```

### Run tests
```bash
python -m pytest tests/ -v    # 54 tests
```

## REST API

The API serves predictions, fantasy pricing, pit crew data, and more. Full Swagger docs at `/docs`.

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/predictions` | All driver win/podium/top6 probabilities |
| `GET /api/predictions/{driver}` | Detailed prediction for one driver |
| `GET /api/fantasy/drivers` | Fantasy prices for all drivers (5M-30M) |
| `GET /api/fantasy/constructors` | Fantasy prices for all constructors |
| `GET /api/fantasy/all` | Complete price sheet (drivers + constructors) |
| `GET /api/value-bets` | Value bets with Kelly sizing |
| `GET /api/pitstops` | Pit crew consistency rankings |
| `GET /api/fastest-laps` | Fastest lap propensity rankings |
| `GET /api/teams/pace` | Team pace profiles |
| `GET /api/drivers/elo` | Elo ratings |
| `GET /api/circuit` | Circuit profile + weather |
| `GET /api/performance/summary` | Combined performance overview |
| `GET /api/model/refresh` | Force re-run Monte Carlo |

### Static Data Access (No Server Needed)

Your app can also fetch the latest predictions directly from GitHub:

```
https://raw.githubusercontent.com/singhabhitej/f1-betting-model/main/output/latest_predictions.json
https://raw.githubusercontent.com/singhabhitej/f1-betting-model/main/output/Japanese_Grand_Prix_predictions.csv
https://raw.githubusercontent.com/singhabhitej/f1-betting-model/main/output/Japanese_Grand_Prix_kelly.json
```

These files are automatically updated before each race weekend by GitHub Actions.

## Deployment

### Option A: Render (Recommended — Free Tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/singhabhitej/f1-betting-model)

1. Click the button above (or go to [render.com](https://render.com))
2. Connect your GitHub repo
3. Render auto-detects `render.yaml` and deploys
4. API is live at `https://f1-predictor-api.onrender.com`
5. Auto-deploys on every push to `main`

### Option B: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Option C: Docker (Any Platform)

```bash
docker build -t f1-predictor .
docker run -p 5000:5000 f1-predictor
```

Works on AWS ECS, Google Cloud Run, Azure Container Apps, Fly.io, etc.

### Option D: Manual (Any VPS)

```bash
git clone https://github.com/singhabhitej/f1-betting-model.git
cd f1-betting-model
pip install -r requirements.txt fastapi uvicorn
uvicorn api:app --host 0.0.0.0 --port 5000
```

## Automation (GitHub Actions)

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| `pre_race_predictions.yml` | Wed + Fri 10:00 UTC | Runs full model, generates predictions, commits JSON/CSV to repo |
| `weather_watch.yml` | Daily 08:00 UTC | Fetches weather forecast → regenerates predictions |
| `race_weekend.yml` | Every 6h Thu-Sun | Full data refresh + predictions |
| `post_race.yml` | Monday 06:00 UTC | Ingests results → updates Elo → regenerates predictions |

## Pre-Race Configuration

Before each race weekend, update `src/config.py`:

1. `RACE` — Round number, circuit name, lap count, sprint flag
2. `CIRCUIT_PROFILE` — Power/aero/traction/tyre_deg demands
3. `WEATHER` — Forecast (or let `auto_ingest.py` fetch it)
4. `BOOKIE_ODDS_RACE_WIN` / `BOOKIE_ODDS_PODIUM` — Current betting lines
5. `GRID_POSITION` — Post-qualifying grid (empty dict if quali hasn't happened)
6. `SEASON_MOMENTUM` — Update after each race
7. `DRIVER_ELO` — Update via `update_elo.py` after each race

## Data Sources

- **OpenF1 API** — Race results, session data (free, no key)
- **Open-Meteo API** — 7-day weather forecasts (free, no key)
- **DHL Fastest Pit Stop** — Pit crew performance data
- **Manual** — Team pace attributes, bookie odds, circuit profiles

## Project Structure

```
f1-betting-model/
├── api.py                    # FastAPI REST API (20+ endpoints)
├── predict.py                # CLI prediction runner
├── update_elo.py             # Post-race Elo updater
├── Dockerfile                # Container deployment
├── render.yaml               # Render one-click deploy
├── railway.json              # Railway deploy config
├── Procfile                  # Heroku/Railway process file
├── requirements.txt          # Python dependencies
├── src/
│   ├── config.py             # Master configuration
│   ├── auto_predict.py       # Prediction pipeline
│   ├── monte_carlo.py        # MC race simulator
│   ├── elo_system.py         # Bayesian Elo
│   ├── circuit_regression.py # Circuit fit scoring
│   ├── weather_engine.py     # Weather impact
│   ├── kelly.py              # Kelly Criterion bets
│   ├── backtest.py           # 50-race backtesting engine
│   ├── performance_metrics.py# Pit crew + fastest lap
│   └── auto_ingest.py        # Data ingestion
├── data/
│   └── historical_races.json # 50-race backtest dataset
├── output/                   # Generated predictions
├── tests/
│   └── test_core.py          # 54 tests
└── .github/workflows/        # CI/CD automation
```
