"""Unit tests for baseline comparison differentials and retention metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.batting_pressure.baseline_comparator import compare_with_baselines


def test_baseline_comparator_differentials():
    """Verify strike rate, average, boundary, and dot ball differentials against baselines."""
    hp_data = [{
        "player_id": "P1",
        "player_name": "Clutch Batter",
        "balls_faced": 50,
        "total_runs": 80,
        "strike_rate": 160.0,
        "batting_average": 40.0,
        "boundary_percentage": 60.0,
        "dot_ball_percentage": 30.0,
        "dismissals": 2,
        "dismissal_rate": 0.04,
    }]
    overall_base = [{
        "player_id": "P1",
        "strike_rate": 130.0,
        "batting_average": 30.0,
        "shrunk_strike_rate": 128.0,
        "shrunk_batting_average": 28.0,
        "boundary_percentage": 50.0,
        "dot_ball_percentage": 40.0,
        "dismissal_rate": 0.05,
        "baseline_reliability_level": "High",
    }]
    lp_base = [{
        "player_id": "P1",
        "strike_rate": 135.0,
        "batting_average": 32.0,
        "boundary_percentage": 52.0,
        "dot_ball_percentage": 38.0,
        "dismissal_rate": 0.045,
    }]

    comp_df = compare_with_baselines(
        high_pressure_df=pd.DataFrame(hp_data),
        overall_baseline_df=pd.DataFrame(overall_base),
        low_pressure_baseline_df=pd.DataFrame(lp_base),
    )
    p1 = comp_df.iloc[0]

    # Overall differentials
    assert round(p1["strike_rate_difference_overall"], 2) == 30.0
    assert round(p1["strike_rate_retention_overall"], 2) == round((160.0 / 130.0) * 100.0, 2)
    assert round(p1["average_difference_overall"], 2) == 10.0
    assert round(p1["boundary_percentage_difference_overall"], 2) == 10.0
    assert round(p1["dot_ball_difference_overall"], 2) == -10.0  # Fewer dot balls
    assert round(p1["dismissal_rate_difference_overall"], 3) == -0.010


def test_baseline_comparator_missing_baseline():
    """Verify that a player missing baseline data gets NaN, never fabricated zero."""
    hp_data = [{
        "player_id": "P_NEW",
        "player_name": "Debut Batter",
        "balls_faced": 20,
        "total_runs": 25,
        "strike_rate": 125.0,
        "batting_average": 25.0,
        "boundary_percentage": 40.0,
        "dot_ball_percentage": 45.0,
        "dismissals": 1,
        "dismissal_rate": 0.05,
    }]
    comp_df = compare_with_baselines(
        high_pressure_df=pd.DataFrame(hp_data),
        overall_baseline_df=pd.DataFrame(columns=["player_id", "strike_rate", "batting_average"]),
        low_pressure_baseline_df=pd.DataFrame(columns=["player_id", "strike_rate", "batting_average"]),
    )
    p = comp_df.iloc[0]
    assert pd.isna(p["overall_strike_rate"])
    assert pd.isna(p["strike_rate_difference"])
    assert pd.isna(p["strike_rate_retention"])

