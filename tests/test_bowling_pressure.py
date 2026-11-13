"""Unit tests for the bowling pressure module.

Tests defense risk, time margins, run containment, and decoupling from batting pressure.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.pressure.bowling_pressure import calculate_bowling_pressure, derive_bowling_reason


def test_bowling_pressure_decoupled_from_batting_pressure():
    """Verify that high RRR produces LOW bowling pressure (bowler has room for error)."""
    # 60 needed off 12 balls (RRR 30.0) -> Batting pressure is extreme, bowling pressure is low
    data = {
        "delivery_sequence": [1],
        "is_chasing_innings": [True],
        "runs_required_before": [60.0],
        "legal_balls_remaining_before": [12.0],
        "required_run_rate_before": [30.0],
        "current_run_rate_before": [6.5],
        "wickets_before": [6],
        "available_legal_balls": [120.0],
        "knock_out": [0],
        "stage": ["League"],
    }
    df = pd.DataFrame(data)
    res = calculate_bowling_pressure(df)
    bowl_score = res.loc[0, "bowling_pressure_score"]

    # Bowler has comfortable defense cushion
    assert bowl_score < 35.0
    assert "cushion" in res.loc[0, "bowling_pressure_reason"].lower()


def test_tight_finish_high_bowling_pressure():
    """Verify that defending a tight target in the final over creates high bowling pressure."""
    # 8 needed off 6 balls with 6 wickets in hand for batting side
    data = {
        "delivery_sequence": [1],
        "is_chasing_innings": [True],
        "runs_required_before": [8.0],
        "legal_balls_remaining_before": [6.0],
        "required_run_rate_before": [8.0],
        "current_run_rate_before": [8.5],
        "wickets_before": [4],
        "available_legal_balls": [120.0],
        "knock_out": [1],
        "stage": ["Final"],
    }
    df = pd.DataFrame(data)
    res = calculate_bowling_pressure(df)
    assert res.loc[0, "bowling_pressure_score"] >= 65.0


def test_first_innings_bowling_containment():
    """Verify bowling pressure in 1st innings when batters are scoring heavily."""
    data = {
        "delivery_sequence": [1],
        "is_chasing_innings": [False],
        "current_run_rate_before": [12.5],  # Heavy batting assault
        "wickets_before": [1],              # 9 wickets in hand
        "innings_phase_before": ["death"],
        "competition_type": ["IPL"],
        "knock_out": [0],
        "stage": ["League"],
    }
    df = pd.DataFrame(data)
    res = calculate_bowling_pressure(df)
    assert res.loc[0, "bowling_pressure_score"] >= 65.0

