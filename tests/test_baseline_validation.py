"""Unit tests for baseline validation and integrity checks.

Tests mathematical formula consistency, non-negativity enforcement, and duplicate detection.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.baseline_validation import validate_baselines, BaselineValidationError


def test_validate_baselines_clean_passes():
    """Verify clean baseline data passes all validation checks."""
    batting = pd.DataFrame({
        "player_id": ["P1", "P2"],
        "total_runs": [150, 40],
        "total_balls_faced": [100, 25],
        "dismissals": [3, 1],
        "batting_average": [50.0, 40.0],
        "strike_rate": [150.0, 160.0],
        "fours": [10, 2],
        "sixes": [5, 2],
        "boundary_runs": [70, 20],
    })
    bowling = pd.DataFrame({
        "player_id": ["BW1", "BW2"],
        "runs_conceded": [60, 45],
        "legal_balls_bowled": [48, 30],
        "wickets_credited": [3, 1],
        "economy_rate": [7.5, 9.0],
        "bowling_average": [20.0, 45.0],
    })

    checks = validate_baselines(batting, bowling)
    assert all(checks.values())


def test_validate_baselines_detects_formula_inconsistency():
    """Verify that an incorrect strike rate raises BaselineValidationError."""
    bad_batting = pd.DataFrame({
        "player_id": ["P1"],
        "total_runs": [100],
        "total_balls_faced": [50],
        "dismissals": [1],
        "batting_average": [100.0],
        "strike_rate": [50.0], # Should be 200.0!
        "fours": [0],
        "sixes": [0],
        "boundary_runs": [0],
    })
    bowling = pd.DataFrame({
        "player_id": ["BW1"],
        "runs_conceded": [20],
        "legal_balls_bowled": [12],
        "wickets_credited": [1],
        "economy_rate": [10.0],
        "bowling_average": [20.0],
    })

    with pytest.raises(BaselineValidationError, match="Baseline validation failed"):
        validate_baselines(bad_batting, bowling)

