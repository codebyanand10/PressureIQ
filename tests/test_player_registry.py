"""Unit tests for player registry creation and metadata management.

Tests player identity consistency, multi-team representation, bench reserve handling,
and distinct active participation tracking.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.baselines.player_registry import build_player_registry


def test_build_player_registry_multi_team_and_participation():
    """Verify registry builds with multi-team representation and active flags."""
    mapping = pd.DataFrame({
        "comp_id": [1, 2],
        "comp_name": ["IPL 2024", "T20I 2024"],
        "team_id": [10, 20],
        "team_name": ["Rajasthan Royals", "India"],
        "player_id": ["P100", "P100"],
        "player_name": ["Sanju Samson", "Sanju Samson"],
    })

    playing_eleven = pd.DataFrame({
        "match_id": [101, 102],
        "team_id": [10, 20],
        "player_id": ["P100", "P100"],
        "batting_order": [3, 4],
        "is_played": [True, True],
        "is_captain": [True, False],
        "is_wk": [True, True],
        "is_impact": [False, False],
        "is_impact_off": [False, False],
    })

    matches = pd.DataFrame({
        "match_id": [101, 102],
        "match_date": ["2024-04-10", "2024-06-15"],
    })

    deliveries = pd.DataFrame({
        "delivery_sequence": [1, 2],
        "match_id": [101, 101],
        "innings": [1, 1],
        "striker_id": ["P100", "P100"],
        "bowler_id": ["B200", "B200"],
        "extras_type": [None, None],
        "is_legal_delivery": [True, True],
    })

    registry = build_player_registry(mapping, playing_eleven, matches, deliveries)

    assert len(registry) == 1
    row = registry.iloc[0]
    assert row["player_id"] == "P100"
    assert "Rajasthan Royals" in row["registered_teams"]
    assert "India" in row["registered_teams"]
    assert row["matches_available"] == 2
    assert row["first_recorded_match"] == "2024-04-10"
    assert row["last_recorded_match"] == "2024-06-15"
    assert row["batting_innings"] == 1
    assert row["is_active_batter"] == True
    assert row["is_active_bowler"] == False


def test_build_player_registry_bench_reserve():
    """Verify registered bench players who never played are flagged inactive."""
    mapping = pd.DataFrame({
        "comp_id": [1],
        "comp_name": ["IPL 2024"],
        "team_id": [10],
        "team_name": ["Rajasthan Royals"],
        "player_id": ["P999"],
        "player_name": ["Bench Player"],
    })
    empty_pe = pd.DataFrame(columns=["match_id", "team_id", "player_id", "match_date"])
    empty_m = pd.DataFrame(columns=["match_id", "match_date"])
    empty_deliv = pd.DataFrame(columns=["delivery_sequence", "match_id", "innings", "striker_id", "bowler_id", "extras_type", "is_legal_delivery"])

    registry = build_player_registry(mapping, empty_pe, empty_m, empty_deliv)
    row = registry.iloc[0]
    assert row["matches_available"] == 0
    assert row["is_active_batter"] == False
    assert row["is_active_bowler"] == False
    assert row["has_participated"] == False

