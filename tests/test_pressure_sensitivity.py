"""Unit tests for Phase 9 pressure model sensitivity analysis."""

import pandas as pd
import pytest

from src.validation.pressure_sensitivity import evaluate_pressure_model_sensitivity
from src.validation.validation_config import ValidationConfig


def test_evaluate_pressure_model_sensitivity():
    """Verify that pressure model sensitivity evaluates alternative pressure expressions."""
    cfg = ValidationConfig()

    r_bat = pd.DataFrame({
        "player_id": [f"bat_{i}" for i in range(10)],
        "rank": list(range(1, 11)),
    })
    r_bowl = pd.DataFrame({
        "player_id": [f"bowl_{i}" for i in range(10)],
        "rank": list(range(1, 11)),
    })

    df_summary, df_players = evaluate_pressure_model_sensitivity(r_bat, r_bowl, cfg)

    assert "pressure_scenario" in df_summary.columns
    assert "batting_top10_overlap" in df_summary.columns
    assert "bowling_top10_overlap" in df_summary.columns
    assert "sensitivity_status" in df_summary.columns
    assert len(df_summary) >= 3

