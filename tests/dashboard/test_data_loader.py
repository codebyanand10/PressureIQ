"""Tests for dashboard data loader service."""

from __future__ import annotations
import pytest
import pandas as pd
from dashboard.services.data_loader import (
    load_batter_ratings,
    load_bowler_ratings,
    load_ranking_components,
    load_ranking_explanations,
    load_match_metadata,
    load_validation_scorecard,
    load_bootstrap_results,
    load_stability_results,
    load_leakage_audit,
    load_pressure_scores_summary,
)


def test_load_batter_ratings_actual():
    """Verify that actual Phase 8 batter ratings load correctly without fabrication."""
    df = load_batter_ratings()
    assert not df.empty
    assert len(df) == 170
    assert "rank" in df.columns
    assert "final_fbpr" in df.columns
    assert "ci_lower_fbpr" in df.columns
    assert "ci_upper_fbpr" in df.columns
    # Check #1 rank
    top_1 = df[df["rank"] == 1].iloc[0]
    assert top_1["player_name"] == "Rinku Singh"
    assert top_1["final_fbpr"] > 70.0


def test_load_bowler_ratings_actual():
    """Verify that actual Phase 8 bowler ratings load correctly without fabrication."""
    df = load_bowler_ratings()
    assert not df.empty
    assert len(df) == 232
    assert "rank" in df.columns
    assert "final_fbor" in df.columns
    assert "ci_lower_fbor" in df.columns
    assert "ci_upper_fbor" in df.columns
    top_1 = df[df["rank"] == 1].iloc[0]
    assert top_1["player_name"] == "Joshua Little"


def test_load_validation_scorecard_actual():
    """Verify official Phase 9 10-dimension scorecard loads accurately."""
    df = load_validation_scorecard()
    assert not df.empty
    assert len(df) == 10
    assert "dimension" in df.columns
    assert "batting_result" in df.columns
    assert "bowling_result" in df.columns


def test_load_pressure_summary_fast():
    """Verify fast DuckDB pressure summary executes and returns required counts."""
    summary = load_pressure_scores_summary()
    assert isinstance(summary, dict)
    assert "total_deliveries" in summary
    assert summary["total_deliveries"] >= 200000
    assert "hp_deliveries" in summary
    assert summary["hp_deliveries"] > 0

