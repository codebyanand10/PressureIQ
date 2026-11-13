"""Unit tests for Batting Pressure Performance Index (BPPI) calculation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.bppi_calculator import calculate_bppi


def test_bppi_bounds_and_components():
    """Verify that BPPI and all components remain strictly bounded in [0, 100]."""
    test_rows = [
        # Clutch performer: +50% SR retention, +20% boundary diff, -15% dot diff
        {
            "player_id": "P_CLUTCH",
            "strike_rate_retention": 150.0,
            "overall_shrunk_batting_average": 25.0,
            "batting_average": 40.0,
            "dismissals": 2,
            "total_runs": 80,
            "boundary_percentage_difference": 20.0,
            "dot_ball_difference": -15.0,
            "dismissal_risk_difference": -0.02,
        },
        # Parity performer: 100% retention, 0 diffs
        {
            "player_id": "P_PARITY",
            "strike_rate_retention": 100.0,
            "overall_shrunk_batting_average": 25.0,
            "batting_average": 25.0,
            "dismissals": 2,
            "total_runs": 50,
            "boundary_percentage_difference": 0.0,
            "dot_ball_difference": 0.0,
            "dismissal_risk_difference": 0.0,
        },
        # Struggling performer: 60% SR retention, -20% boundary diff, +20% dot diff
        {
            "player_id": "P_STRUGGLE",
            "strike_rate_retention": 60.0,
            "overall_shrunk_batting_average": 25.0,
            "batting_average": 10.0,
            "dismissals": 4,
            "total_runs": 40,
            "boundary_percentage_difference": -20.0,
            "dot_ball_difference": 20.0,
            "dismissal_risk_difference": 0.04,
        },
    ]

    res = calculate_bppi(pd.DataFrame(test_rows))

    clutch = res[res["player_id"] == "P_CLUTCH"].iloc[0]
    parity = res[res["player_id"] == "P_PARITY"].iloc[0]
    struggle = res[res["player_id"] == "P_STRUGGLE"].iloc[0]

    # Verify monotonic ranking: Clutch > Parity > Struggle
    assert clutch["bppi"] > parity["bppi"] > struggle["bppi"]
    assert clutch["bppi"] >= 70.0
    assert 48.0 <= parity["bppi"] <= 52.0
    assert struggle["bppi"] <= 35.0

    # Verify component bounds
    for col in ["score_sr_retention", "score_average_retention", "score_boundary_efficiency", "score_dot_ball_control", "score_dismissal_management"]:
        assert 0.0 <= clutch[col] <= 100.0
        assert 0.0 <= parity[col] <= 100.0
        assert 0.0 <= struggle[col] <= 100.0

