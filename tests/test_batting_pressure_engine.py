"""Integration tests for the complete Batting Performance Under Pressure Engine."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.batting_pressure_engine import calculate_batting_pressure_performance


def test_batting_pressure_engine_end_to_end():
    """Verify that end-to-end pipeline produces all expected datasets and passes validations."""
    deliveries = []
    # 3 matches, player P1 faces high pressure balls and low pressure balls
    for m in range(1, 4):
        for b in range(10):
            deliveries.append({
                "match_id": m,
                "innings": 2,
                "striker_id": "P1",
                "striker_name": "Clutch Finisher",
                "batter_runs": 4 if b % 2 == 0 else 1,
                "extras_runs": 0,
                "extras_type": None,
                "is_legal_delivery": True,
                "is_four": b % 2 == 0,
                "is_six": False,
                "is_wicket": False,
                "batting_pressure_score": 75.0,  # High pressure
                "innings_phase_before": "death",
                "competition_type": "IPL",
                "knock_out": True,
                "batting_order": 6,
            })
        # Low pressure balls
        for b in range(5):
            deliveries.append({
                "match_id": m,
                "innings": 1,
                "striker_id": "P1",
                "striker_name": "Clutch Finisher",
                "batter_runs": 1,
                "extras_runs": 0,
                "extras_type": None,
                "is_legal_delivery": True,
                "is_four": False,
                "is_six": False,
                "is_wicket": False,
                "batting_pressure_score": 25.0,  # Low pressure
                "innings_phase_before": "middle",
                "competition_type": "IPL",
                "knock_out": False,
                "batting_order": 6,
            })

    registry = [{"player_id": "P1", "player_name": "Clutch Finisher"}]
    overall_base = [{
        "player_id": "P1",
        "strike_rate": 130.0,
        "batting_average": 30.0,
        "shrunk_strike_rate": 128.0,
        "shrunk_batting_average": 28.0,
        "boundary_percentage": 45.0,
        "dot_ball_percentage": 40.0,
        "dismissal_rate": 0.05,
        "baseline_reliability_level": "Medium",
    }]
    lp_base = [{
        "player_id": "P1",
        "strike_rate": 135.0,
        "batting_average": 32.0,
        "boundary_percentage": 48.0,
        "dot_ball_percentage": 38.0,
        "dismissal_rate": 0.045,
    }]

    results = calculate_batting_pressure_performance(
        deliveries_df=pd.DataFrame(deliveries),
        player_registry_df=pd.DataFrame(registry),
        overall_baseline_df=pd.DataFrame(overall_base),
        low_pressure_baseline_df=pd.DataFrame(lp_base),
    )

    expected_keys = [
        "batter_pressure_category_metrics",
        "batter_high_pressure_performance",
        "batter_baseline_comparison",
        "batter_situational_performance",
        "batter_pressure_reliability",
        "batter_pressure_performance_index",
        "batter_pressure_explanations",
        "validation_checks",
    ]
    for k in expected_keys:
        assert k in results

    assert len(results["batter_high_pressure_performance"]) == 1
    assert len(results["batter_pressure_performance_index"]) == 1
    assert len(results["batter_pressure_explanations"]) == 1

    # Check validation passed
    assert all(results["validation_checks"].values())

