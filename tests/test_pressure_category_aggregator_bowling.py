"""Unit tests for bowling pressure category aggregator."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.pressure_category_aggregator import (
    assign_bowling_pressure_category,
    aggregate_by_bowling_pressure_category,
)


def test_assign_bowling_pressure_category():
    """Verify categorical assignment across boundaries."""
    cfg = BowlingPressureConfig()
    scores = pd.Series([10.0, 19.99, 20.0, 39.99, 40.0, 59.99, 60.0, 79.99, 80.0, 95.5])
    categories = assign_bowling_pressure_category(scores, cfg)

    expected = [
        "very_low",
        "very_low",
        "low",
        "low",
        "moderate",
        "moderate",
        "high",
        "high",
        "extreme",
        "extreme",
    ]
    assert categories.tolist() == expected


def test_aggregate_by_bowling_pressure_category():
    """Verify aggregation across categories and high pressure cohort creation."""
    cfg = BowlingPressureConfig()

    deliveries = pd.DataFrame([
        # Low pressure ball
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": False, "wicket_type": None, "bowling_pressure_score": 25.0},
        # High pressure ball
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": True, "is_six": False, "is_wicket": False, "wicket_type": None, "bowling_pressure_score": 65.0},
        # Extreme pressure ball
        {"match_id": 1, "innings": 1, "bowler_id": "B1", "batter_runs": 0, "extras_runs": 0, "extras_type": None, "is_legal_delivery": True, "is_four": False, "is_six": False, "is_wicket": True, "wicket_type": "Bowled", "bowling_pressure_score": 85.0},
    ])

    registry = pd.DataFrame([
        {"player_id": "B1", "player_name": "Test Bowler", "bowling_type": "Right-arm fast"}
    ])

    cat_df, hp_df = aggregate_by_bowling_pressure_category(deliveries, registry, cfg)

    assert len(cat_df) > 0
    assert "pressure_category" in cat_df.columns
    assert "player_name" in cat_df.columns

    # High pressure cohort should have deliveries >= 60.0 (high + extreme)
    assert len(hp_df) == 1
    b1_hp = hp_df[hp_df["player_id"] == "B1"].iloc[0]
    assert b1_hp["legal_balls_bowled"] == 2
    assert b1_hp["runs_conceded"] == 4
    assert b1_hp["wickets_credited"] == 1

