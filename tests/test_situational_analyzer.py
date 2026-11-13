"""Unit tests for situational batting analysis under pressure."""

from __future__ import annotations

import pandas as pd
import pytest

from src.batting_pressure.situational_analyzer import analyze_situational_batting


def test_situational_analyzer_contexts():
    """Verify that deliveries are correctly sliced across phase, innings, and competition."""
    deliveries = [
        # Death overs, 2nd innings, IPL
        {
            "match_id": 1, "innings": 2, "striker_id": "P1", "batter_runs": 6, "extras_runs": 0, "extras_type": None,
            "is_four": False, "is_six": True, "is_wicket": False, "batting_pressure_score": 75.0,
            "innings_phase_before": "death", "competition_type": "IPL", "knock_out": True, "batting_order": 5
        },
        # Powerplay overs, 1st innings, T20I
        {
            "match_id": 2, "innings": 1, "striker_id": "P1", "batter_runs": 4, "extras_runs": 0, "extras_type": None,
            "is_four": True, "is_six": False, "is_wicket": False, "batting_pressure_score": 45.0,
            "innings_phase_before": "powerplay", "competition_type": "T20I", "knock_out": False, "batting_order": 2
        },
    ]
    registry = [{"player_id": "P1", "player_name": "Versatile Batter"}]

    sit_df = analyze_situational_batting(
        deliveries_df=pd.DataFrame(deliveries),
        player_registry_df=pd.DataFrame(registry),
    )

    types = set(sit_df["context_type"].unique())
    assert "innings_phase" in types
    assert "innings_number" in types
    assert "competition_type" in types
    assert "match_stage" in types
    assert "batting_position" in types
    assert "pressure_intensity" in types

    death_rec = sit_df[(sit_df["context_type"] == "innings_phase") & (sit_df["context_value"] == "death")]
    assert len(death_rec) == 1
    assert death_rec.iloc[0]["total_runs"] == 6

