"""Integration tests for match state reconstruction engine (Phase 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.match_state.match_state_engine import reconstruct_match_states


@pytest.fixture
def synthetic_full_match() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Match with Innings 1 and Innings 2
    bbb = pd.DataFrame({
        "match_id": [1, 1, 1, 1],
        "innings": [1, 1, 2, 2],
        "overid": [1, 1, 1, 1],
        "over_ball_num": [1, 2, 1, 2],
        "innings_ball_num": [1, 2, 1, 2],
        "delivery_order_idx": [0, 1, 2, 3],
        "runs": [4, 6, 1, 4],
        "extras1_runs": [0, 0, 0, 0],
        "extras_2_runs": [0, 0, 0, 0],
        "extras_type": [None, None, None, None],
        "is_four": [True, False, False, True],
        "is_six": [False, True, False, False],
        "is_wicket": [False, False, False, False],
        "dismissal_type": [None, None, None, None],
        "dismissed_player_id": [None, None, None, None],
        "batting_team_id": [10, 10, 20, 20],
        "bowling_team_id": [20, 20, 10, 10],
        "striker_id": [1, 1, 2, 2],
        "bowler_id": [20, 20, 10, 10],
    })

    matches = pd.DataFrame({
        "match_id": [1],
        "comp_id": [100],
        "match_format": ["T20"],
        "season": ["2024"],
        "result": ["Team 10 won"],
        "first_inn_revised_overs": [np.nan],
        "second_inn_revised_overs": [np.nan],
        "revised_target": [np.nan],
    })

    competitions = pd.DataFrame({
        "comp_id": [100],
        "comp_name": ["Test League 2024"],
        "match_format": ["T20"],
        "season": ["2024"],
        "competition_category": ["IPL"],
    })

    return bbb, matches, competitions


def test_reconstruct_match_states_end_to_end(synthetic_full_match):
    bbb, matches, competitions = synthetic_full_match
    states_df, summary_df, val_report = reconstruct_match_states(bbb, matches, competitions)

    # 1. Delivery row count exactly preserved
    assert len(states_df) == len(bbb)

    # 2. Innings summary count: 2 innings (Inn 1 and Inn 2)
    assert len(summary_df) == 2

    # 3. Target score correctly calculated for Innings 2:
    # Innings 1 scored 4 + 6 = 10 runs -> Target = 11
    inn2_rows = states_df[states_df["innings"] == 2]
    assert inn2_rows["target_score"].iloc[0] == 11.0
    assert inn2_rows["runs_required_before"].iloc[0] == 11.0
    assert inn2_rows["runs_required_after"].iloc[0] == 10.0

    # 4. Validation clean
    assert states_df["match_state_valid"].all()


def test_reconstruct_target_chase_completed():
    # 2nd innings where target is scored
    bbb = pd.DataFrame({
        "match_id": [1, 1],
        "innings": [1, 2],
        "overid": [1, 1],
        "over_ball_num": [1, 1],
        "innings_ball_num": [1, 1],
        "delivery_order_idx": [0, 1],
        "runs": [4, 6],
        "extras1_runs": [0, 0],
        "extras_2_runs": [0, 0],
        "extras_type": [None, None],
        "is_four": [True, False],
        "is_six": [False, True],
        "is_wicket": [False, False],
        "dismissal_type": [None, None],
        "dismissed_player_id": [None, None],
        "batting_team_id": [10, 20],
        "bowling_team_id": [20, 10],
        "striker_id": [1, 2],
        "bowler_id": [20, 10],
    })
    matches = pd.DataFrame({
        "match_id": [1],
        "comp_id": [100],
        "match_format": ["T20"],
        "season": ["2024"],
        "result": ["Team 20 won"],
    })
    competitions = pd.DataFrame({
        "comp_id": [100],
        "comp_name": ["Test League"],
        "match_format": ["T20"],
        "season": ["2024"],
    })

    states_df, summary_df, _ = reconstruct_match_states(bbb, matches, competitions)
    # Inn 1 score 4 -> Target 5
    # Inn 2 scores 6 -> runs_required_after = 0 (target chased)
    assert states_df.loc[1, "runs_required_after"] == 0.0
    inn2_summary = summary_df[summary_df["innings"] == 2].iloc[0]
    assert inn2_summary["innings_termination_reason"] == "TARGET_CHASED"

