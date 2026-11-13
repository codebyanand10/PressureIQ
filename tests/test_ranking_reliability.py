"""Unit tests for Phase 8 statistical reliability and shrinkage module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.ranking.ranking_config import RankingConfig
from src.ranking.reliability import (
    apply_reliability_adjustment_batting,
    apply_reliability_adjustment_bowling,
)


def test_apply_reliability_adjustment_batting():
    """Verify Empirical Bayes shrinkage behavior for batting."""
    cfg = RankingConfig()

    df = pd.DataFrame([
        # High volume batter (low shrinkage from 80.0 toward cohort median ~55.0)
        {"player_id": "P_HIGH", "raw_fbpr": 80.0, "balls_faced": 250, "bootstrap_se_sr": 8.0},
        # Low volume batter with same raw score (stronger shrinkage toward cohort median)
        {"player_id": "P_LOW", "raw_fbpr": 80.0, "balls_faced": 40, "bootstrap_se_sr": 18.0},
        # Average batters establishing cohort prior
        {"player_id": "P_AVG1", "raw_fbpr": 55.0, "balls_faced": 100, "bootstrap_se_sr": 10.0},
        {"player_id": "P_AVG2", "raw_fbpr": 50.0, "balls_faced": 120, "bootstrap_se_sr": 10.0},
        {"player_id": "P_AVG3", "raw_fbpr": 45.0, "balls_faced": 80, "bootstrap_se_sr": 12.0},
    ])

    res = apply_reliability_adjustment_batting(df, cfg)

    assert "final_fbpr" in res.columns
    assert "ci_lower_fbpr" in res.columns
    assert "ci_upper_fbpr" in res.columns

    p_high = res[res["player_id"] == "P_HIGH"].iloc[0]
    p_low = res[res["player_id"] == "P_LOW"].iloc[0]

    # Both had raw_fbpr 80.0, but P_HIGH has 250 balls vs 40 balls -> P_HIGH shrinks less!
    assert p_high["final_fbpr"] > p_low["final_fbpr"]
    # P_LOW has higher standard error and wider CI
    assert p_low["ci_width_fbpr"] > p_high["ci_width_fbpr"]


def test_apply_reliability_adjustment_bowling():
    """Verify Empirical Bayes shrinkage behavior for bowling."""
    cfg = RankingConfig()

    df = pd.DataFrame([
        # High volume bowler (low shrinkage from 75.0 toward cohort median ~50.0)
        {"player_id": "B_HIGH", "raw_fbor": 75.0, "legal_balls_bowled": 200, "bootstrap_se_econ": 0.5},
        # Low volume bowler with same raw score (stronger shrinkage toward cohort median)
        {"player_id": "B_LOW", "raw_fbor": 75.0, "legal_balls_bowled": 48, "bootstrap_se_econ": 1.5},
        # Average bowlers establishing cohort prior
        {"player_id": "B_AVG1", "raw_fbor": 50.0, "legal_balls_bowled": 120, "bootstrap_se_econ": 0.8},
        {"player_id": "B_AVG2", "raw_fbor": 48.0, "legal_balls_bowled": 100, "bootstrap_se_econ": 0.9},
        {"player_id": "B_AVG3", "raw_fbor": 45.0, "legal_balls_bowled": 80, "bootstrap_se_econ": 1.0},
    ])

    res = apply_reliability_adjustment_bowling(df, cfg)

    b_high = res[res["player_id"] == "B_HIGH"].iloc[0]
    b_low = res[res["player_id"] == "B_LOW"].iloc[0]

    assert b_high["final_fbor"] > b_low["final_fbor"]
    assert b_low["ci_width_fbor"] > b_high["ci_width_fbor"]

