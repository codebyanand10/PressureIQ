"""Unit tests for pressure category aggregation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.batting_pressure_config import BattingPressureConfig
from src.batting_pressure.pressure_category_aggregator import (
    assign_pressure_category,
    aggregate_by_pressure_category,
)


def test_pressure_category_boundaries():
    """Verify categorical assignment across exact boundary thresholds."""
    cfg = BattingPressureConfig()
    scores = pd.Series([0.0, 19.99, 20.0, 39.99, 40.0, 59.99, 60.0, 79.99, 80.0, 100.0])
    cats = assign_pressure_category(scores, cfg).tolist()

    expected = [
        "very_low", "very_low",
        "low", "low",
        "moderate", "moderate",
        "high", "high",
        "extreme", "extreme",
    ]
    assert cats == expected


def test_aggregate_by_pressure_category_end_to_end():
    """Verify category metrics and high pressure dataset segregation."""
    deliv_data = [
        # Very low pressure ball
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": False, "batting_pressure_score": 10.0},
        # High pressure ball
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 6, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": True, "is_wicket": False, "batting_pressure_score": 70.0},
        # Extreme pressure ball
        {"match_id": 1, "innings": 1, "striker_id": "P1", "batter_runs": 4, "extras_runs": 0, "extras_type": None, "is_four": True, "is_six": False, "is_wicket": False, "batting_pressure_score": 90.0},
    ]
    reg_data = [{"player_id": "P1", "player_name": "Test Batter"}]

    cat_df, hp_df = aggregate_by_pressure_category(
        deliveries_df=pd.DataFrame(deliv_data),
        player_registry_df=pd.DataFrame(reg_data),
    )

    assert len(cat_df) == 3  # very_low, high, extreme
    assert len(hp_df) == 1
    p1_hp = hp_df.iloc[0]
    assert p1_hp["balls_faced"] == 2
    assert p1_hp["total_runs"] == 10
    assert p1_hp["high_pressure_balls"] == 1
    assert p1_hp["extreme_pressure_balls"] == 1

