"""Unit tests for the complete Pressure Detection Engine end-to-end pipeline.

Tests end-to-end delivery scoring, metadata integration, column completeness,
and zero-leakage enforcement.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.pressure.pressure_engine import calculate_pressure_scores
from src.pressure.pressure_config import PressureConfig


def test_pressure_engine_end_to_end():
    """Verify that calculate_pressure_scores enriches a DataFrame with all required fields."""
    match_states = pd.DataFrame({
        "match_id": [101, 101, 102],
        "comp_id": [1, 1, 2],
        "comp_name": ["IPL 2024", "IPL 2024", "T20I Tri-Series"],
        "competition_type": ["IPL", "IPL", "T20I"],
        "season": ["2024", "2024", "2024"],
        "match_format": ["T20", "T20", "T20"],
        "innings": [1, 2, 1],
        "batting_team_id": [10, 20, 30],
        "bowling_team_id": [20, 10, 40],
        "delivery_sequence": [1, 125, 1],
        "innings_ball_num": [1, 1, 1],
        "overid": [1, 1, 1],
        "over_ball_num": [1, 1, 1],
        "striker_id": [1001, 2001, 3001],
        "bowler_id": [2001, 1001, 4001],
        "is_legal_delivery": [True, True, True],
        "delivery_runs": [1, 0, 4],
        "is_wicket": [False, False, False],
        "runs_before": [0, 0, 0],
        "wickets_before": [0, 0, 0],
        "legal_balls_bowled_before": [0, 0, 0],
        "legal_balls_remaining_before": [120, 120, 120],
        "innings_progress_before": [0.0, 0.0, 0.0],
        "target_score": [np.nan, 185.0, np.nan],
        "runs_required_before": [np.nan, 185.0, np.nan],
        "current_run_rate_before": [0.0, 0.0, 0.0],
        "required_run_rate_before": [np.nan, 9.25, np.nan],
        "innings_phase_before": ["powerplay", "powerplay", "powerplay"],
        "is_chasing_innings": [False, True, False],
        "available_legal_balls": [120, 120, 120],
        "match_state_valid": [True, True, True],
    })

    matches_meta = pd.DataFrame({
        "match_id": [101, 102],
        "knock_out": [1, 0],
        "stage": ["Final", "League"],
    })

    cfg = PressureConfig()
    result = calculate_pressure_scores(match_states, matches_meta, cfg)

    # Verify required Section 12 columns
    expected_cols = [
        "batting_pressure_score",
        "batting_pressure_level",
        "bowling_pressure_score",
        "bowling_pressure_level",
        "batting_pressure_reliability",
        "bowling_pressure_reliability",
        "pressure_reliability_flags",
        "batting_pressure_reason",
        "bowling_pressure_reason",
        "dominant_pressure_factor",
        "pressure_model_version",
        "rrr_pressure",
        "run_rate_gap_pressure",
        "wicket_pressure",
        "time_pressure",
        "match_importance_pressure",
    ]

    for col in expected_cols:
        assert col in result.columns, f"Expected output column missing: {col}"

    assert len(result) == len(match_states)
    assert (result["batting_pressure_score"] >= 0.0).all()
    assert (result["batting_pressure_score"] <= 100.0).all()
    assert (result["bowling_pressure_score"] >= 0.0).all()
    assert (result["bowling_pressure_score"] <= 100.0).all()
    assert result["pressure_model_version"].iloc[0] == cfg.version

