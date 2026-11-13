"""Unit tests for Phase 9 eligibility threshold sensitivity analysis."""

import pandas as pd
import pytest

from src.validation.eligibility_sensitivity import evaluate_eligibility_sensitivity
from src.validation.validation_config import ValidationConfig


def test_evaluate_eligibility_sensitivity():
    """Verify that shifting eligibility boundaries recalculates cohorts properly."""
    cfg = ValidationConfig()

    bat_el = pd.DataFrame({
        "player_id": ["p1", "p2", "p3", "p4"],
        "player_name": ["P1", "P2", "P3", "P4"],
        "balls_faced": [25, 45, 65, 80],
        "matches_count": [2, 4, 6, 8],
        "innings_count": [2, 3, 4, 5],
        "has_baseline": [True, True, True, True],
        "is_registered": [True, True, True, True],
    })

    bowl_el = pd.DataFrame({
        "player_id": ["b1", "b2", "b3", "b4"],
        "player_name": ["B1", "B2", "B3", "B4"],
        "legal_balls_bowled": [30, 50, 75, 90],
        "matches_bowled": [2, 4, 6, 8],
        "innings_bowled": [2, 3, 4, 5],
        "has_baseline": [True, True, True, True],
        "is_registered": [True, True, True, True],
    })

    r_bat = pd.DataFrame({
        "player_id": ["p4", "p3", "p2", "p1"],
        "player_name": ["P4", "P3", "P2", "P1"],
        "rank": [1, 2, 3, 4],
        "final_fbpr": [75.0, 70.0, 65.0, 60.0],
    })

    r_bowl = pd.DataFrame({
        "player_id": ["b4", "b3", "b2", "b1"],
        "player_name": ["B4", "B3", "B2", "B1"],
        "rank": [1, 2, 3, 4],
        "final_fbor": [55.0, 50.0, 48.0, 45.0],
    })

    summary, movements = evaluate_eligibility_sensitivity(
        bat_el, bowl_el, r_bat, r_bowl, cfg
    )

    assert len(summary) == 3  # lower, primary, higher
    lower_row = summary[summary["scenario"] == "lower"].iloc[0]
    higher_row = summary[summary["scenario"] == "higher"].iloc[0]

    # Lower threshold should include more or equal eligible players than higher threshold
    assert lower_row["bat_eligible_count"] >= higher_row["bat_eligible_count"]
    assert lower_row["bowl_eligible_count"] >= higher_row["bowl_eligible_count"]

