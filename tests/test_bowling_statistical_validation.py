"""Unit tests for bowling statistical validation module."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.statistical_validation import validate_bowling_pressure_datasets


def test_validate_bowling_pressure_datasets_passes():
    """Verify that valid bowling datasets pass all statistical checks."""
    category_df = pd.DataFrame([
        {"player_id": "B1", "pressure_category": "high", "runs_conceded": 24, "legal_balls_bowled": 18, "wickets_credited": 1}
    ])

    hp_df = pd.DataFrame([
        {"player_id": "B1", "legal_balls_bowled": 18, "runs_conceded": 24, "economy_rate": 8.0, "wickets_credited": 1, "bowling_average": 24.0}
    ])

    comp_df = hp_df.copy()

    bppi_df = pd.DataFrame([
        {
            "player_id": "B1",
            "bppi_b": 65.0,
            "score_economy_retention": 60.0,
            "score_wicket_taking": 70.0,
            "score_dot_ball_generation": 65.0,
            "score_boundary_prevention": 60.0,
            "score_average_retention": 70.0,
            "bowler_classification": "Strong Under Pressure",
        }
    ])

    sit_df = pd.DataFrame([
        {"player_id": "B1", "runs_conceded": 10, "legal_balls_bowled": 6}
    ])

    checks = validate_bowling_pressure_datasets(category_df, hp_df, comp_df, bppi_df, sit_df)

    assert all(checks.values())
    assert checks["runs_non_negative"]
    assert checks["economy_formula_consistent"]
    assert checks["bowling_average_formula_consistent"]
    assert checks["bppi_b_within_bounds"]
    assert checks["classifications_valid"]

