"""Unit tests for explanation generator module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.explanation_generator import generate_batter_explanations


def test_generate_batter_explanations():
    """Verify narrative explanations and dominant factor generation."""
    data = [
        {
            "player_id": "P1",
            "player_name": "Rinku Singh",
            "batter_classification": "Elite Under Pressure",
            "bppi": 82.5,
            "balls_faced": 150,
            "total_runs": 280,
            "strike_rate": 186.7,
            "strike_rate_retention": 140.0,
            "boundary_percentage_difference": 12.0,
            "dot_ball_difference": -10.0,
            "dismissal_risk_difference": -0.03,
            "reliability_level": "High",
            "matches_count": 15,
        },
        {
            "player_id": "P2",
            "player_name": "Unknown Tailender",
            "batter_classification": "Insufficient Evidence",
            "bppi": 50.0,
            "balls_faced": 4,
            "total_runs": 2,
            "strike_rate": 50.0,
            "strike_rate_retention": 50.0,
            "boundary_percentage_difference": 0.0,
            "dot_ball_difference": 0.0,
            "dismissal_risk_difference": 0.0,
            "reliability_level": "Insufficient Data",
            "matches_count": 1,
        },
    ]

    exp_df = generate_batter_explanations(pd.DataFrame(data))
    assert len(exp_df) == 2

    p1 = exp_df.loc[exp_df["player_id"] == "P1"].iloc[0]
    assert "Elite" in p1["batter_classification"]
    assert "Rinku Singh" in p1["pressure_performance_summary"]
    assert len(p1["strengths_under_pressure"]) > 5
    assert len(p1["dominant_performance_factor"]) > 3

    p2 = exp_df.loc[exp_df["player_id"] == "P2"].iloc[0]
    assert p2["batter_classification"] == "Insufficient Evidence"
    assert "insufficient" in p2["pressure_performance_summary"].lower()

