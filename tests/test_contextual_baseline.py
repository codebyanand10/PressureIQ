"""Unit tests for contextual player baselines.

Tests phase, competition, innings number, and batting position group partitioning.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.contextual_baseline import calculate_contextual_baselines
from src.baselines.baseline_config import BaselineConfig


def test_calculate_contextual_baselines_phase_and_competition():
    """Verify context breakdown across phases and competitions."""
    deliveries = pd.DataFrame({
        "delivery_sequence": [1, 2, 3],
        "match_id": [101, 101, 102],
        "innings": [1, 1, 2],
        "striker_id": ["P1", "P1", "P1"],
        "bowler_id": ["BW1", "BW1", "BW2"],
        "batter_runs": [4, 6, 1],
        "extras_runs": [0, 0, 0],
        "extras_type": [None, None, None],
        "delivery_runs": [4, 6, 1],
        "is_legal_delivery": [True, True, True],
        "is_wicket": [False, False, False],
        "dismissal_type": [None, None, None],
        "is_four": [True, False, False],
        "is_six": [False, True, False],
        "innings_phase_before": ["powerplay", "death", "middle"],
        "competition_type": ["IPL", "IPL", "T20I"],
        "batting_order": [1, 1, 1],
        "delivery_ist_time": ["2024-04-01"] * 3,
    })

    registry = pd.DataFrame({
        "player_id": ["P1", "BW1", "BW2"],
        "player_name": ["Batter 1", "Bowler 1", "Bowler 2"],
    })

    cfg = BaselineConfig()
    bat_context, bowl_context = calculate_contextual_baselines(deliveries, registry, cfg)

    assert len(bat_context) > 0
    assert len(bowl_context) > 0

    # Verify context types
    bat_types = set(bat_context["context_type"])
    assert "innings_phase" in bat_types
    assert "competition_type" in bat_types
    assert "innings_number" in bat_types

    # Verify powerplay batting
    pp_row = bat_context[(bat_context["context_type"] == "innings_phase") & (bat_context["context_value"] == "powerplay")]
    assert len(pp_row) == 1
    assert pp_row.iloc[0]["total_runs"] == 4
    assert pp_row.iloc[0]["strike_rate"] == 400.0

