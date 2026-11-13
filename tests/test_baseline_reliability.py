"""Unit tests for baseline reliability assessment.

Tests volume thresholds, dismissal/wicket confidence tiers, and reliability flag assignment.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.baseline_reliability import (
    assess_batting_reliability,
    assess_bowling_reliability,
    assess_baseline_reliability,
)
from src.baselines.baseline_config import BaselineConfig


def test_assess_batting_reliability_tiers():
    """Verify batting reliability classification according to configured standards."""
    cfg = BaselineConfig()
    df = pd.DataFrame({
        "total_balls_faced": [200, 100, 40, 10],
        "dismissals": [8, 4, 1, 0],
        "matches_batted": [15, 6, 2, 1],
    })

    scores, levels, flags = assess_batting_reliability(df, cfg)

    assert levels.tolist() == ["High", "Medium", "Low", "Insufficient Data"]
    assert "SMALL_SAMPLE" in flags.iloc[3]
    assert "ZERO_DISMISSALS" in flags.iloc[3]
    assert "SINGLE_MATCH_SAMPLE" in flags.iloc[3]
    assert flags.iloc[0] == "NORMAL"


def test_assess_bowling_reliability_tiers():
    """Verify bowling reliability classification according to configured standards."""
    cfg = BaselineConfig()
    df = pd.DataFrame({
        "legal_balls_bowled": [150, 60, 24, 6],
        "wickets_credited": [10, 2, 1, 0],
        "matches_bowled": [8, 3, 2, 1],
    })

    scores, levels, flags = assess_bowling_reliability(df, cfg)

    assert levels.tolist() == ["High", "Medium", "Low", "Insufficient Data"]
    assert "ZERO_WICKETS" in flags.iloc[3]

