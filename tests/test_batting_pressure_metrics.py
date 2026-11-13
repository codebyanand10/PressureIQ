"""Unit tests for batting pressure metrics calculation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.batting_pressure.batting_pressure_metrics import (
    annotate_batting_deliveries,
    compute_batting_pressure_metrics,
)


def test_batting_metrics_wides_and_noballs():
    """Verify that wides do not count as balls faced, while no-balls and byes do."""
    data = [
        # Normal ball: 4 runs off bat
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_four": True, "is_six": False, "is_wicket": False},
        # Wide: 1 extra run, 0 runs off bat -> NOT a ball faced
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 0, "extras_runs": 1, "extras_type": "wide", "is_four": False, "is_six": False, "is_wicket": False},
        # No-ball: 1 extra run, 2 runs off bat -> IS a ball faced
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 2, "extras_runs": 1, "extras_type": "Overstep", "is_four": False, "is_six": False, "is_wicket": False},
        # Bye: 1 extra run, 0 runs off bat -> IS a ball faced
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 0, "extras_runs": 1, "extras_type": "bye", "is_four": False, "is_six": False, "is_wicket": False},
    ]
    df = pd.DataFrame(data)
    annotated = annotate_batting_deliveries(df)

    assert annotated["is_ball_faced"].tolist() == [1, 0, 1, 1]
    assert annotated["batter_runs_calc"].tolist() == [4, 0, 2, 0]

    metrics = compute_batting_pressure_metrics(df, group_col="striker_id")
    p1 = metrics[metrics["striker_id"] == "P1"].iloc[0]

    assert p1["balls_faced"] == 3
    assert p1["total_runs"] == 6
    assert p1["strike_rate"] == 200.0


def test_batting_metrics_zero_dismissals():
    """Verify that 0 dismissals results in NaN batting average (never zero)."""
    data = [
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 6, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": True, "is_wicket": False},
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_four": True, "is_six": False, "is_wicket": False},
    ]
    df = pd.DataFrame(data)
    metrics = compute_batting_pressure_metrics(df, group_col="striker_id")
    p1 = metrics[metrics["striker_id"] == "P1"].iloc[0]

    assert p1["dismissals"] == 0
    assert pd.isna(p1["batting_average"])
    assert p1["total_runs"] == 10
    assert p1["strike_rate"] == 500.0


def test_batting_metrics_dismissal_attribution():
    """Verify that a non-striker run out does not count as a striker dismissal."""
    data = [
        # Striker dismissed (caught)
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": True, "dismissed_player_id": "P1"},
        # Non-striker dismissed (run out)
        {"match_id": 1, "innings": 1, "striker_id": "P2", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": True, "dismissed_player_id": "P3"},
    ]
    df = pd.DataFrame(data)
    metrics = compute_batting_pressure_metrics(df, group_col="striker_id")

    p1 = metrics[metrics["striker_id"] == "P1"].iloc[0]
    p2 = metrics[metrics["striker_id"] == "P2"].iloc[0]

    assert p1["dismissals"] == 1
    assert p2["dismissals"] == 0
    assert pd.isna(p2["batting_average"])

