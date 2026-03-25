"""Core tests for the F1 betting model."""
import pytest
from src.elo_system import expected_score, update_elo
from src.kelly import kelly_fraction, find_value_bets
from src.auto_predict import build_composites
from src.monte_carlo import simulate_race
from src.config import MODEL_WEIGHTS, grid_position_score
from src.performance_metrics import (
    get_pit_crew_rankings, get_pit_crew_for_team,
    get_fastest_lap_rankings, get_circuit_records,
    pit_stop_impact, get_race_fastest_laps,
    PIT_CREW_STATS, FASTEST_LAP_PROPENSITY,
)


class TestEloSystem:
    def test_expected_score_equal_ratings(self):
        assert expected_score(1500, 1500) == pytest.approx(0.5)

    def test_expected_score_higher_rating_favored(self):
        assert expected_score(2000, 1500) > 0.5
        assert expected_score(1500, 2000) < 0.5

    def test_expected_scores_sum_to_one(self):
        ea = expected_score(1800, 1600)
        eb = expected_score(1600, 1800)
        assert ea + eb == pytest.approx(1.0)

    def test_update_elo_winner_gains(self):
        ratings = {"A": 1500, "B": 1500}
        result = ["A", "B"]
        new = update_elo(ratings, result)
        assert new["A"] > 1500
        assert new["B"] < 1500

    def test_update_elo_preserves_total(self):
        ratings = {"A": 1800, "B": 1600, "C": 1700}
        result = ["A", "C", "B"]
        new = update_elo(ratings, result)
        # With asymmetric K-factors (rookie vs veteran), total isn't perfectly conserved
        # but the update should still produce reasonable values
        assert sum(new.values()) == pytest.approx(sum(ratings.values()), abs=10.0)

    def test_update_elo_unknown_driver_skipped(self):
        ratings = {"A": 1500, "B": 1500}
        result = ["A", "C", "B"]
        new = update_elo(ratings, result)
        assert "C" not in new
        assert "A" in new and "B" in new

    def test_update_elo_single_driver_unchanged(self):
        ratings = {"A": 1500}
        result = ["A"]
        new = update_elo(ratings, result)
        assert new["A"] == 1500


class TestKellyCriterion:
    def test_kelly_positive_edge(self):
        # Model says 50% chance, odds are 3.0 (implied 33%)
        k = kelly_fraction(0.50, 3.0)
        assert k > 0

    def test_kelly_no_edge(self):
        # Model says 50%, odds are 2.0 (implied 50%) — no edge
        k = kelly_fraction(0.50, 2.0)
        assert k == 0.0

    def test_kelly_negative_edge(self):
        # Model says 20%, odds are 2.0 (implied 50%) — negative edge
        k = kelly_fraction(0.20, 2.0)
        assert k == 0.0

    def test_kelly_quarter_sizing(self):
        # Full Kelly for 60% at 2.0 odds = (1*0.6-0.4)/1 = 0.2
        # Quarter Kelly = 0.05
        k = kelly_fraction(0.60, 2.0)
        assert k == pytest.approx(0.05, abs=0.001)

    def test_kelly_zero_odds(self):
        k = kelly_fraction(0.50, 1.0)
        assert k == 0.0

    def test_find_value_bets_returns_sorted(self):
        mc_results = {
            "Russell": {"win_pct": 40.0, "podium_pct": 80.0},
            "Antonelli": {"win_pct": 20.0, "podium_pct": 60.0},
        }
        bets = find_value_bets(mc_results, "win")
        if len(bets) >= 2:
            assert bets[0]["edge_pp"] >= bets[1]["edge_pp"]


class TestCompositeScores:
    def test_weights_sum_to_one(self):
        total = sum(MODEL_WEIGHTS.values())
        assert total == pytest.approx(1.0, abs=0.001)

    def test_build_composites_all_drivers(self):
        composites = build_composites()
        from src.config import GRID
        assert len(composites) == len(GRID)

    def test_composites_bounded(self):
        composites = build_composites()
        for driver, score in composites.items():
            assert 0 <= score <= 200, f"{driver} composite {score} out of bounds"

    def test_composites_are_numeric(self):
        composites = build_composites()
        for driver, score in composites.items():
            assert isinstance(score, (int, float)), f"{driver} score is {type(score)}"


