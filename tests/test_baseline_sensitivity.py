"""Unit tests for Phase 9 baseline sensitivity analysis."""

import pandas as pd
import pytest

from src.validation.baseline_sensitivity import evaluate_baseline_sensitivity
from src.validation.validation_config import ValidationConfig


def test_evaluate_baseline_sensitivity():
    """Verify that overall vs contextual baseline sensitivity calculates correlations."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": ["p1", "p2", "p3"],
        "player_name": ["P1", "P2", "P3"],
        "rank": [1, 2, 3],
        "final_fbpr": [75.0, 70.0, 65.0],
        "strike_rate": [180.0, 160.0, 150.0],
        "overall_strike_rate": [140.0, 135.0, 130.0],
        "balls_faced": [150, 120, 100],
        "score_batting_absolute": [80.0, 70.0, 65.0],
        "score_batting_consistency": [60.0, 58.0, 55.0],
        "score_batting_context": [65.0, 60.0, 55.0],
    })

    r_bowl = pd.DataFrame({
        "player_id": ["b1", "b2", "b3"],
        "player_name": ["B1", "B2", "B3"],
        "rank": [1, 2, 3],
        "final_fbor": [50.0, 48.0, 46.0],
        "economy_rate": [7.5, 8.0, 8.5],
        "overall_economy_rate": [7.8, 8.2, 8.4],
        "legal_balls_bowled": [180, 150, 120],
        "score_bowling_absolute": [55.0, 50.0, 48.0],
        "score_bowling_consistency": [58.0, 56.0, 54.0],
        "score_bowling_context": [52.0, 50.0, 48.0],
    })

    ctx_bat = pd.DataFrame({"player_id": ["p1", "p2", "p3"]})
    ctx_bowl = pd.DataFrame({"player_id": ["b1", "b2", "b3"]})

    df_out, metrics = evaluate_baseline_sensitivity(r_bat, r_bowl, ctx_bat, ctx_bowl, cfg)

    assert "contextual_rating" in df_out.columns
    assert "batting_baseline_spearman" in metrics
    assert "bowling_baseline_spearman" in metrics

