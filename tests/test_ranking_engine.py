"""Unit tests for Phase 8 Unified Player Rating & Ranking Engine coordinator."""

import numpy as np
import pandas as pd
import pytest

from src.ranking.ranking_config import RankingConfig
from src.ranking.ranking_engine import calculate_unified_player_rankings


@pytest.fixture
def mock_ranking_inputs():
    """Create a minimal synthetic fixture for testing the ranking orchestrator."""
    np.random.seed(42)
    n_bat = 25
    bat_ids = [f"bat_{i}" for i in range(n_bat)]
    bat_names = [f"Batter {i}" for i in range(n_bat)]

    batting_bppi = pd.DataFrame({
        "player_id": bat_ids,
        "player_name": bat_names,
        "bppi": np.random.uniform(40, 80, n_bat),
        "balls_faced": np.random.randint(50, 200, n_bat),
        "innings_count": np.random.randint(5, 15, n_bat),
        "matches_count": np.random.randint(5, 15, n_bat),
    })

    batting_hp = pd.DataFrame({
        "player_id": bat_ids,
        "strike_rate": np.random.uniform(120, 180, n_bat),
        "dot_ball_pct": np.random.uniform(25, 45, n_bat),
        "boundary_pct": np.random.uniform(12, 25, n_bat),
        "balls_per_dismissal": np.random.uniform(15, 35, n_bat),
        "runs_scored": np.random.randint(100, 400, n_bat),
    })

    batting_comparison = pd.DataFrame({
        "player_id": bat_ids,
        "strike_rate_diff": np.random.uniform(-10, 30, n_bat),
        "dot_ball_pct_diff": np.random.uniform(-10, 5, n_bat),
        "boundary_pct_diff": np.random.uniform(-3, 8, n_bat),
        "balls_per_dismissal_diff": np.random.uniform(-5, 10, n_bat),
        "sr_delta": np.random.uniform(-10, 30, n_bat),
    })

    batting_rel = pd.DataFrame({
        "player_id": bat_ids,
        "sample_size": batting_bppi["balls_faced"],
        "variance": np.random.uniform(0.5, 2.0, n_bat),
    })

    batting_baseline = pd.DataFrame({
        "player_id": bat_ids,
        "baseline_strike_rate": np.random.uniform(120, 150, n_bat),
        "balls_faced": batting_bppi["balls_faced"] * 2,
    })

    n_bowl = 25
    bowl_ids = [f"bowl_{i}" for i in range(n_bowl)]
    bowl_names = [f"Bowler {i}" for i in range(n_bowl)]

    bowling_bppi = pd.DataFrame({
        "player_id": bowl_ids,
        "player_name": bowl_names,
        "bppi_b": np.random.uniform(40, 75, n_bowl),
        "legal_balls_bowled": np.random.randint(60, 240, n_bowl),
        "innings_bowled": np.random.randint(5, 15, n_bowl),
        "matches_bowled": np.random.randint(5, 15, n_bowl),
    })

    bowling_hp = pd.DataFrame({
        "player_id": bowl_ids,
        "economy_rate": np.random.uniform(6.5, 9.5, n_bowl),
        "dot_ball_pct": np.random.uniform(30, 50, n_bowl),
        "boundary_pct": np.random.uniform(10, 20, n_bowl),
        "wickets_taken": np.random.randint(3, 20, n_bowl),
        "strike_rate": np.random.uniform(12, 28, n_bowl),
    })

    bowling_comparison = pd.DataFrame({
        "player_id": bowl_ids,
        "economy_rate_diff": np.random.uniform(-1.5, 1.5, n_bowl),
        "dot_ball_pct_diff": np.random.uniform(-5, 10, n_bowl),
        "boundary_pct_diff": np.random.uniform(-5, 5, n_bowl),
        "wickets_taken_diff": np.random.uniform(-2, 5, n_bowl),
    })

    bowling_rel = pd.DataFrame({
        "player_id": bowl_ids,
        "sample_size": bowling_bppi["legal_balls_bowled"],
        "variance": np.random.uniform(0.5, 2.0, n_bowl),
    })

    bowling_baseline = pd.DataFrame({
        "player_id": bowl_ids,
        "baseline_economy": np.random.uniform(7.0, 9.0, n_bowl),
        "legal_balls_bowled": bowling_bppi["legal_balls_bowled"] * 2,
    })

    registry = pd.DataFrame({
        "player_id": bat_ids + bowl_ids,
        "player_name": bat_names + bowl_names,
        "country": ["India"] * 25 + ["Australia"] * 25,
        "data_quality_flag": [False] * 50,
    })

    return {
        "batting_bppi": batting_bppi,
        "batting_hp": batting_hp,
        "batting_comparison": batting_comparison,
        "batting_reliability": batting_rel,
        "batting_baseline": batting_baseline,
        "bowling_bppi": bowling_bppi,
        "bowling_hp": bowling_hp,
        "bowling_comparison": bowling_comparison,
        "bowling_reliability": bowling_rel,
        "bowling_baseline": bowling_baseline,
        "player_registry": registry,
    }


def test_calculate_unified_player_rankings_structure(mock_ranking_inputs):
    """Test full execution of ranking coordinator returning required structure."""
    cfg = RankingConfig()
    results = calculate_unified_player_rankings(inputs=mock_ranking_inputs, config=cfg)

    required_keys = [
        "top_10_batters",
        "top_10_bowlers",
        "all_batter_rankings",
        "all_bowler_rankings",
        "batting_eligibility",
        "bowling_eligibility",
        "excluded_players",
        "ranking_components",
        "ranking_explanations",
        "validation_checks",
        "fairness_audit",
        "configuration_summary",
    ]
    for key in required_keys:
        assert key in results, f"Missing key {key} in results dictionary"

    # Verify top 10 counts
    assert len(results["top_10_batters"]) == 10
    assert len(results["top_10_bowlers"]) == 10

    # Verify ranks are contiguous 1..10
    assert list(results["top_10_batters"]["rank"]) == list(range(1, 11))
    assert list(results["top_10_bowlers"]["rank"]) == list(range(1, 11))


def test_ranking_validation_passes(mock_ranking_inputs):
    """Test that all validation checks pass on the synthetic pipeline run."""
    results = calculate_unified_player_rankings(inputs=mock_ranking_inputs)
    validation = results["validation_checks"]
    for check_name, passed in validation.items():
        assert passed is True, f"Validation check failed: {check_name}"


def test_weights_profile_switching(mock_ranking_inputs):
    """Test that ranking can be executed under different configured weight profiles."""
    res_primary = calculate_unified_player_rankings(
        inputs=mock_ranking_inputs, weights_profile="primary"
    )
    res_balanced = calculate_unified_player_rankings(
        inputs=mock_ranking_inputs, weights_profile="balanced"
    )

    assert res_primary["configuration_summary"]["active_profile"] == "primary"
    assert res_balanced["configuration_summary"]["active_profile"] == "balanced"
    # Ratings should run without error and be bounded in [0, 100]
    assert (res_primary["top_10_batters"]["final_fbpr"] >= 0).all()
    assert (res_balanced["top_10_batters"]["final_fbpr"] <= 100).all()

