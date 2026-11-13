"""Tests for macro dashboard metrics and highlights."""

from __future__ import annotations
import pytest
from dashboard.services.ranking_service import get_overview_kpis, get_ranking_highlights


def test_get_overview_kpis():
    """Verify macro KPIs match validated historical datasets."""
    kpis = get_overview_kpis()
    assert kpis["total_matches"] >= 800
    assert kpis["eligible_batters"] == 170
    assert kpis["eligible_bowlers"] == 232
    assert kpis["hp_deliveries"] >= 20000


def test_get_ranking_highlights():
    """Verify highest rated and most reliable distinctions."""
    highlights = get_ranking_highlights()
    assert highlights["highest_rated_batter"]["player_name"] == "Rinku Singh"
    assert highlights["highest_rated_bowler"]["player_name"] == "Joshua Little"
    assert highlights["most_reliable_batter"]["balls_faced"] >= 80
    assert highlights["most_reliable_bowler"]["legal_balls_bowled"] >= 60
