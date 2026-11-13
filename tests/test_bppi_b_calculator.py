"""Unit tests for BPPI-B calculator."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bppi_b_calculator import calculate_bppi_b


def test_calculate_bppi_b_bounds_and_components():
    """Verify that BPPI-B and all 5 components are within [0, 100]."""
    cfg = BowlingPressureConfig()

    df = pd.DataFrame([
        {
            "player_id": "B1",
            "economy_retention": 100.0,
            "wicket_taking_difference": 0.0,
            "dot_ball_difference": 0.0,
            "boundary_prevention_difference": 0.0,
            "overall_bowling_average": 24.0,
            "bowling_average": 24.0,
            "wickets_credited": 5,
        },
        {
            "player_id": "B2",
            "economy_retention": 150.0,
            "wicket_taking_difference": 0.05,
            "dot_ball_difference": 15.0,
            "boundary_prevention_difference": -10.0,
            "overall_bowling_average": 30.0,
            "bowling_average": 20.0,
            "wickets_credited": 10,
        },
    ])

    res = calculate_bppi_b(df, cfg)

    for col in [
        "bppi_b",
        "score_economy_retention",
        "score_wicket_taking",
        "score_dot_ball_generation",
        "score_boundary_prevention",
        "score_average_retention",
    ]:
        assert col in res.columns
        assert (res[col] >= 0.0).all()
        assert (res[col] <= 100.0).all()

    # B1 has neutral deltas -> should be exactly ~50.0 across all components
    b1 = res[res["player_id"] == "B1"].iloc[0]
    assert pytest.approx(b1["score_economy_retention"], 0.1) == 50.0
    assert pytest.approx(b1["score_wicket_taking"], 0.1) == 50.0
    assert pytest.approx(b1["score_dot_ball_generation"], 0.1) == 50.0
    assert pytest.approx(b1["score_boundary_prevention"], 0.1) == 50.0
    assert pytest.approx(b1["score_average_retention"], 0.1) == 50.0
    assert pytest.approx(b1["bppi_b"], 0.1) == 50.0

