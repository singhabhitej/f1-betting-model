# F1 Betting Model — 50-Race Backtest Report

## Overview
- **Races evaluated:** 50
- **Monte Carlo simulations per race:** 5000
- **Period:** 2024 Season + 2025 Season + 2026 Rounds 1-2
- **Methodology:** Sequential backtest — model predictions use only data available at race time

> **Note:** 2024 and 2025 data is under the previous (2022-2025) technical regulations.
> 2026 Rounds 1-2 use the new 2026 regulations (active aero, new PU formula).
> The backtest validates the *model methodology*, not specific config values.

---

## Key Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Win Brier Score | 0.0407 | Lower is better (0=perfect, 1=worst) |
| Podium Brier Score | 0.0846 | Lower is better |
| Win Log Loss | 0.1428 | Lower is better |
| Podium Log Loss | 0.4077 | Lower is better |
| Winner in Top 1 | 32.0% | Model's #1 pick = actual winner |
| Winner in Top 3 | 72.0% | Actual winner in model's top 3 |
| Winner in Top 5 | 86.0% | Actual winner in model's top 5 |
| Avg Podium Overlap | 1.72 / 3 | Model's top 3 vs actual podium |
| Avg Spearman Correlation | 0.8585 | Predicted vs actual order (-1 to 1) |

### Reference Benchmarks
| Metric | Random Model | Good Model | Our Model |
|--------|-------------|------------|-----------|
| Win Brier | ~0.090 | <0.060 | 0.0407 |
| Winner Top 3 | ~15% | >50% | 72.0% |
| Spearman | ~0.00 | >0.30 | 0.8585 |

---

## Win Probability Calibration

| Predicted Range | Avg Predicted | Avg Actual | Count |
|----------------|---------------|------------|-------|
| 0%-5% | 0.0037 | 0.0136 | 806 |
| 5%-15% | 0.0908 | 0.1268 | 71 |
| 15%-30% | 0.2051 | 0.1493 | 67 |
| 30%-50% | 0.3962 | 0.2857 | 42 |
| 50%-100% | 0.6381 | 0.5000 | 16 |

## Podium Probability Calibration

| Predicted Range | Avg Predicted | Avg Actual | Count |
|----------------|---------------|------------|-------|
| 0%-5% | 0.0015 | 0.0121 | 661 |
| 5%-15% | 0.0996 | 0.2200 | 50 |
| 15%-30% | 0.2209 | 0.2895 | 76 |
| 30%-50% | 0.4017 | 0.3514 | 74 |
| 50%-100% | 0.6917 | 0.5887 | 141 |

---

## Performance by Era

| Era | Races | Avg Winner Rank | Winner Top 1% | Winner Top 3% | Avg Podium Overlap | Avg Spearman |
|-----|-------|-----------------|----------------|----------------|--------------------|--------------| 
| 2024_early | 11 | 1.45 | 81.8% | 90.9% | 1.73 | 0.8050 |
| 2024_late | 13 | 4.23 | 15.4% | 46.2% | 1.46 | 0.8970 |
| 2025_early | 12 | 2.67 | 16.7% | 83.3% | 1.83 | 0.8795 |
| 2025_late | 12 | 2.67 | 25.0% | 75.0% | 2.00 | 0.8508 |
| 2026 | 2 | 3.50 | 0.0% | 50.0% | 1.00 | 0.8229 |

---

## Race-by-Race Results

