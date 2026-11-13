"""Unit tests for batter classification logic."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.batter_classifier import classify_batters


def test_classify_batters_tiers():
    """Verify evidence-based batter classification rules."""
    data = [
        # 1. Elite: BPPI >= 75.0, Medium/High rel, >= 40 balls
        {"player_id": "P_ELITE", "bppi": 78.5, "reliability_level": "High", "balls_faced": 120},
        # 2. High BPPI but small sample (< 40 balls) cannot be Elite
        {"player_id": "P_SMALL_ELITE", "bppi": 85.0, "reliability_level": "Low", "balls_faced": 25},
        # 3. Strong: BPPI 60.0-74.9, Medium/High rel, >= 40 balls
        {"player_id": "P_STRONG", "bppi": 68.0, "reliability_level": "Medium", "balls_faced": 50},
        # 4. Average: BPPI 45.0-59.9
        {"player_id": "P_AVG", "bppi": 52.0, "reliability_level": "Low", "balls_faced": 20},
        # 5. Below Baseline: BPPI < 45.0
        {"player_id": "P_BELOW", "bppi": 38.0, "reliability_level": "Low", "balls_faced": 20},
        # 6. Insufficient Data (< 15 balls)
        {"player_id": "P_INSUFF", "bppi": 90.0, "reliability_level": "Insufficient Data", "balls_faced": 8},
    ]

    classified = classify_batters(pd.DataFrame(data))

    assert classified.loc[classified["player_id"] == "P_ELITE", "batter_classification"].iloc[0] == "Elite Under Pressure"
    assert classified.loc[classified["player_id"] == "P_SMALL_ELITE", "batter_classification"].iloc[0] != "Elite Under Pressure"
    assert classified.loc[classified["player_id"] == "P_STRONG", "batter_classification"].iloc[0] == "Strong Under Pressure"
    assert classified.loc[classified["player_id"] == "P_AVG", "batter_classification"].iloc[0] == "Average Under Pressure"
    assert classified.loc[classified["player_id"] == "P_BELOW", "batter_classification"].iloc[0] == "Below Baseline Under Pressure"
    assert classified.loc[classified["player_id"] == "P_INSUFF", "batter_classification"].iloc[0] == "Insufficient Evidence"

