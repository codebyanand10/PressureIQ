"""Tests for leaderboard querying, sorting, and display limits."""

from __future__ import annotations
import pytest
from dashboard.services.ranking_service import filter_batter_rankings, filter_bowler_rankings


def test_filter_batter_rankings_top10():
    """Verify top 10 batter retrieval preserves rankings without mutation."""
    top_10 = filter_batter_rankings(top_n=10)
    assert len(top_10) == 10
    ranks = list(top_10["rank"])
    assert ranks == list(range(1, 11))
    assert top_10.iloc[0]["player_name"] == "Rinku Singh"


def test_filter_batter_rankings_search():
    """Verify searching for a specific batter by substring."""
    res = filter_batter_rankings(search_query="Rinku")
    assert len(res) >= 1
    assert any("Rinku" in name for name in res["player_name"])


def test_filter_bowler_rankings_top10():
    """Verify top 10 bowler retrieval preserves rankings without mutation."""
    top_10 = filter_bowler_rankings(top_n=10)
    assert len(top_10) == 10
    ranks = list(top_10["rank"])
    assert ranks == list(range(1, 11))
    assert top_10.iloc[0]["player_name"] == "Joshua Little"


def test_filter_bowler_rankings_role():
    """Verify filtering bowlers by role (e.g. Death overs)."""
    res = filter_bowler_rankings(top_n=10, bowling_role="Death")
    assert len(res) > 0
    assert all(d >= 24 for d in res["DEATH_OVERS"])