| # | Year | Race | Circuit | Winner | Model Rank | Win% | Podium Overlap | Spearman |
|---|------|------|---------|--------|------------|------|----------------|----------|
| 1 | 2024 | Bahrain Grand Prix | Bahrain | Verstappen | #1 | 54.6% | 1/3 | 0.889 |
| 2 | 2024 | Saudi Arabia Grand Prix | Jeddah | Verstappen | #1 | 77.1% | 3/3 | 0.967 |
| 3 | 2024 | Australia Grand Prix | Melbourne | Sainz | #4 | 1.6% | 1/3 | 0.332 |
| 4 | 2024 | Japan Grand Prix | Suzuka | Verstappen | #1 | 42.1% | 2/3 | 0.984 |
| 5 | 2024 | China Grand Prix | Shanghai | Verstappen | #1 | 53.5% | 2/3 | 0.977 |
| 6 | 2024 | United States Grand Prix | Miami | Verstappen | #1 | 60.6% | 3/3 | 0.698 |
| 7 | 2024 | Italy Grand Prix | Imola | Verstappen | #1 | 61.2% | 2/3 | 0.961 |
| 8 | 2024 | Canada Grand Prix | Montreal | Verstappen | #1 | 67.0% | 1/3 | 0.405 |
| 9 | 2024 | Monaco Grand Prix | Monaco | Leclerc | #3 | 2.9% | 1/3 | 0.732 |
| 10 | 2024 | Spain Grand Prix | Barcelona | Verstappen | #1 | 81.2% | 1/3 | 0.940 |
| 11 | 2024 | Austria Grand Prix | Spielberg | Verstappen | #1 | 66.7% | 2/3 | 0.971 |
| 12 | 2024 | United Kingdom Grand Prix | Silverstone | Hamilton | #7 | 1.2% | 2/3 | 0.635 |
| 13 | 2024 | Hungary Grand Prix | Budapest | Piastri | #3 | 12.0% | 2/3 | 0.970 |
| 14 | 2024 | Belgium Grand Prix | Spa | Russell | #7 | 1.5% | 1/3 | 0.944 |
| 15 | 2024 | Netherlands Grand Prix | Zandvoort | Norris | #2 | 18.6% | 2/3 | 0.970 |
| 16 | 2024 | Italy Grand Prix | Monza | Leclerc | #5 | 4.0% | 2/3 | 0.959 |
| 17 | 2024 | Azerbaijan Grand Prix | Baku | Piastri | #3 | 22.5% | 1/3 | 0.731 |
| 18 | 2024 | Mexico Grand Prix | Mexico City | Sainz | #7 | 2.6% | 1/3 | 0.866 |
| 19 | 2024 | Brazil Grand Prix | Interlagos | Norris | #3 | 14.7% | 2/3 | 0.964 |
| 20 | 2024 | Singapore Grand Prix | Singapore | Norris | #1 | 31.4% | 2/3 | 0.982 |
| 21 | 2024 | United States Grand Prix | Las Vegas | Russell | #7 | 0.9% | 0/3 | 0.919 |
| 22 | 2024 | United States Grand Prix | Austin | Leclerc | #4 | 16.1% | 1/3 | 0.973 |
| 23 | 2024 | Qatar Grand Prix | Lusail | Piastri | #5 | 11.7% | 1/3 | 0.817 |
| 24 | 2024 | United Arab Emirates Gran | Yas Marina | Norris | #1 | 29.8% | 2/3 | 0.932 |
| 25 | 2025 | Australia Grand Prix | Melbourne | Norris | #1 | 34.6% | 1/3 | 0.889 |
| 26 | 2025 | China Grand Prix | Shanghai | Hamilton | #6 | 11.0% | 0/3 | 0.926 |
| 27 | 2025 | Saudi Arabian Grand Prix | Jeddah | Piastri | #2 | 17.2% | 2/3 | 0.985 |
| 28 | 2025 | Japanese Grand Prix | Suzuka | Verstappen | #3 | 17.3% | 3/3 | 0.991 |
| 29 | 2025 | United States Grand Prix | Miami | Norris | #2 | 29.3% | 2/3 | 0.552 |
| 30 | 2025 | Bahrain Grand Prix | Bahrain | Piastri | #2 | 34.1% | 2/3 | 0.979 |
| 31 | 2025 | Italy Grand Prix | Imola | Verstappen | #3 | 8.1% | 3/3 | 0.990 |
| 32 | 2025 | Monaco Grand Prix | Monaco | Norris | #1 | 46.0% | 2/3 | 0.878 |
| 33 | 2025 | Spain Grand Prix | Barcelona | Piastri | #2 | 37.5% | 2/3 | 0.939 |
| 34 | 2025 | Canada Grand Prix | Montreal | Russell | #6 | 0.2% | 1/3 | 0.738 |
| 35 | 2025 | Austria Grand Prix | Spielberg | Norris | #2 | 31.2% | 2/3 | 0.818 |
| 36 | 2025 | United Kingdom Grand Prix | Silverstone | Norris | #2 | 38.1% | 2/3 | 0.869 |
| 37 | 2025 | Hungarian Grand Prix | Budapest | Norris | #2 | 40.4% | 2/3 | 0.967 |
| 38 | 2025 | Belgium Grand Prix | Spa | Verstappen | #6 | 0.8% | 2/3 | 0.829 |
| 39 | 2025 | Dutch Grand Prix | Zandvoort | Piastri | #1 | 46.7% | 2/3 | 0.901 |
| 40 | 2025 | Italy Grand Prix | Monza | Verstappen | #3 | 2.8% | 3/3 | 0.993 |
| 41 | 2025 | Azerbaijan Grand Prix | Baku | Verstappen | #3 | 7.4% | 1/3 | 0.614 |
| 42 | 2025 | Singapore Grand Prix | Singapore | Russell | #4 | 1.4% | 2/3 | 0.959 |
| 43 | 2025 | United States Grand Prix | Austin | Verstappen | #1 | 37.7% | 1/3 | 0.541 |
| 44 | 2025 | Mexico Grand Prix | Mexico City | Norris | #3 | 13.0% | 2/3 | 0.937 |
| 45 | 2025 | Brazil Grand Prix | Interlagos | Norris | #2 | 17.3% | 2/3 | 0.731 |
| 46 | 2025 | United States Grand Prix | Las Vegas | Verstappen | #1 | 39.9% | 3/3 | 0.941 |
| 47 | 2025 | Qatar Grand Prix | Lusail | Piastri | #4 | 9.3% | 2/3 | 0.818 |
| 48 | 2025 | Abu Dhabi Grand Prix | Yas Marina | Verstappen | #2 | 27.8% | 2/3 | 0.979 |
| 49 | 2026 | Australian Grand Prix | Melbourne | Russell | #2 | 23.5% | 1/3 | 0.803 |
| 50 | 2026 | Chinese Grand Prix | Shanghai | Antonelli | #5 | 8.8% | 1/3 | 0.843 |

