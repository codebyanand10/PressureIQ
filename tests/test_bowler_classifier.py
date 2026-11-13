"""Unit tests for bowler classifier module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowler_classifier import classify_bowlers


def test_classify_bowlers_tiers():
    """Verify tier assignment based on BPPI-B and sample size."""
    cfg = BowlingPressureConfig()

    df = pd.DataFrame([
        # Elite: BPPI-B >= 75.0, High/Med reliability, >= 48 balls
        {"player_id": "B_ELITE", "bppi_b": 80.0, "reliability_level": "High", "legal_balls_bowled": 150},
        # Strong: BPPI-B 60-74.99, High/Med reliability, >= 48 balls
        {"player_id": "B_STRONG", "bppi_b": 68.0, "reliability_level": "Medium", "legal_balls_bowled": 60},
        # Average: BPPI-B 45-59.99
        {"player_id": "B_AVG", "bppi_b": 52.0, "reliability_level": "Low", "legal_balls_bowled": 30},
        # Below: BPPI-B < 45.0
        {"player_id": "B_BELOW", "bppi_b": 38.0, "reliability_level": "Medium", "legal_balls_bowled": 50},
        # Insufficient: < 18 balls or Insufficient Data tier
        {"player_id": "B_INSUF", "bppi_b": 90.0, "reliability_level": "Insufficient Data", "legal_balls_bowled": 12},
    ])

    res = classify_bowlers(df, cfg)
    tier_map = res.set_index("player_id")["bowler_classification"].to_dict()

    assert tier_map["B_ELITE"] == "Elite Under Pressure"
    assert tier_map["B_STRONG"] == "Strong Under Pressure"
    assert tier_map["B_AVG"] == "Average Under Pressure"
    assert tier_map["B_BELOW"] == "Below Baseline Under Pressure"
    assert tier_map["B_INSUF"] == "Insufficient Evidence"
