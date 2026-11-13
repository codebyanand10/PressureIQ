"""Unit tests for baseline statistical shrinkage module.

Tests Empirical Bayes formula, large vs small sample shrinkage strength,
and preservation of original raw metrics.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.baseline_shrinkage import (
    apply_empirical_bayes_shrinkage,
    apply_baseline_shrinkage,
)
from src.baselines.baseline_config import BaselineConfig


def test_empirical_bayes_shrinkage_behavior():
    """Verify small samples shrink towards reference while large samples remain near raw."""
    raw_vals = pd.Series([250.0, 150.0]) # Player 1 had freak 250 SR in 5 balls, Player 2 had 150 SR in 500 balls
    samples = pd.Series([5, 500])
    k = 60.0
    ref = 125.0

    shrunk, strength = apply_empirical_bayes_shrinkage(raw_vals, samples, k_constant=k, reference_val=ref)

    # Player 1: w = 5 / (5 + 60) = 5/65 = 0.0769 -> Heavy shrinkage towards 125
    assert strength.iloc[0] > 0.90
    assert shrunk.iloc[0] < 140.0  # Far away from 250

    # Player 2: w = 500 / (500 + 60) = 500/560 = 0.8928 -> Minimal shrinkage
    assert strength.iloc[1] < 0.15
    assert 145.0 < shrunk.iloc[1] < 155.0


def test_apply_baseline_shrinkage_dataframe_preservation():
    """Verify raw metrics are preserved alongside shrunk columns in baseline DataFrame."""
    batting = pd.DataFrame({
        "player_id": ["P1"],
        "strike_rate": [180.0],
        "batting_average": [45.0],
        "total_balls_faced": [20],
        "dismissals": [2],
    })
    bowling = pd.DataFrame({
        "player_id": ["BW1"],
        "economy_rate": [5.5],
        "bowling_average": [12.0],
        "legal_balls_bowled": [30],
        "wickets_credited": [3],
    })

    b_out, bw_out, report = apply_baseline_shrinkage(batting, bowling)

    assert "strike_rate" in b_out.columns
    assert "shrunk_strike_rate" in b_out.columns
    assert "economy_rate" in bw_out.columns
    assert "shrunk_economy_rate" in bw_out.columns
    assert len(report) == 4  # 2 batting metrics + 2 bowling metrics

