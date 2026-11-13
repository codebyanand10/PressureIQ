"""Tests for multi-player comparison service."""

from __future__ import annotations
import pytest
from dashboard.services.comparison_service import compare_batters, compare_bowlers
from dashboard.services.ranking_service import filter_batter_rankings, filter_bowler_rankings


def test_compare_batters():
    """Verify side-by-side comparison of 2 top batters."""
    top_2 = filter_batter_rankings(top_n=2)
    ids = list(top_2["player_id"])
    res = compare_batters(ids)

    assert "players_df" in res
    assert "radar_data" in res
    assert len(res["players_df"]) == 2
    assert len(res["radar_data"]) == 2
    # Verify radar metrics are bounded 0-100
    for r in res["radar_data"]:
        for metric, val in r["metrics"].items():
            assert 0.0 <= val <= 100.0


def test_compare_bowlers():
    """Verify side-by-side comparison of 2 top bowlers."""
    top_2 = filter_bowler_rankings(top_n=2)
    ids = list(top_2["player_id"])
    res = compare_bowlers(ids)

    assert "players_df" in res
    assert "radar_data" in res
    assert len(res["players_df"]) == 2
    assert len(res["radar_data"]) == 2
    for r in res["radar_data"]:
        for metric, val in r["metrics"].items():
            assert 0.0 <= val <= 100.0

