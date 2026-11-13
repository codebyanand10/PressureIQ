"""Unit tests for the complete Player Baseline Calculation Engine pipeline.

Tests end-to-end baseline orchestration, table packaging, metadata generation,
and validation integration.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.baseline_engine import calculate_all_player_baselines
from src.baselines.baseline_config import BaselineConfig


def test_baseline_engine_end_to_end():
    """Verify calculate_all_player_baselines generates all expected baseline datasets."""
    mapping = pd.DataFrame({
        "comp_id": [1, 1],
        "comp_name": ["IPL 2024", "IPL 2024"],
        "team_id": [10, 20],
        "team_name": ["Team A", "Team B"],
        "player_id": ["P1", "BW1"],
        "player_name": ["Batter 1", "Bowler 1"],
    })

    pe = pd.DataFrame({
        "match_id": [101, 101],
        "team_id": [10, 20],
        "player_id": ["P1", "BW1"],
        "batting_order": [1, 11],
        "is_played": [True, True],
        "is_captain": [False, False],
        "is_wk": [False, False],
        "is_impact": [False, False],
        "is_impact_off": [False, False],
    })

    matches = pd.DataFrame({
        "match_id": [101],
        "match_date": ["2024-04-10"],
    })

    deliveries = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 101],
        "innings": [1, 1],
        "striker_id": ["P1", "P1"],
        "bowler_id": ["BW1", "BW1"],
        "batter_runs": [4, 1],
        "extras_runs": [0, 0],
        "extras_type": [None, None],
        "delivery_runs": [4, 1],
        "is_legal_delivery": [True, True],
        "is_wicket": [False, False],
        "dismissal_type": [None, None],
        "is_four": [True, False],
        "is_six": [False, False],
        "innings_phase_before": ["powerplay", "powerplay"],
        "competition_type": ["IPL", "IPL"],
        "batting_order": [1, 1],
        "batting_pressure_score": [25.0, 30.0],
        "bowling_pressure_score": [30.0, 35.0],
        "delivery_ist_time": ["2024-04-10 19:30:00", "2024-04-10 19:31:00"],
    })

    cfg = BaselineConfig()
    results = calculate_all_player_baselines(deliveries, mapping, pe, matches, cfg)

    expected_tables = [
        "player_registry",
        "batting_overall_baseline",
        "batting_low_pressure_baseline",
        "bowling_overall_baseline",
        "bowling_low_pressure_baseline",
        "batting_contextual_baseline",
        "bowling_contextual_baseline",
        "baseline_reliability",
        "baseline_metadata",
        "shrinkage_report",
        "validation_checks",
    ]

    for tbl in expected_tables:
        assert tbl in results, f"Expected table {tbl} missing from engine output."

    assert len(results["player_registry"]) == 2
    assert len(results["batting_overall_baseline"]) == 1
    assert len(results["bowling_overall_baseline"]) == 1
    assert all(results["validation_checks"].values())