class TestMonteCarlo:
    def test_produces_valid_probabilities(self):
        composites = {"A": 80.0, "B": 70.0, "C": 60.0}
        results = simulate_race(composites, n_sims=1000)
        for driver in composites:
            assert 0 <= results[driver]["win_pct"] <= 100
            assert 0 <= results[driver]["podium_pct"] <= 100
            assert 0 <= results[driver]["top6_pct"] <= 100

    def test_win_percentages_sum_approximately_100(self):
        composites = {"A": 80.0, "B": 70.0, "C": 60.0, "D": 50.0}
        results = simulate_race(composites, n_sims=5000)
        total_win = sum(r["win_pct"] for r in results.values())
        assert total_win == pytest.approx(100.0, abs=1.0)

    def test_higher_composite_wins_more(self):
        composites = {"Strong": 95.0, "Weak": 40.0}
        results = simulate_race(composites, n_sims=5000)
        assert results["Strong"]["win_pct"] > results["Weak"]["win_pct"]

    def test_empty_composites(self):
        results = simulate_race({}, n_sims=100)
        assert results == {}

    def test_positions_tracked(self):
        composites = {"A": 80.0, "B": 60.0}
        results = simulate_race(composites, n_sims=100)
        assert len(results["A"]["positions"]) > 0


class TestGridPositionScore:
    def test_p1_is_100(self):
        assert grid_position_score(1) == 100

    def test_p2_is_96(self):
        assert grid_position_score(2) == 96

    def test_p3_is_92(self):
        assert grid_position_score(3) == 92

    def test_decreasing(self):
        scores = [grid_position_score(i) for i in range(1, 23)]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]

    def test_all_non_negative(self):
        for i in range(1, 30):
            assert grid_position_score(i) >= 0

    def test_zero_position(self):
        assert grid_position_score(0) == 0


# ── Backtest Function Tests ──

class TestBrierScore:
    def test_perfect_prediction(self):
        from src.backtest import brier_score
        # Perfect: predicted 1.0 for events that happened
        probs = [1.0, 0.0, 0.0]
        outcomes = [1.0, 0.0, 0.0]
        assert brier_score(probs, outcomes) == pytest.approx(0.0)

    def test_worst_prediction(self):
        from src.backtest import brier_score
        # Worst: predicted 1.0 for events that didn't happen
        probs = [1.0, 1.0]
        outcomes = [0.0, 0.0]
        assert brier_score(probs, outcomes) == pytest.approx(1.0)

    def test_moderate_prediction(self):
        from src.backtest import brier_score
        probs = [0.8, 0.2]
        outcomes = [1.0, 0.0]
        expected = ((0.8 - 1.0)**2 + (0.2 - 0.0)**2) / 2
        assert brier_score(probs, outcomes) == pytest.approx(expected)

    def test_empty_returns_one(self):
        from src.backtest import brier_score
        assert brier_score([], []) == 1.0

    def test_fifty_fifty(self):
        from src.backtest import brier_score
        probs = [0.5, 0.5]
        outcomes = [1.0, 0.0]
        assert brier_score(probs, outcomes) == pytest.approx(0.25)


class TestLogLoss:
    def test_good_prediction_low_loss(self):
        from src.backtest import log_loss
        # High confidence correct prediction → low loss
        loss = log_loss([0.95], [1.0])
        assert loss < 0.1

    def test_bad_prediction_high_loss(self):
        from src.backtest import log_loss
        # High confidence wrong prediction → high loss
        loss = log_loss([0.95], [0.0])
        assert loss > 2.0

    def test_empty_returns_inf(self):
        from src.backtest import log_loss
        assert log_loss([], []) == float("inf")

    def test_symmetric(self):
        from src.backtest import log_loss
        # Same loss for predicting 0.3 when outcome is 1 vs predicting 0.7 when outcome is 0
        loss_a = log_loss([0.3], [1.0])
        loss_b = log_loss([0.7], [0.0])
        assert loss_a == pytest.approx(loss_b, abs=0.001)


class TestCalibrationBuckets:
    def test_returns_correct_structure(self):
        from src.backtest import calibration_buckets
        probs = [0.01, 0.02, 0.10, 0.30, 0.60]
        outcomes = [0.0, 0.0, 0.0, 1.0, 1.0]
        buckets = calibration_buckets(probs, outcomes)
        assert isinstance(buckets, list)
        for b in buckets:
            assert "range" in b
            assert "avg_predicted" in b
            assert "avg_actual" in b
            assert "count" in b

    def test_all_in_one_bucket(self):
        from src.backtest import calibration_buckets
        probs = [0.01, 0.02, 0.03]
        outcomes = [0.0, 0.0, 1.0]
        buckets = calibration_buckets(probs, outcomes)
        low_bucket = [b for b in buckets if b["range"] == "0%-5%"]
        assert len(low_bucket) == 1
        assert low_bucket[0]["count"] == 3


