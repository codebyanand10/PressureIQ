"""Unit tests for batting metrics computation.

Tests runs off the bat, wide ball exclusion, no-ball inclusion,
zero-dismissal average handling, boundary percentage, and dot balls.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.baselines.batting_metrics import compute_batting_metrics


def test_batting_metrics_wides_and_noballs():
    """Verify that wides do not count as balls faced, but no-balls do."""
    # 3 deliveries to batter B1:
    # Ball 1: wide (1 extra, 0 batter runs) -> Not a ball faced
    # Ball 2: no-ball (Overstep) with 2 runs off the bat -> 1 ball faced, 2 runs
    # Ball 3: legal ball with 4 runs (four) -> 1 ball faced, 4 runs
    df = pd.DataFrame({
        "delivery_sequence": [1, 2, 3],
        "match_id": [101, 101, 101],
        "innings": [1, 1, 1],
        "striker_id": ["B1", "B1", "B1"],
        "batter_runs": [0, 2, 4],
        "extras_runs": [1, 1, 0],
        "extras_type": ["wide", "Overstep", None],
        "is_four": [False, False, True],
        "is_six": [False, False, False],
        "is_wicket": [False, False, False],
        "dismissed_player_id": [None, None, None],
    })

    res = compute_batting_metrics(df)
    row = res.iloc[0]

    assert row["total_deliveries"] == 3
    assert row["total_balls_faced"] == 2  # Wide excluded!
    assert row["total_runs"] == 6         # 2 + 4
    assert row["fours"] == 1
    assert row["sixes"] == 0
    assert row["strike_rate"] == 300.0   # (6 / 2) * 100


def test_batting_metrics_zero_dismissals():
    """Verify batter with zero dismissals has NaN average and not-out == innings."""
    df = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 102],
        "innings": [1, 2],
        "striker_id": ["B1", "B1"],
        "batter_runs": [10, 25],
        "extras_runs": [0, 0],
        "extras_type": [None, None],
        "is_four": [1, 1],
        "is_six": [0, 1],
        "is_wicket": [False, False],
        "dismissed_player_id": [None, None],
    })

    res = compute_batting_metrics(df)
    row = res.iloc[0]

    assert row["innings_batted"] == 2
    assert row["dismissals"] == 0
    assert row["not_outs"] == 2
    assert np.isnan(row["batting_average"])
    assert row["total_runs"] == 35


def test_batting_metrics_dismissal_attribution():
    """Verify dismissals only count when dismissed_player_id matches striker_id."""
    df = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 101],
        "innings": [1, 1],
        "striker_id": ["B1", "B1"],
        "batter_runs": [1, 0],
        "extras_runs": [0, 0],
        "extras_type": [None, None],
        "is_four": [False, False],
        "is_six": [False, False],
        "is_wicket": [True, True],
        # First wicket: non-striker run out (B2 dismissed, not B1)
        # Second wicket: B1 caught
        "dismissed_player_id": ["B2", "B1"],
    })

    res = compute_batting_metrics(df)
    row = res.iloc[0]

    assert row["dismissals"] == 1  # Only B1's dismissal counts
    assert row["batting_average"] == 1.0