---

## Methodology Notes

### Model Pipeline (per race)
1. **Elo Ratings**: Start from pre-season estimates, update after each race using pairwise head-to-head comparisons
2. **Circuit Fit**: Team pace × circuit profile (power, aero, traction, tyre degradation)
3. **Weather Modifiers**: Cold tyre penalty, crosswind sensitivity, rain competence, air density
4. **Team Form**: Rolling 5-race window of constructor points performance
5. **Season Momentum**: Driver-level exponentially weighted recent results
6. **Composite Score**: Weighted combination of all factors
   - Elo: 23.5%, Circuit: 23.5%, Form: 17.6%, Weather: 11.8%, Reliability: 11.8%, Momentum: 11.8%
   - (grid_position weight redistributed since qualifying data not available in backtest)
7. **Monte Carlo**: N simulations modeling variance, DNF, safety car, rain, T1 incidents

### Fairness Constraints
- Model uses only information available *at the time* of each race prediction
- Elo and team pace evolve naturally through race results (no hindsight)
- Pre-season baselines reset at each new season
- Team pace uses EMA (α=0.15) for gradual adaptation

### Regulation Note
- 2024-2025: Previous technical regulations (2022-2025 era)
- 2026 R1-R2: New 2026 regulations (active aero, simplified PU, new aero philosophy)
- Cross-era team pace is not directly comparable — pre-season baselines account for regulation changes

*Report generated from 50-race backtest with 5000 MC simulations per race.*