"""Unit tests for bowling pressure metrics calculation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_metrics import (
    annotate_bowling_deliveries,
    compute_bowling_pressure_metrics,
    compute_bowling_innings_consistency,
)


def test_bowling_metrics_extras_and_legal_deliveries():
    """Verify that wides/no-balls are charged to bowler, while byes/leg-byes are excluded.
    Verify that only legal deliveries count towards legal_balls_bowled.
    """
    data = [
        # Legal ball: 4 runs off bat -> 1 legal ball, 4 runs conceded
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": True, "is_six": False, "is_wicket": False, "wicket_type": None},
        # Wide: 1 extra run, 0 batter runs -> 0 legal balls, 1 run conceded
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 1, "extras_type": "wide", "is_legal_delivery": False, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
        # No-ball: 1 extra run, 2 off bat -> 0 legal balls, 3 runs conceded
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 2, "extras_runs": 1, "extras_type": "Overstep", "is_legal_delivery": False, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
        # Bye: 1 extra run, 0 off bat -> 1 legal ball, 0 runs conceded to bowler
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 1, "extras_type": "bye", "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
        # Leg-bye: 2 extra runs, 0 off bat -> 1 legal ball, 0 runs conceded to bowler
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 2, "extras_type": "legbye", "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
    ]
    df = pd.DataFrame(data)
    annotated = annotate_bowling_deliveries(df)

    assert annotated["is_legal_calc"].tolist() == [1, 0, 0, 1, 1]
    # Runs: [4, 1, 3, 0, 0]
    assert annotated["bowler_runs_calc"].tolist() == [4, 1, 3, 0, 0]

    metrics = compute_bowling_pressure_metrics(df, group_col="bowler_id")
    b1 = metrics[metrics["bowler_id"] == "B1"].iloc[0]

    assert b1["legal_balls_bowled"] == 3
    assert b1["total_balls_bowled"] == 5
    assert b1["runs_conceded"] == 8
    # Economy rate = (8 / 3) * 6 = 16.0
    assert pytest.approx(b1["economy_rate"], 0.01) == 16.0


def test_bowling_metrics_wicket_attribution():
    """Verify that only bowler-credited dismissals count (Bowled, Caught, LBW, Stumped, Hit Wicket).
    Run outs and retired outs must be excluded.
    """
    data = [
        # Bowled -> credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Bowled"},
        # Caught -> credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Caught"},
        # LBW -> credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "LBW"},
        # Stumped -> credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Stumped"},
        # Hit Wicket -> credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Hit Wicket"},
        # Run Out -> NOT credited
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Run Out"},
    ]
    df = pd.DataFrame(data)
    annotated = annotate_bowling_deliveries(df)

    assert annotated["is_bowler_wicket_calc"].tolist() == [1, 1, 1, 1, 1, 0]

    metrics = compute_bowling_pressure_metrics(df, group_col="bowler_id")
    b1 = metrics[metrics["bowler_id"] == "B1"].iloc[0]

    assert b1["wickets_credited"] == 5
    assert b1["total_wickets_in_over"] == 6


def test_bowling_metrics_dot_balls_and_boundaries():
    """Verify dot ball and boundary percentages."""
    data = [
        # Dot ball: legal ball, 0 runs
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
        # Four
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": True, "is_six": False, "is_wicket": False, "wicket_type": None},
        # Six
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 6, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": True, "is_wicket": False, "wicket_type": None},
        # Single
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None},
    ]
    df = pd.DataFrame(data)
    metrics = compute_bowling_pressure_metrics(df, group_col="bowler_id")
    b1 = metrics[metrics["bowler_id"] == "B1"].iloc[0]

    assert b1["dot_balls"] == 1
    assert b1["dot_ball_percentage"] == 25.0
    assert b1["fours_conceded"] == 1
    assert b1["sixes_conceded"] == 1
    # 10 boundary runs out of 11 total runs conceded = 90.91%
    assert pytest.approx(b1["boundary_percentage_conceded"], 0.01) == 90.91
