"""Unit tests for bowling explanation generator."""

from __future__ import annotations

import pandas as pd
import pytest

from src.bowling_pressure.explanation_generator import generate_bowler_explanations


def test_generate_bowler_explanations_fields():
    """Verify that narrative explanations generate complete diagnostic fields."""
    classified_df = pd.DataFrame([
        {
            "player_id": "B1",
            "player_name": "Jasprit Bumrah",
            "bowler_classification": "Elite Under Pressure",
            "bppi_b": 85.0,
            "legal_balls_bowled": 300,
            "overs_bowled": 50.0,
            "runs_conceded": 350,
            "wickets_credited": 25,
            "economy_rate": 7.0,
            "economy_retention": 110.0,
            "economy_difference": -1.0,
            "dot_ball_difference": 5.0,
            "boundary_prevention_difference": -3.0,
            "wicket_taking_difference": 0.02,
            "reliability_level": "High",
            "score_economy_retention": 80.0,
            "score_wicket_taking": 85.0,
            "score_dot_ball_generation": 75.0,
            "score_boundary_prevention": 80.0,
            "score_average_retention": 90.0,
        }
    ])

    res = generate_bowler_explanations(classified_df)

    assert len(res) == 1
    row = res.iloc[0]

    assert "pressure_performance_summary" in row
    assert "strengths_under_pressure" in row
    assert "weaknesses_under_pressure" in row
    assert "dominant_performance_factor" in row
    assert "classification_reason" in row

    assert "Jasprit Bumrah" in row["pressure_performance_summary"]
    assert len(row["strengths_under_pressure"]) > 0
