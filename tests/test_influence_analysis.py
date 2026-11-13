"""Unit tests for Phase 9 single-match influence analysis."""

import pandas as pd
import pytest

from src.validation.influence_analysis import evaluate_influential_matches
from src.validation.validation_config import ValidationConfig


def test_evaluate_influential_matches():
    """Verify single-match leverage identification for Top 10 players."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": ["p1", "p2"],
        "player_name": ["P1", "P2"],
        "rank": [1, 2],
        "final_fbpr": [75.0, 70.0],
        "strike_rate": [180.0, 160.0],
    })
    r_bowl = pd.DataFrame({
        "player_id": ["b1", "b2"],
        "player_name": ["B1", "B2"],
        "rank": [1, 2],
        "final_fbor": [50.0, 48.0],
    })

    bat_m = pd.DataFrame([
        {"player_id": "p1", "match_id": 101, "hp_runs": 50, "hp_balls": 25},
        {"player_id": "p1", "match_id": 102, "hp_runs": 30, "hp_balls": 18},
        {"player_id": "p2", "match_id": 101, "hp_runs": 20, "hp_balls": 15},
    ])
    bowl_m = pd.DataFrame([
        {"player_id": "b1", "match_id": 101, "hp_wickets": 3, "hp_legal_balls": 24, "hp_runs_conceded": 20},
        {"player_id": "b1", "match_id": 102, "hp_wickets": 1, "hp_legal_balls": 24, "hp_runs_conceded": 28},
        {"player_id": "b2", "match_id": 101, "hp_wickets": 1, "hp_legal_balls": 24, "hp_runs_conceded": 32},
    ])
    meta = pd.DataFrame({
        "match_id": [101, 102],
        "home_team": ["Team A", "Team C"],
        "away_team": ["Team B", "Team D"],
        "match_date": ["2023-04-10", "2023-04-15"],
    })

    df_inf, metrics = evaluate_influential_matches(r_bat, r_bowl, bat_m, bowl_m, meta, cfg)

    assert "most_influential_match_id" in df_inf.columns
    assert "volume_share_in_match" in df_inf.columns
    assert "statistical_interpretation" in df_inf.columns
    assert "batters_with_high_influence_match" in metrics

