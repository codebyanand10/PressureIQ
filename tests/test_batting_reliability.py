"""Unit tests for batting reliability assessment and block bootstrap resampling."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.batting_pressure.batting_reliability import assess_batting_reliability


def test_batting_reliability_tiers():
    """Verify tier assignment based on sample balls faced and match counts."""
    bppi_data = [
        {"player_id": "P_HIGH", "balls_faced": 120, "matches_count": 8, "innings_count": 6, "dismissals": 4, "overall_baseline_reliability_level": "High", "bppi": 75.0, "strike_rate": 150.0},
        {"player_id": "P_MED", "balls_faced": 45, "matches_count": 4, "innings_count": 3, "dismissals": 2, "overall_baseline_reliability_level": "Medium", "bppi": 65.0, "strike_rate": 140.0},
        {"player_id": "P_LOW", "balls_faced": 20, "matches_count": 2, "innings_count": 2, "dismissals": 1, "overall_baseline_reliability_level": "Low", "bppi": 55.0, "strike_rate": 130.0},
        {"player_id": "P_INSUFF", "balls_faced": 10, "matches_count": 1, "innings_count": 1, "dismissals": 0, "overall_baseline_reliability_level": "Low", "bppi": 60.0, "strike_rate": 120.0},
    ]
    # Synthetic delivery data for bootstrap
    deliv_rows = []
    for m in range(1, 9):
        for _ in range(15):
            deliv_rows.append({
                "match_id": m, "innings": 1, "striker_id": "P_HIGH", "batter_runs": 2, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": False, "batting_pressure_score": 70.0
            })
    for m in range(1, 5):
        for _ in range(12):
            deliv_rows.append({
                "match_id": m, "innings": 1, "striker_id": "P_MED", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": False, "batting_pressure_score": 70.0
            })
    for m in range(1, 3):
        for _ in range(10):
            deliv_rows.append({
                "match_id": m, "innings": 1, "striker_id": "P_LOW", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": False, "batting_pressure_score": 70.0
            })
    deliv_rows.append({
        "match_id": 1, "innings": 1, "striker_id": "P_INSUFF", "batter_runs": 1, "extras_runs": 0, "extras_type": None, "is_four": False, "is_six": False, "is_wicket": False, "batting_pressure_score": 70.0
    })

    res = assess_batting_reliability(
        bppi_df=pd.DataFrame(bppi_data),
        high_pressure_deliveries_df=pd.DataFrame(deliv_rows),
    )

    high = res[res["player_id"] == "P_HIGH"].iloc[0]
    med = res[res["player_id"] == "P_MED"].iloc[0]
    low = res[res["player_id"] == "P_LOW"].iloc[0]
    insuff = res[res["player_id"] == "P_INSUFF"].iloc[0]

    assert high["reliability_level"] == "High"
    assert high["is_statistically_reliable"] is True or high["is_statistically_reliable"] == 1

    assert med["reliability_level"] == "Medium"
    assert med["is_statistically_reliable"] is True or med["is_statistically_reliable"] == 1

    assert low["reliability_level"] == "Low"
    assert low["is_statistically_reliable"] is False or low["is_statistically_reliable"] == 0

    assert insuff["reliability_level"] == "Insufficient Data"
    assert insuff["is_statistically_reliable"] is False or insuff["is_statistically_reliable"] == 0

