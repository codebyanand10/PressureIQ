"""Integration tests for the complete Bowling Performance Under Pressure Engine."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.bowling_pressure_engine import calculate_bowling_pressure_performance


def test_bowling_pressure_engine_end_to_end():
    """Verify that end-to-end pipeline produces all 8 datasets, role analysis, and passes validations."""
    deliveries = []
    # 3 matches, bowler B1 bowls high pressure and low pressure deliveries
    for m in range(1, 4):
        # 10 High pressure balls per match
        for b in range(10):
            deliveries.append({
                "match_id": m,
                "innings": 2,
                "bowler_id": "B1",
                "bowler_name": "Death Specialist",
                "batter_runs": 0 if b % 2 == 0 else 1,
                "extras_runs": 0,
                "extras_type": None,
                "is_legal_delivery": True,
                "is_four": False,
                "is_six": False,
                "is_wicket": b == 0,
                "wicket_type": "Bowled" if b == 0 else None,
                "bowling_pressure_score": 75.0,  # High pressure
                "innings_phase_before": "death",
                "overid": 18,
                "competition_name": "IPL",
                "knock_out": True,
                "pace_or_spin": "pace",
            })
        # 5 Low pressure balls per match
        for b in range(5):
            deliveries.append({
                "match_id": m,
                "innings": 1,
                "bowler_id": "B1",
                "bowler_name": "Death Specialist",
                "batter_runs": 1,
                "extras_runs": 0,
                "extras_type": None,
                "is_legal_delivery": True,
                "is_four": False,
                "is_six": False,
                "is_wicket": False,
                "wicket_type": None,
                "bowling_pressure_score": 25.0,  # Low pressure
                "innings_phase_before": "middle",
                "overid": 12,
                "competition_name": "IPL",
                "knock_out": False,
                "pace_or_spin": "pace",
            })

    registry = [{"player_id": "B1", "player_name": "Death Specialist", "bowling_type": "Right-arm fast"}]
    overall_base = [{
        "player_id": "B1",
        "economy_rate": 8.5,
        "bowling_average": 22.0,
        "bowling_strike_rate": 18.0,
        "shrunk_economy_rate": 8.4,
        "shrunk_bowling_average": 22.5,
        "dot_ball_percentage": 40.0,
        "boundary_percentage_conceded": 15.0,
        "baseline_reliability_level": "Medium",
    }]
    lp_base = [{
        "player_id": "B1",
        "economy_rate": 7.8,
        "bowling_average": 25.0,
        "bowling_strike_rate": 20.0,
        "dot_ball_percentage": 42.0,
        "boundary_percentage_conceded": 14.0,
    }]

    results = calculate_bowling_pressure_performance(
        deliveries_df=pd.DataFrame(deliveries),
        player_registry_df=pd.DataFrame(registry),
        overall_baseline_df=pd.DataFrame(overall_base),
        low_pressure_baseline_df=pd.DataFrame(lp_base),
    )

    expected_keys = [
        "bowler_pressure_category_metrics",
        "bowler_high_pressure_performance",
        "bowler_baseline_comparison",
        "bowler_situational_performance",
        "bowler_role_analysis",
        "bowler_pressure_reliability",
        "bowler_pressure_performance_index",
        "bowler_pressure_explanations",
        "validation_checks",
    ]
    for k in expected_keys:
        assert k in results

    assert len(results["bowler_high_pressure_performance"]) == 1
    assert len(results["bowler_pressure_performance_index"]) == 1
    assert len(results["bowler_pressure_explanations"]) == 1
    assert len(results["bowler_role_analysis"]) == 1

    # Check validation passed
    assert all(results["validation_checks"].values())
