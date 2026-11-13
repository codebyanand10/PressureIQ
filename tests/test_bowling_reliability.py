"""Unit tests for bowling sample reliability and bootstrap module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_reliability import (
    calculate_match_block_bootstrap_bowling,
    assess_bowling_reliability,
)


def test_calculate_match_block_bootstrap_bowling():
    """Verify bootstrap CI calculation returns valid intervals for sufficient sample."""
    deliv = pd.DataFrame([
        {"match_id": 1, "bowler_runs_calc": 8, "is_legal_calc": 6},
        {"match_id": 2, "bowler_runs_calc": 10, "is_legal_calc": 6},
        {"match_id": 3, "bowler_runs_calc": 6, "is_legal_calc": 6},
        {"match_id": 4, "bowler_runs_calc": 12, "is_legal_calc": 6},
    ])

    res = calculate_match_block_bootstrap_bowling(deliv, iterations=100, random_seed=42)

    assert not pd.isna(res["ci_lower_econ"])
    assert not pd.isna(res["ci_upper_econ"])
    assert res["ci_lower_econ"] <= res["ci_upper_econ"]


def test_assess_bowling_reliability_tiers():
    """Verify reliability tiers: High (>=120 balls), Medium (>=48 balls), Low (>=18 balls), Insufficient (<18)."""
    cfg = BowlingPressureConfig()

    bppi_df = pd.DataFrame([
        {"player_id": "B_HIGH", "bppi_b": 75.0, "economy_rate": 8.0, "legal_balls_bowled": 150, "matches_bowled": 10, "innings_bowled": 8, "wickets_credited": 10, "overall_baseline_reliability_level": "High"},
        {"player_id": "B_MED", "bppi_b": 65.0, "economy_rate": 8.5, "legal_balls_bowled": 60, "matches_bowled": 4, "innings_bowled": 3, "wickets_credited": 3, "overall_baseline_reliability_level": "Medium"},
        {"player_id": "B_LOW", "bppi_b": 55.0, "economy_rate": 9.0, "legal_balls_bowled": 24, "matches_bowled": 2, "innings_bowled": 2, "wickets_credited": 1, "overall_baseline_reliability_level": "Low"},
        {"player_id": "B_INSUF", "bppi_b": 50.0, "economy_rate": 9.5, "legal_balls_bowled": 12, "matches_bowled": 1, "innings_bowled": 1, "wickets_credited": 0, "overall_baseline_reliability_level": "Low"},
    ])

    hp_deliv = pd.DataFrame([
        {"match_id": 1, "bowler_id": "B_HIGH", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None, "bowling_pressure_score": 70.0},
        {"match_id": 2, "bowler_id": "B_HIGH", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None, "bowling_pressure_score": 70.0},
    ])

    rel_df = assess_bowling_reliability(bppi_df, hp_deliv, cfg)

    tier_map = rel_df.set_index("player_id")["reliability_level"].to_dict()
    assert tier_map["B_HIGH"] == "High"
    assert tier_map["B_MED"] == "Medium"
    assert tier_map["B_LOW"] == "Low"
    assert tier_map["B_INSUF"] == "Insufficient Data"
