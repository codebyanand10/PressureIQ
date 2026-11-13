"""Unit tests for statistical validation and domain integrity checks."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.statistical_validation import validate_batting_pressure_datasets


def test_validation_passes_clean_data():
    """Verify that consistent data passes all validation checks."""
    cat_df = pd.DataFrame([{"total_runs": 50, "balls_faced": 30, "dismissals": 1}])
    hp_df = pd.DataFrame([{
        "player_id": "P1", "total_runs": 50, "balls_faced": 30, "strike_rate": 166.67,
        "dismissals": 1, "batting_average": 50.0
    }])
    comp_df = pd.DataFrame([{"player_id": "P1"}])
    bppi_df = pd.DataFrame([{
        "player_id": "P1", "bppi": 65.0, "score_sr_retention": 70.0,
        "score_average_retention": 60.0, "score_boundary_efficiency": 65.0,
        "score_dot_ball_control": 60.0, "score_dismissal_management": 55.0,
        "batter_classification": "Strong Under Pressure"
    }])
    sit_df = pd.DataFrame([{"total_runs": 50}])

    results = validate_batting_pressure_datasets(cat_df, hp_df, comp_df, bppi_df, sit_df)
    assert all(results.values())


def test_validation_catches_invalid_bounds():
    """Verify that BPPI > 100 or negative runs are caught."""
    cat_df = pd.DataFrame([{"total_runs": -5, "balls_faced": 10, "dismissals": 0}])
    hp_df = pd.DataFrame([{
        "player_id": "P1", "total_runs": 10, "balls_faced": 10, "strike_rate": 100.0,
        "dismissals": 0, "batting_average": None
    }])
    comp_df = pd.DataFrame([{"player_id": "P1"}])
    bppi_df = pd.DataFrame([{
        "player_id": "P1", "bppi": 125.0,  # Invalid
        "score_sr_retention": 70.0, "score_average_retention": 60.0,
        "score_boundary_efficiency": 65.0, "score_dot_ball_control": 60.0,
        "score_dismissal_management": 55.0, "batter_classification": "Strong Under Pressure"
    }])
    sit_df = pd.DataFrame([{"total_runs": 10}])

    results = validate_batting_pressure_datasets(cat_df, hp_df, comp_df, bppi_df, sit_df)
    assert results["runs_non_negative"] is False
    assert results["bppi_within_bounds"] is False

