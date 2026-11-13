"""Unit tests for bowler role analyzer."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowler_role_analyzer import analyze_bowler_roles


def test_analyze_bowler_roles_death_specialist():
    """Verify that a bowler with majority death overs is classified as Death-Overs Specialist."""
    cfg = BowlingPressureConfig()

    deliveries = pd.DataFrame([
        {
            "match_id": 1,
            "innings": 1,
            "bowler_id": "B_DEATH",
            "overid": 18,
            "batter_runs": 1,
            "extras_runs": 0,
            "extras_type": None,
            "is_legal_delivery": True,
            "is_four": False,
            "is_six": False,
            "is_wicket": False,
            "wicket_type": None,
            "bowling_pressure_score": 75.0,
            "pace_or_spin": "pace",
        }
    ] * 60)  # 60 death deliveries (>= min_balls_for_role)

    registry = pd.DataFrame([
        {"player_id": "B_DEATH", "player_name": "Death Specialist", "bowling_type": "Right-arm fast"}
    ])

    role_df = analyze_bowler_roles(deliveries, registry, cfg)
    row = role_df[role_df["player_id"] == "B_DEATH"].iloc[0]

    assert row["bowling_role"] == "Death-Overs Specialist"
    assert row["death_pct"] == 100.0
    assert row["primary_bowling_style"] == "Pace"


def test_analyze_bowler_roles_part_timer():
    """Verify that a bowler with few balls is classified as Unclassified / Part-Timer."""
    cfg = BowlingPressureConfig()

    deliveries = pd.DataFrame([
        {
            "match_id": 1,
            "innings": 1,
            "bowler_id": "B_PART",
            "overid": 10,
            "batter_runs": 1,
            "extras_runs": 0,
            "extras_type": None,
            "is_legal_delivery": True,
            "is_four": False,
            "is_six": False,
            "is_wicket": False,
            "wicket_type": None,
            "bowling_pressure_score": 50.0,
            "pace_or_spin": "spin",
        }
    ] * 10)  # only 10 balls (< min_balls_for_role of 36)

    registry = pd.DataFrame([
        {"player_id": "B_PART", "player_name": "Part Timer", "bowling_type": "Off spin"}
    ])

    role_df = analyze_bowler_roles(deliveries, registry, cfg)
    row = role_df[role_df["player_id"] == "B_PART"].iloc[0]

    assert row["bowling_role"] == "Unclassified / Part-Timer"

