"""Unit tests for bowling baseline module.

Tests overall and low-pressure bowling baseline separation, pressure threshold filtering,
and registry integration.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.bowling_baseline import calculate_bowling_baselines
from src.baselines.baseline_config import BaselineConfig


def test_calculate_bowling_baselines_separation():
    """Verify that overall and low-pressure bowling baselines are separately calculated."""
    deliveries = pd.DataFrame({
        "delivery_sequence": [1, 2, 3, 4],
        "match_id": [101, 101, 101, 101],
        "innings": [1, 1, 1, 1],
        "bowler_id": ["BW1", "BW1", "BW1", "BW1"],
        "batter_runs": [0, 1, 4, 0],
        "extras_runs": [0, 0, 0, 0],
        "extras_type": [None, None, None, None],
        "delivery_runs": [0, 1, 4, 0],
        "is_legal_delivery": [True, True, True, True],
        "is_wicket": [False, False, False, True],
        "dismissal_type": [None, None, None, "Bowled"],
        "is_four": [False, False, True, False],
        "is_six": [False, False, False, False],
        "bowling_pressure_score": [20.0, 35.0, 70.0, 80.0], # 2 low pressure, 2 high pressure
        "delivery_ist_time": ["2024-04-01 19:30:00"] * 4,
    })

    registry = pd.DataFrame({
        "player_id": ["BW1"],
        "player_name": ["Jasprit Bumrah"],
    })

    cfg = BaselineConfig()
    bowl_overall, bowl_lp = calculate_bowling_baselines(deliveries, registry, cfg)

    assert len(bowl_overall) == 1
    assert len(bowl_lp) == 1

    # Overall has 4 legal balls, 5 runs conceded (1+4), 1 wicket
    assert bowl_overall.iloc[0]["legal_balls_bowled"] == 4
    assert bowl_overall.iloc[0]["runs_conceded"] == 5
    assert bowl_overall.iloc[0]["wickets_credited"] == 1
    assert bowl_overall.iloc[0]["baseline_type"] == "overall"

    # Low pressure has 2 legal balls (20.0 and 35.0 <= 39.99), 1 run conceded, 0 wickets
    assert bowl_lp.iloc[0]["legal_balls_bowled"] == 2
    assert bowl_lp.iloc[0]["runs_conceded"] == 1
    assert bowl_lp.iloc[0]["wickets_credited"] == 0
    assert bowl_lp.iloc[0]["baseline_type"] == "low_pressure"

