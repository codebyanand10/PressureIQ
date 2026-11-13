"""Unit tests for bowling metrics computation.

Tests bowler run concessions, bye/leg-bye omission, non-bowler dismissal exclusion,
and zero-wicket economy/average edge cases.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.baselines.bowling_metrics import compute_bowling_metrics


def test_bowling_metrics_byes_and_legbyes_omitted():
    """Verify byes and leg-byes are excluded from bowler conceded runs."""
    # 4 deliveries by BW1:
    # Ball 1: 0 batter runs, 4 byes -> Bowler conceded = 0, legal ball = 1
    # Ball 2: 1 batter run, 0 extras -> Bowler conceded = 1, legal ball = 1
    # Ball 3: 0 batter runs, 1 wide -> Bowler conceded = 1, legal ball = 0
    # Ball 4: 0 batter runs, 2 leg-byes -> Bowler conceded = 0, legal ball = 1
    df = pd.DataFrame({
        "delivery_sequence": [1, 2, 3, 4],
        "match_id": [101, 101, 101, 101],
        "innings": [1, 1, 1, 1],
        "bowler_id": ["BW1", "BW1", "BW1", "BW1"],
        "batter_runs": [0, 1, 0, 0],
        "extras_runs": [4, 0, 1, 2],
        "extras_type": ["bye", None, "wide", "legbye"],
        "delivery_runs": [4, 1, 1, 2],
        "is_legal_delivery": [True, True, False, True],
        "is_wicket": [False, False, False, False],
        "dismissal_type": [None, None, None, None],
        "is_four": [False, False, False, False],
        "is_six": [False, False, False, False],
    })

    res = compute_bowling_metrics(df)
    row = res.iloc[0]

    assert row["total_deliveries"] == 4
    assert row["legal_balls_bowled"] == 3
    # Conceded: 0 (bye) + 1 (off bat) + 1 (wide) + 0 (legbye) = 2 runs
    assert row["runs_conceded"] == 2
    # Economy = (2 * 6) / 3 = 4.0
    assert row["economy_rate"] == 4.0


def test_bowling_metrics_runout_not_credited():
    """Verify run-outs are not credited as bowler wickets."""
    df = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 101],
        "innings": [1, 1],
        "bowler_id": ["BW1", "BW1"],
        "batter_runs": [0, 0],
        "extras_runs": [0, 0],
        "extras_type": [None, None],
        "delivery_runs": [0, 0],
        "is_legal_delivery": [True, True],
        "is_wicket": [True, True],
        # Ball 1: Run Out (not bowler wicket)
        # Ball 2: Bowled (bowler wicket)
        "dismissal_type": ["Run Out", "Bowled"],
        "is_four": [False, False],
        "is_six": [False, False],
    })

    res = compute_bowling_metrics(df)
    row = res.iloc[0]

    assert row["wickets_credited"] == 1
    assert row["bowling_average"] == 0.0
    assert row["bowling_strike_rate"] == 2.0  # 2 legal balls / 1 wicket


def test_bowling_metrics_zero_wickets_nan_average():
    """Verify zero wickets results in NaN average and NaN strike rate."""
    df = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 101],
        "innings": [1, 1],
        "bowler_id": ["BW1", "BW1"],
        "batter_runs": [4, 6],
        "extras_runs": [0, 0],
        "extras_type": [None, None],
        "delivery_runs": [4, 6],
        "is_legal_delivery": [True, True],
        "is_wicket": [False, False],
        "dismissal_type": [None, None],
        "is_four": [True, False],
        "is_six": [False, True],
    })

    res = compute_bowling_metrics(df)
    row = res.iloc[0]

    assert row["wickets_credited"] == 0
    assert np.isnan(row["bowling_average"])
    assert np.isnan(row["bowling_strike_rate"])
    assert row["runs_conceded"] == 10
    assert row["economy_rate"] == 30.0

