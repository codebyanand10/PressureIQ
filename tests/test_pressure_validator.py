"""Unit tests for the pressure validator and leakage auditing module.

Tests leakage detection, reliability scoring, DLS flag propagation,
and boundary integrity validation.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.pressure.pressure_validator import (
    audit_leakage,
    calculate_pressure_reliability,
    validate_pressure_scores,
    PressureValidationError,
)


def test_audit_leakage_clean():
    """Verify zero leakage passes when pressure has no correlation with delivery outcomes."""
    np.random.seed(42)
    n = 5000
    df = pd.DataFrame({
        "batting_pressure_score": np.random.uniform(20, 80, n),
        "bowling_pressure_score": np.random.uniform(20, 80, n),
        "delivery_runs": np.random.choice([0, 1, 2, 4, 6], n),
        "is_wicket": np.random.choice([0, 1], p=[0.95, 0.05], size=n),
    })

    metrics = audit_leakage(df)
    assert "corr_batting_score_delivery_runs" in metrics
    assert abs(metrics["corr_batting_score_delivery_runs"]) < 0.10


def test_audit_leakage_flags_fabricated_leakage():
    """Verify that artificial leakage from delivery outcome raises an exception."""
    # Fabricate 100 heavily leaked delivery rows (r > 0.8)
    runs = np.random.choice([0, 1, 2, 4, 6], 100)
    df = pd.DataFrame({
        "delivery_runs": runs,
        "batting_pressure_score": runs * 15.0 + 10.0, # Directly leaked from delivery runs
    })
    with pytest.raises(PressureValidationError, match="Potential leakage detected"):
        audit_leakage(df)


def test_calculate_pressure_reliability_flags():
    """Verify that DLS revised matches and extreme RRRs receive appropriate reliability flags."""
    df = pd.DataFrame({
        "match_state_valid": [True, False],
        "target_source": ["DLS_REVISED_TARGET", "INNINGS_1_TOTAL_PLUS_ONE"],
        "is_super_over": [False, True],
        "required_run_rate_before": [10.0, 45.0], # 45 > 36
        "runs_required_before": [40.0, 0.0],
    })

    scores, levels, flags = calculate_pressure_reliability(df)
    assert "DLS_REVISED_INNINGS" in flags.iloc[0]
    assert "EXTREME_RRR_CAPPED" in flags.iloc[1]
    assert "SUPER_OVER" in flags.iloc[1]
    assert "CHASE_COMPLETED" in flags.iloc[1]
    assert "UNVALIDATED_MATCH_STATE" in flags.iloc[1]


def test_validate_pressure_scores_bounds():
    """Verify range enforcement [0, 100]."""
    clean_df = pd.DataFrame({
        "batting_pressure_score": [10.0, 50.0, 90.0],
        "bowling_pressure_score": [80.0, 40.0, 20.0],
    })
    res = validate_pressure_scores(clean_df)
    assert res["batting_score_within_0_100"] is True

    bad_df = pd.DataFrame({
        "batting_pressure_score": [-5.0, 50.0],
        "bowling_pressure_score": [40.0, 40.0],
    })
    with pytest.raises(PressureValidationError):
        validate_pressure_scores(bad_df)

