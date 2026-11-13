"""Unit tests for Phase 9 scoring weight sensitivity analysis."""

import pandas as pd
import pytest

from src.validation.sensitivity_analysis import run_weight_sensitivity_analysis
from src.validation.validation_config import ValidationConfig


def test_run_weight_sensitivity_analysis():
    """Verify that sensitivity analysis evaluates all configured scenarios."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": ["p1", "p2", "p3"],
        "player_name": ["Player 1", "Player 2", "Player 3"],
        "rank": [1, 2, 3],
        "final_fbpr": [75.0, 70.0, 65.0],
        "balls_faced": [150, 120, 100],
        "score_batting_resilience": [75.0, 68.0, 60.0],
        "score_batting_absolute": [80.0, 72.0, 64.0],
        "score_batting_consistency": [60.0, 62.0, 58.0],
        "score_batting_context": [65.0, 60.0, 55.0],
    })

    r_bowl = pd.DataFrame({
        "player_id": ["b1", "b2", "b3"],
        "player_name": ["Bowler 1", "Bowler 2", "Bowler 3"],
        "rank": [1, 2, 3],
        "final_fbor": [50.0, 48.0, 45.0],
        "legal_balls_bowled": [180, 150, 120],
        "score_bowling_resilience": [52.0, 49.0, 44.0],
        "score_bowling_absolute": [55.0, 50.0, 46.0],
        "score_bowling_consistency": [58.0, 56.0, 54.0],
        "score_bowling_context": [50.0, 48.0, 45.0],
    })

    bat_sens, bowl_sens, summary = run_weight_sensitivity_analysis(r_bat, r_bowl, cfg)

    assert len(summary) == len(cfg.SENSITIVITY_SCENARIOS)
    assert "scenario" in summary.columns
    assert "batting_spearman" in summary.columns
    assert "bowling_spearman" in summary.columns

    # Check that ratings are within [0, 100]
    assert (bat_sens["scenario_fbpr"] >= 0.0).all() and (bat_sens["scenario_fbpr"] <= 100.0).all()
    assert (bowl_sens["scenario_fbor"] >= 0.0).all() and (bowl_sens["scenario_fbor"] <= 100.0).all()

