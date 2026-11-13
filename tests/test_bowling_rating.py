"""Unit tests for Phase 8 bowling rating calculations."""

from __future__ import annotations

import pandas as pd
import pytest

from src.ranking.ranking_config import RankingConfig
from src.ranking.bowling_rating import calculate_bowling_rating_components


def test_calculate_bowling_rating_components():
    """Verify component bounds and weighted composite raw FBOR."""
    cfg = RankingConfig()

    df = pd.DataFrame([
        {
            "player_id": "B1",
            "bppi_b": 68.0,
            "economy_rate": 7.2,
            "dot_ball_percentage": 45.0,
            "wickets_credited": 12,
            "legal_balls_bowled": 150,
            "economy_rate_variability": 1.5,
            "matches_bowled": 10,
            "innings_bowled": 8,
            "death_pct": 50.0,
            "extreme_pressure_balls": 25,
        },
        {
            "player_id": "B2",
            "bppi_b": 42.0,
            "economy_rate": 10.8,
            "dot_ball_percentage": 28.0,
            "wickets_credited": 3,
            "legal_balls_bowled": 50,
            "economy_rate_variability": 4.5,
            "matches_bowled": 4,
            "innings_bowled": 3,
            "death_pct": 20.0,
            "extreme_pressure_balls": 5,
        },
    ])

    res = calculate_bowling_rating_components(df, cfg, weights_profile="primary")

    for col in [
        "score_bowling_resilience",
        "score_bowling_absolute",
        "score_bowling_consistency",
        "score_bowling_context",
        "raw_fbor",
    ]:
        assert col in res.columns
        assert (res[col] >= 0.0).all()
        assert (res[col] <= 100.0).all()

    # B1 has much lower economy, more dots, more wickets -> raw_fbor must exceed B2
    b1 = res[res["player_id"] == "B1"].iloc[0]
    b2 = res[res["player_id"] == "B2"].iloc[0]

    assert b1["raw_fbor"] > b2["raw_fbor"]
    assert b1["score_bowling_absolute"] > b2["score_bowling_absolute"]

