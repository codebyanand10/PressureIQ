"""Tests for Ranking Auditor."""

from pathlib import Path
from src.final_audit.ranking_audit import RankingAuditor


def test_ranking_auditor():
    """Verify top 10 batter and bowler rankings pass all integrity checks."""
    root_dir = Path(__file__).resolve().parents[2]
    auditor = RankingAuditor(root_dir)
    summary = auditor.audit()

    assert summary.batting_verified is True
    assert summary.bowling_verified is True
    assert summary.cross_format_concordance is True
    assert summary.has_critical_issues is False
    assert len(summary.top_10_batters) == 10
    assert len(summary.top_10_bowlers) == 10

    # Verify Rinku Singh is #1 batter
    assert summary.top_10_batters[0]["player_name"] == "Rinku Singh"
    assert round(float(summary.top_10_batters[0]["final_fbpr"]), 2) == 77.07

    # Verify Joshua Little is #1 bowler
    assert summary.top_10_bowlers[0]["player_name"] == "Joshua Little"
    assert round(float(summary.top_10_bowlers[0]["final_fbor"]), 2) == 50.05

