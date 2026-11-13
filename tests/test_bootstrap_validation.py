"""Unit tests for Phase 9 match-level bootstrap validation."""

import numpy as np
import pandas as pd
import pytest

from src.validation.validation_config import ValidationConfig
from src.validation.bootstrap_validation import run_match_level_bootstrap


@pytest.fixture
def mock_bootstrap_inputs():
    """Synthetic inputs for testing bootstrap validation."""
    bat_pids = [f"bat_{i}" for i in range(15)]
    ranked_batters = pd.DataFrame({
        "player_id": bat_pids,
        "player_name": [f"Batter {i}" for i in range(15)],
        "rank": list(range(1, 16)),
        "final_fbpr": [80.0 - i * 2 for i in range(15)],
        "raw_fbpr": [82.0 - i * 2 for i in range(15)],
        "balls_faced": [150 - i * 5 for i in range(15)],
        "strike_rate": [170.0 - i * 2 for i in range(15)],
        "score_batting_consistency": [60.0] * 15,
        "score_batting_context": [65.0] * 15,
        "overall_strike_rate": [140.0] * 15,
    })

    bowl_pids = [f"bowl_{i}" for i in range(15)]
    ranked_bowlers = pd.DataFrame({
        "player_id": bowl_pids,
        "player_name": [f"Bowler {i}" for i in range(15)],
        "rank": list(range(1, 16)),
        "final_fbor": [55.0 - i * 1 for i in range(15)],
        "raw_fbor": [56.0 - i * 1 for i in range(15)],
        "legal_balls_bowled": [180 - i * 5 for i in range(15)],
        "economy_rate": [7.5 + i * 0.1 for i in range(15)],
        "score_bowling_consistency": [60.0] * 15,
        "score_bowling_context": [65.0] * 15,
        "overall_economy_rate": [8.0] * 15,
    })

    # Synthetic match level rows (3 matches per player)
    bat_match_rows = []
    for pid in bat_pids:
        for m in range(4):
            bat_match_rows.append({
                "player_id": pid,
                "match_id": m,
                "hp_balls": 25,
                "hp_runs": 40,
                "hp_fours": 3,
                "hp_sixes": 2,
                "hp_dots": 8,
                "hp_dismissals": 0,
            })
    bat_match_agg = pd.DataFrame(bat_match_rows)

    bowl_match_rows = []
    for pid in bowl_pids:
        for m in range(4):
            bowl_match_rows.append({
                "player_id": pid,
                "match_id": m,
                "hp_legal_balls": 24,
                "hp_runs_conceded": 30,
                "hp_dots": 10,
                "hp_wickets": 1,
            })
    bowl_match_agg = pd.DataFrame(bowl_match_rows)

    return ranked_batters, ranked_bowlers, bat_match_agg, bowl_match_agg


def test_match_level_bootstrap_reproducibility(mock_bootstrap_inputs):
    """Verify that bootstrap runs yield reproducible results with fixed seed."""
    r_bat, r_bowl, b_m, bw_m = mock_bootstrap_inputs
    cfg1 = ValidationConfig(quick_mode=True, bootstrap_iterations=5, random_seed=42)
    cfg2 = ValidationConfig(quick_mode=True, bootstrap_iterations=5, random_seed=42)

    bat_res1, bowl_res1 = run_match_level_bootstrap(r_bat, r_bowl, b_m, bw_m, cfg1)
    bat_res2, bowl_res2 = run_match_level_bootstrap(r_bat, r_bowl, b_m, bw_m, cfg2)

    pd.testing.assert_frame_equal(bat_res1, bat_res2)
    pd.testing.assert_frame_equal(bowl_res1, bowl_res2)


def test_bootstrap_confidence_interval_bounds(mock_bootstrap_inputs):
    """Verify that bootstrap confidence intervals are bounded and monotonically ordered."""
    r_bat, r_bowl, b_m, bw_m = mock_bootstrap_inputs
    cfg = ValidationConfig(quick_mode=True, bootstrap_iterations=10, random_seed=42)

    bat_res, bowl_res = run_match_level_bootstrap(r_bat, r_bowl, b_m, bw_m, cfg)

    # Check 95% CI bounds
    assert (bat_res["ci_95_lower"] <= bat_res["ci_95_upper"]).all()
    assert (bat_res["ci_90_lower"] >= bat_res["ci_95_lower"]).all()
    assert (bat_res["ci_90_upper"] <= bat_res["ci_95_upper"]).all()
    assert (bat_res["ci_95_width"] >= 0).all()

    # Probabilities in [0, 1]
    assert ((bat_res["prob_in_top_10"] >= 0.0) & (bat_res["prob_in_top_10"] <= 1.0)).all()
    assert ((bowl_res["prob_in_top_10"] >= 0.0) & (bowl_res["prob_in_top_10"] <= 1.0)).all()