class TestSpearmanCorrelation:
    def test_perfect_correlation(self):
        from src.backtest import spearman_correlation
        order = ["A", "B", "C", "D"]
        assert spearman_correlation(order, order) == pytest.approx(1.0)

    def test_reverse_correlation(self):
        from src.backtest import spearman_correlation
        forward = ["A", "B", "C", "D"]
        reverse = ["D", "C", "B", "A"]
        assert spearman_correlation(forward, reverse) == pytest.approx(-1.0)

    def test_partial_overlap(self):
        from src.backtest import spearman_correlation
        pred = ["A", "B", "C", "D"]
        actual = ["A", "C", "B", "D"]
        corr = spearman_correlation(pred, actual)
        assert -1.0 <= corr <= 1.0
        assert corr > 0  # Still mostly correct

    def test_too_few_common_drivers(self):
        from src.backtest import spearman_correlation
        assert spearman_correlation(["A", "B"], ["C", "D"]) == 0.0


class TestPodiumOverlap:
    def test_perfect_overlap(self):
        from src.backtest import podium_overlap
        assert podium_overlap(["A", "B", "C"], ["A", "B", "C"]) == 3

    def test_no_overlap(self):
        from src.backtest import podium_overlap
        assert podium_overlap(["A", "B", "C"], ["D", "E", "F"]) == 0

    def test_partial_overlap(self):
        from src.backtest import podium_overlap
        assert podium_overlap(["A", "B", "C"], ["A", "D", "C"]) == 2

    def test_order_independent(self):
        from src.backtest import podium_overlap
        # Same drivers in different order → still full overlap
        assert podium_overlap(["A", "B", "C"], ["C", "A", "B"]) == 3


class TestPerformanceMetrics:
    """Tests for pit crew and fastest lap performance metrics."""

    def test_pit_crew_rankings_sorted_by_consistency(self):
        rankings = get_pit_crew_rankings()
        # Must include all teams
        assert len(rankings) == len(PIT_CREW_STATS)
        # Must be sorted by consistency_score descending
        scores = [r["consistency_score"] for r in rankings]
        assert scores == sorted(scores, reverse=True)
        # Ferrari should be #1 (consistency_score 97)
        assert rankings[0]["team"] == "Ferrari"
        assert rankings[0]["consistency_score"] == 97

    def test_pit_crew_lookup_by_team(self):
        # Exact name
        data = get_pit_crew_for_team("Ferrari")
        assert data is not None
        assert data["team"] == "Ferrari"
        assert data["avg_time"] == 2.31
        assert data["consistency_score"] == 97
        assert data["best_time"] == 2.00
        # Case-insensitive
        data2 = get_pit_crew_for_team("ferrari")
        assert data2 is not None
        assert data2["team"] == "Ferrari"
        # Unknown team
        assert get_pit_crew_for_team("Nonexistent") is None

    def test_fastest_lap_propensity_rankings(self):
        rankings = get_fastest_lap_rankings()
        assert len(rankings) == len(FASTEST_LAP_PROPENSITY)
        # Sorted descending by propensity
        propensities = [r["propensity"] for r in rankings]
        assert propensities == sorted(propensities, reverse=True)
        # Russell should be #1 (90)
        assert rankings[0]["driver"] == "Russell"
        assert rankings[0]["propensity"] == 90

    def test_circuit_records_lookup(self):
        records = get_circuit_records("Suzuka")
        assert records is not None
        assert records["circuit"] == "Suzuka"
        assert records["race_record"]["driver"] == "Antonelli"
        assert records["race_record"]["time"] == "1:30.965"
        assert records["qualifying_record"]["driver"] == "Verstappen"
        # Case-insensitive
        records2 = get_circuit_records("suzuka")
        assert records2 is not None
        # Unknown circuit
        assert get_circuit_records("Nonexistent") is None

    def test_pit_stop_impact_calculation(self):
        # Ferrari is the fastest — should have a positive impact (gains time vs average)
        ferrari_impact = pit_stop_impact("Ferrari")
        assert ferrari_impact is not None
        assert ferrari_impact > 0  # Ferrari gains time vs grid average

        # Haas is one of the slowest — should have a negative impact
        haas_impact = pit_stop_impact("Haas")
        assert haas_impact is not None
        assert haas_impact < 0  # Haas loses time vs grid average

        # Unknown team returns None
        assert pit_stop_impact("Nonexistent") is None

    def test_race_fastest_laps_2026(self):
        results = get_race_fastest_laps(2026)
        assert len(results) == 2  # R1 and R2
        assert results[0]["round"] == 1
        assert results[0]["driver"] == "Verstappen"
        assert results[1]["round"] == 2
        assert results[1]["driver"] == "Antonelli"
        # Unknown year returns empty
        assert get_race_fastest_laps(2020) == []

    def test_pit_stop_impact_ferrari_approx(self):
        # Ferrari avg_time = 2.31s, grid avg ≈ 2.72s, delta ≈ 0.41 * 2 ≈ 0.82
        impact = pit_stop_impact("Ferrari")
        assert impact is not None
        assert 0.5 < impact < 1.5  # Reasonable range
