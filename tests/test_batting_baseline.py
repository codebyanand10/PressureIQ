"""Unit tests for batting baseline module.

Tests overall and low-pressure baseline separation, pressure score filtering,
and registry mapping.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.batting_baseline import calculate_batting_baselines
from src.baselines.baseline_config import BaselineConfig


def test_calculate_batting_baselines_separation():
    """Verify that overall and low-pressure baselines are separately calculated and filtered."""
    deliveries = pd.DataFrame({
        "delivery_sequence": [1, 2, 3, 4],
        "match_id": [101, 101, 101, 101],
        "innings": [1, 1, 1, 1],
        "striker_id": ["P1", "P1", "P1", "P1"],
        "batter_runs": [1, 2, 4, 6],
        "extras_runs": [0, 0, 0, 0],
        "extras_type": [None, None, None, None],
        "is_four": [False, False, True, False],
        "is_six": [False, False, False, True],
        "is_wicket": [False, False, False, True],
        "dismissed_player_id": [None, None, None, "P1"],
        "batting_pressure_score": [15.0, 30.0, 65.0, 85.0], # 2 low pressure, 2 high pressure
        "delivery_ist_time": ["2024-04-01 19:30:00"] * 4,
    })

    registry = pd.DataFrame({
        "player_id": ["P1"],
        "player_name": ["Virat Kohli"],
    })

    cfg = BaselineConfig()
    bat_overall, bat_lp = calculate_batting_baselines(deliveries, registry, cfg)

    assert len(bat_overall) == 1
    assert len(bat_lp) == 1

    # Overall has 4 deliveries, 4 balls faced, 13 runs (1+2+4+6)
    assert bat_overall.iloc[0]["total_balls_faced"] == 4
    assert bat_overall.iloc[0]["total_runs"] == 13
    assert bat_overall.iloc[0]["baseline_type"] == "overall"

    # Low-pressure has only 2 deliveries (15.0 and 30.0 <= 39.99), 3 runs (1+2)
    assert bat_lp.iloc[0]["total_balls_faced"] == 2
    assert bat_lp.iloc[0]["total_runs"] == 3
    assert bat_lp.iloc[0]["baseline_type"] == "low_pressure"
    assert bat_lp.iloc[0]["dismissals"] == 0

