"""Unit tests for batting pressure module.

Tests routing between innings types, classification, dominant factor attribution,
and explainability outputs across synthetic DataFrames.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.pressure.batting_pressure import (
    calculate_batting_pressure,
    derive_batting_reason_and_factor,
)


def test_derive_batting_reason_and_factor():
    """Verify human-readable reason strings and dominant factor labels."""
    reason, factor = derive_batting_reason_and_factor(
        is_chase=True,
        score=85.0,
        rrr_p=90.0,
        gap_p=80.0,
        wkt_p=40.0,
        time_p=70.0,
        imp_p=50.0,
        rrr=15.2,
    )
    assert factor == "RRR_URGENCY"
    assert "High RRR" in reason
    assert "15.2" in reason


def test_calculate_batting_pressure_dataframe_vectorized():
    """Verify batch calculation on synthetic DataFrame containing both 1st and 2nd innings."""
    data = {
        "delivery_sequence": [1, 2, 3],
        "is_chasing_innings": [False, True, True],
        "runs_required_before": [np.nan, 30.0, 0.0],
        "legal_balls_remaining_before": [90.0, 18.0, 6.0],
        "required_run_rate_before": [np.nan, 10.0, 0.0],
        "current_run_rate_before": [7.5, 8.0, 9.0],
        "wickets_before": [1, 5, 2],
        "available_legal_balls": [120.0, 120.0, 120.0],
        "innings_phase_before": ["powerplay", "death", "death"],
        "competition_type": ["IPL", "IPL", "IPL"],
        "knock_out": [0, 1, 0],
        "stage": ["League", "Final", "League"],
    }
    df = pd.DataFrame(data)
    res = calculate_batting_pressure(df)

    assert "batting_pressure_score" in res.columns
    assert "batting_pressure_level" in res.columns
    assert "batting_pressure_reason" in res.columns
    assert "dominant_pressure_factor" in res.columns

    # Row 0: 1st inn
    assert 0.0 <= res.loc[0, "batting_pressure_score"] <= 100.0
    # Row 1: High chase in Final
    assert res.loc[1, "batting_pressure_score"] >= 60.0
    # Row 2: Target already reached -> 0
    assert res.loc[2, "batting_pressure_score"] == 0.0
    assert res.loc[2, "dominant_pressure_factor"] == "TARGET_ACHIEVED"

