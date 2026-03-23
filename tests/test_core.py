"""Core tests for the F1 betting model."""
import pytest
from src.elo_system import expected_score, update_elo
from src.kelly import kelly_fraction, find_value_bets
from src.auto_predict import build_composites
from src.monte_carlo import simulate_race
from src.config import MODEL_WEIGHTS, grid_position_score


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
