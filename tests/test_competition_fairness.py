"""Unit tests for Phase 9 competition fairness validation."""

import pandas as pd
import pytest

from src.validation.competition_fairness import evaluate_competition_fairness
from src.validation.validation_config import ValidationConfig


def test_evaluate_competition_fairness():
    """Verify that competition fairness evaluates IPL and T20I representations."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": ["p1", "p2", "p3", "p4"],
        "rank": [1, 2, 3, 4],
        "final_fbpr": [75.0, 70.0, 65.0, 60.0],
    })
    r_bowl = pd.DataFrame({
        "player_id": ["b1", "b2", "b3", "b4"],
        "rank": [1, 2, 3, 4],
        "final_fbor": [50.0, 48.0, 46.0, 44.0],
    })
    match_meta = pd.DataFrame({
        "match_id": [1, 2],
        "comp_name": ["Indian Premier League", "ICC Men's T20 World Cup"],
    })

    df_fairness, metrics = evaluate_competition_fairness(r_bat, r_bowl, match_meta, cfg)

    assert "competition" in df_fairness.columns
    assert set(df_fairness["competition"]).issubset({"IPL", "T20I"})
    assert "ipl_top10_batters_count" in metrics
    assert "t20i_top10_batters_count" in metrics

