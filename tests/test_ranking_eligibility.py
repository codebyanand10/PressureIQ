"""Unit tests for Phase 8 player eligibility evaluation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.ranking.ranking_config import RankingConfig
from src.ranking.eligibility import (
    evaluate_batting_eligibility,
    evaluate_bowling_eligibility,
)


def test_batting_eligibility_criteria():
    """Verify Eligible, Provisionally Eligible, and Insufficient Evidence classifications for batters."""
    cfg = RankingConfig()

    bat_df = pd.DataFrame([
        # Eligible: >= 40 balls, >= 4 matches, >= 3 innings
        {"player_id": "P_ELIG", "player_name": "Eligible Batter", "balls_faced": 50, "matches_count": 5, "innings_count": 4},
        # Provisionally Eligible: 20-39 balls, >= 2 matches
        {"player_id": "P_PROV", "player_name": "Provisional Batter", "balls_faced": 25, "matches_count": 3, "innings_count": 2},
        # Insufficient Evidence: < 20 balls
        {"player_id": "P_INSUF", "player_name": "Insufficient Batter", "balls_faced": 10, "matches_count": 2, "innings_count": 1},
        # Unregistered player
        {"player_id": "P_UNREG", "player_name": "Unregistered Batter", "balls_faced": 60, "matches_count": 6, "innings_count": 5},
    ])

    base_df = pd.DataFrame([
        {"player_id": "P_ELIG", "strike_rate": 135.0},
        {"player_id": "P_PROV", "strike_rate": 130.0},
        {"player_id": "P_INSUF", "strike_rate": 125.0},
        {"player_id": "P_UNREG", "strike_rate": 140.0},
    ])

    reg_df = pd.DataFrame([
        {"player_id": "P_ELIG", "player_name": "Eligible Batter"},
        {"player_id": "P_PROV", "player_name": "Provisional Batter"},
        {"player_id": "P_INSUF", "player_name": "Insufficient Batter"},
    ])  # P_UNREG is not registered

    res = evaluate_batting_eligibility(bat_df, base_df, reg_df, cfg)
    status_map = res.set_index("player_id")["eligibility_status"].to_dict()

    assert status_map["P_ELIG"] == "Eligible"
    assert status_map["P_PROV"] == "Provisionally Eligible"
    assert status_map["P_INSUF"] == "Insufficient Evidence"
    assert status_map["P_UNREG"] == "Data Quality Exclusion"


def test_bowling_eligibility_criteria():
    """Verify Eligible, Provisionally Eligible, and Data Quality Exclusion for bowlers."""
    cfg = RankingConfig()

    bowl_df = pd.DataFrame([
        # Eligible: >= 48 legal balls, >= 4 matches, >= 3 innings
        {"player_id": "B_ELIG", "player_name": "Eligible Bowler", "legal_balls_bowled": 60, "matches_bowled": 5, "innings_bowled": 4},
        # Provisionally Eligible: 24-47 balls, >= 2 matches
        {"player_id": "B_PROV", "player_name": "Provisional Bowler", "legal_balls_bowled": 30, "matches_bowled": 3, "innings_bowled": 2},
        # Missing Baseline
        {"player_id": "B_NO_BASE", "player_name": "No Baseline Bowler", "legal_balls_bowled": 80, "matches_bowled": 6, "innings_bowled": 5},
    ])

    base_df = pd.DataFrame([
        {"player_id": "B_ELIG", "economy_rate": 7.5},
        {"player_id": "B_PROV", "economy_rate": 8.0},
    ])  # B_NO_BASE has no baseline

    reg_df = pd.DataFrame([
        {"player_id": "B_ELIG", "player_name": "Eligible Bowler"},
        {"player_id": "B_PROV", "player_name": "Provisional Bowler"},
        {"player_id": "B_NO_BASE", "player_name": "No Baseline Bowler"},
    ])

    res = evaluate_bowling_eligibility(bowl_df, base_df, reg_df, cfg)
    status_map = res.set_index("player_id")["eligibility_status"].to_dict()

    assert status_map["B_ELIG"] == "Eligible"
    assert status_map["B_PROV"] == "Provisionally Eligible"
    assert status_map["B_NO_BASE"] == "Data Quality Exclusion"

