"""Unit tests for cricket-specific domain validation (Phase 2)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.cricket_validation import (
    validate_delivery_numbering,
    validate_dismissal_consistency,
    validate_extras_consistency,
    validate_match_consistency,
    validate_scoring_consistency,
)


@pytest.fixture
def clean_delivery_sample() -> pd.DataFrame:
    return pd.DataFrame({
        "match_id": [1, 1, 1],
        "innings": [1, 1, 1],
        "overid": [1, 1, 1],
        "over_ball_num": [1, 2, 3],
        "innings_ball_num": [1, 2, 3],
        "runs": [0, 4, 6],
        "extras1_runs": [1, 0, 0],
        "extras_2_runs": [0, 0, 0],
        "extras_type": ["wide", None, None],
        "is_four": [False, True, False],
        "is_six": [False, False, True],
        "is_wicket": [False, False, True],
        "dismissal_type": [None, None, "Bowled"],
        "dismissed_player_id": [None, None, 101],
        "batting_team_id": [10, 10, 10],
        "bowling_team_id": [20, 20, 20],
    })


def test_validate_scoring_consistency(clean_delivery_sample: pd.DataFrame):
    result = validate_scoring_consistency(clean_delivery_sample)
    assert result["is_valid"] is True
    assert result["negative_runs_count"] == 0
    assert result["fours_flagged_count"] == 1
    assert result["sixes_flagged_count"] == 1


def test_validate_extras_consistency(clean_delivery_sample: pd.DataFrame):
    result = validate_extras_consistency(clean_delivery_sample)
    assert result["is_valid"] is True
    assert result["total_wides"] == 1
    assert result["wides_with_bat_runs"] == 0


def test_validate_dismissal_consistency(clean_delivery_sample: pd.DataFrame):
    result = validate_dismissal_consistency(clean_delivery_sample)
    assert result["is_valid"] is True
    assert result["total_wickets"] == 1
    assert result["bowler_credited_wickets"] == 1
    assert result["wickets_missing_type_count"] == 0


def test_validate_delivery_numbering(clean_delivery_sample: pd.DataFrame):
    result = validate_delivery_numbering(clean_delivery_sample)
    assert result["is_valid"] is True
    assert result["duplicate_innings_ball_count"] == 0
    assert result["invalid_over_ball_num_count"] == 0


def test_validate_match_consistency(clean_delivery_sample: pd.DataFrame):
    matches_sample = pd.DataFrame({
        "match_id": [1],
        "home_team_id": [10],
        "away_team_id": [20],
        "result": ["Team 10 won"],
    })
    result = validate_match_consistency(matches_sample, clean_delivery_sample)
    assert result["unmatched_batting_teams"] == 0
    assert result["unmatched_bowling_teams"] == 0
    assert result["uncontested_matches_count"] == 0

