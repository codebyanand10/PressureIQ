"""Unit tests for Phase 8 batting rating calculations."""

from __future__ import annotations

import pandas as pd
import pytest

from src.ranking.ranking_config import RankingConfig
from src.ranking.batting_rating import calculate_batting_rating_components


def test_calculate_batting_rating_components():
    """Verify component bounds and weighted composite raw FBPR."""
    cfg = RankingConfig()

    df = pd.DataFrame([
        {
            "player_id": "P1",
            "bppi": 75.0,
            "strike_rate": 180.0,
            "boundary_percentage": 55.0,
            "strike_rate_variability": 30.0,
            "matches_count": 8,
            "innings_count": 6,
            "balls_faced": 120,
            "extreme_pressure_balls": 30,
        },
        {
            "player_id": "P2",
            "bppi": 45.0,
            "strike_rate": 110.0,
            "boundary_percentage": 30.0,
            "strike_rate_variability": 70.0,
            "matches_count": 4,
            "innings_count": 3,
            "balls_faced": 45,
            "extreme_pressure_balls": 5,
        },
    ])

    res = calculate_batting_rating_components(df, cfg, weights_profile="primary")

    for col in [
        "score_batting_resilience",
        "score_batting_absolute",
        "score_batting_consistency",
        "score_batting_context",
        "raw_fbpr",
    ]:
        assert col in res.columns
        assert (res[col] >= 0.0).all()
        assert (res[col] <= 100.0).all()

    # P1 is an elite pressure batter -> raw_fbpr must exceed P2
    p1 = res[res["player_id"] == "P1"].iloc[0]
    p2 = res[res["player_id"] == "P2"].iloc[0]

    assert p1["raw_fbpr"] > p2["raw_fbpr"]
    assert p1["score_batting_absolute"] > p2["score_batting_absolute"]

