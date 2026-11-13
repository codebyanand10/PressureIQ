"""Unit tests for Phase 9 tactical role fairness validation."""

import pandas as pd
import pytest

from src.validation.role_fairness import evaluate_role_fairness
from src.validation.validation_config import ValidationConfig


def test_evaluate_role_fairness():
    """Verify role and situation fairness analysis across batting and bowling cohorts."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": ["p1", "p2", "p3"],
        "rank": [1, 2, 3],
        "final_fbpr": [75.0, 70.0, 65.0],
        "balls_faced": [150, 120, 100],
        "strike_rate": [170.0, 160.0, 150.0],
    })
    r_bowl = pd.DataFrame({
        "player_id": ["b1", "b2", "b3"],
        "rank": [1, 2, 3],
        "final_fbor": [50.0, 48.0, 46.0],
        "legal_balls_bowled": [180, 150, 120],
        "economy_rate": [7.5, 8.0, 8.5],
        "bowling_role": ["Death Specialist", "Powerplay Bowler", "Middle Phase"],
        "primary_bowling_style": ["Right-arm fast", "Slow left-arm orthodox", "Right-arm legbreak"],
    })

    bat_summary, bowl_summary, metrics = evaluate_role_fairness(r_bat, r_bowl, cfg)

    assert "batting_role" in bat_summary.columns
    assert "bowling_role" in bowl_summary.columns
    assert "pace_bowlers_in_top10" in metrics
    assert "spin_bowlers_in_top10" in metrics

