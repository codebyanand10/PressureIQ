"""Unit tests for bowling baseline comparator."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.baseline_comparator import compare_with_bowling_baselines


def test_compare_with_bowling_baselines():
    """Verify differential and retention ratio calculations for bowling."""
    cfg = BowlingPressureConfig()

    hp_df = pd.DataFrame([
        {
            "player_id": "B1",
            "player_name": "Bowler 1",
            "legal_balls_bowled": 120,
            "wickets_credited": 6,
            "economy_rate": 8.0,
            "bowling_average": 20.0,
            "bowling_strike_rate": 15.0,
            "dot_ball_percentage": 40.0,
            "boundary_percentage_conceded": 15.0,
        }
    ])

    overall_df = pd.DataFrame([
        {
            "player_id": "B1",
            "economy_rate": 7.5,
            "bowling_average": 22.0,
            "bowling_strike_rate": 18.0,
            "dot_ball_percentage": 42.0,
            "boundary_percentage_conceded": 14.0,
        }
    ])

    lp_df = pd.DataFrame([
        {
            "player_id": "B1",
            "economy_rate": 7.0,
            "bowling_average": 24.0,
            "bowling_strike_rate": 20.0,
            "dot_ball_percentage": 45.0,
            "boundary_percentage_conceded": 12.0,
        }
    ])

    res = compare_with_bowling_baselines(hp_df, overall_df, lp_df, cfg)

    assert len(res) == 1
    row = res.iloc[0]

    # Economy delta vs overall: 8.0 - 7.5 = +0.5
    assert pytest.approx(row["economy_difference_overall"], 0.01) == 0.5
    # Economy retention ratio: (7.5 / 8.0) * 100
    assert pytest.approx(row["economy_retention_overall"], 0.01) == 93.75
    # Dot ball delta vs overall: 40.0 - 42.0 = -2.0
    assert pytest.approx(row["dot_ball_difference_overall"], 0.01) == -2.0
