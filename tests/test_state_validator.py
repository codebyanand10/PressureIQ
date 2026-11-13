"""Unit tests for match state constraint validation (Phase 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.match_state.state_validator import validate_match_states


@pytest.fixture
def valid_state_df() -> pd.DataFrame:
    return pd.DataFrame({
        "match_id": [1, 1],
        "innings": [1, 1],
        "batting_team_id": [10, 10],
        "bowling_team_id": [20, 20],
        "runs_before": [0, 4],
        "runs_after": [4, 5],
        "wickets_before": [0, 0],
        "wickets_after": [0, 1],
        "legal_balls_bowled_before": [0, 1],
        "legal_balls_bowled_after": [1, 2],
        "legal_balls_remaining_before": [120, 119],
        "legal_balls_remaining_after": [119, 118],
        "available_legal_balls": [120, 120],
        "target_score": [np.nan, np.nan],
        "is_chasing_innings": [False, False],
        "is_super_over": [False, False],
        "current_run_rate_before": [np.nan, 24.0],
        "current_run_rate_after": [24.0, 15.0],
        "required_run_rate_before": [np.nan, np.nan],
        "required_run_rate_after": [np.nan, np.nan],
    })


def test_validate_match_states_pass(valid_state_df: pd.DataFrame):
    df_val, report, summary = validate_match_states(valid_state_df)
    assert summary["invalid_deliveries_count"] == 0
    assert summary["validity_pct"] == 100.0
    assert df_val["match_state_valid"].all()


def test_validate_negative_runs_flagged(valid_state_df: pd.DataFrame):
    invalid_df = valid_state_df.copy()
    invalid_df.loc[0, "runs_before"] = -5
    df_val, report, summary = validate_match_states(invalid_df)
    assert summary["invalid_deliveries_count"] == 1
    assert "NEGATIVE_RUNS" in df_val.loc[0, "validation_flags"]


def test_validate_non_monotonic_runs_flagged(valid_state_df: pd.DataFrame):
    invalid_df = valid_state_df.copy()
    # Runs after is less than runs before
    invalid_df.loc[0, "runs_after"] = -1
    invalid_df.loc[0, "runs_before"] = 10
    df_val, report, summary = validate_match_states(invalid_df)
    assert summary["invalid_deliveries_count"] > 0
    assert "RUNS_DECREASED" in df_val.loc[0, "validation_flags"]

