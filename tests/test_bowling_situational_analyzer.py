"""Unit tests for bowling situational analyzer."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.situational_analyzer import analyze_situational_bowling


def test_analyze_situational_bowling():
    """Verify situational slices for bowling across phase, innings, competition, and stage."""
    cfg = BowlingPressureConfig()

    deliveries = pd.DataFrame([
        {
            "match_id": 1,
            "innings": 2,
            "bowler_id": "B1",
            "batter_runs": 0,
            "extras_runs": 0,
            "extras_type": None,
            "is_legal_delivery": True,
            "is_four": False,
            "is_six": False,
            "is_wicket": True,
            "wicket_type": "Bowled",
            "bowling_pressure_score": 75.0,
            "innings_phase": "Death",
            "competition_name": "IPL",
            "is_knockout": False,
        },
        {
            "match_id": 1,
            "innings": 2,
            "bowler_id": "B1",
            "batter_runs": 4,
            "extras_runs": 0,
            "extras_type": None,
            "is_legal_delivery": True,
            "is_four": True,
            "is_six": False,
            "is_wicket": False,
            "wicket_type": None,
            "bowling_pressure_score": 85.0,
            "innings_phase": "Death",
            "competition_name": "IPL",
            "is_knockout": False,
        },
    ])

    registry = pd.DataFrame([
        {"player_id": "B1", "player_name": "Bowler 1", "bowling_type": "Right-arm fast"}
    ])

    res = analyze_situational_bowling(deliveries, registry, cfg)

    assert len(res) > 0
    assert "context_type" in res.columns
    assert "context_value" in res.columns
    assert "innings_number" in res["context_type"].values
    assert "pressure_intensity" in res["context_type"].values
