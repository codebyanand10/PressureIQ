"""Unit tests for pre- and post-delivery state calculations (Phase 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.match_state.innings_config import InningsConfig
from src.match_state.state_calculator import calculate_match_states


@pytest.fixture
def synthetic_innings_data() -> Tuple[pd.DataFrame, dict]:
    deliveries = pd.DataFrame({
        "match_id": [1, 1, 1, 1],
        "innings": [2, 2, 2, 2],
        "delivery_order_idx": [0, 1, 2, 3],
        "runs": [4, 0, 1, 6],
        "extras1_runs": [0, 1, 0, 0],
        "extras_2_runs": [0, 0, 0, 0],
        "delivery_runs": [4, 1, 1, 6],
        "is_legal_delivery": [True, False, True, True],
        "is_wicket": [False, False, True, False],
        "wickets_on_delivery": [0, 0, 1, 0],
        "batting_team_id": [10, 10, 10, 10],
        "bowling_team_id": [20, 20, 20, 20],
    })

    configs = {
        (1, 2): InningsConfig(
            match_id=1,
            innings=2,
            comp_id=100,
            match_format="T20",
            season="2024",
            is_first_innings=False,
            is_chasing_innings=True,
            is_super_over=False,
            scheduled_overs=20.0,
            available_overs=20.0,
            available_legal_balls=120,
            is_reduced_overs=False,
            has_target=True,
            target_score=150.0,
            target_source="FIRST_INNINGS_TOTAL",
        )
    }
    return deliveries, configs


def test_state_calculator_pre_and_post_runs(synthetic_innings_data):
    deliveries, configs = synthetic_innings_data
    states = calculate_match_states(deliveries, configs)

    # Ball 1: pre-runs = 0, post-runs = 4
    assert states.loc[0, "runs_before"] == 0
    assert states.loc[0, "runs_after"] == 4

    # Ball 2 (Wide, 1 run): pre-runs = 4, post-runs = 5
    assert states.loc[1, "runs_before"] == 4
    assert states.loc[1, "runs_after"] == 5

    # Ball 3 (1 run + Wicket): pre-runs = 5, post-runs = 6
    assert states.loc[2, "runs_before"] == 5
    assert states.loc[2, "runs_after"] == 6

    # Ball 4 (Six): pre-runs = 6, post-runs = 12
    assert states.loc[3, "runs_before"] == 6
    assert states.loc[3, "runs_after"] == 12


def test_state_calculator_wickets_accumulation(synthetic_innings_data):
    deliveries, configs = synthetic_innings_data
    states = calculate_match_states(deliveries, configs)

    # Ball 1 & 2: 0 wickets
    assert states.loc[0, "wickets_before"] == 0
    assert states.loc[0, "wickets_after"] == 0
    assert states.loc[1, "wickets_before"] == 0
    assert states.loc[1, "wickets_after"] == 0

    # Ball 3: Wicket fell
    assert states.loc[2, "wickets_before"] == 0
    assert states.loc[2, "wickets_after"] == 1

    # Ball 4: Next ball starts with 1 wicket
    assert states.loc[3, "wickets_before"] == 1
    assert states.loc[3, "wickets_after"] == 1


def test_state_calculator_legal_balls_and_illegal_delivery(synthetic_innings_data):
    deliveries, configs = synthetic_innings_data
    states = calculate_match_states(deliveries, configs)

    # Ball 1 (Legal): balls before 0 -> after 1
    assert states.loc[0, "legal_balls_bowled_before"] == 0
    assert states.loc[0, "legal_balls_bowled_after"] == 1

    # Ball 2 (Wide - Illegal): balls before 1 -> after 1 (not incremented)
    assert states.loc[1, "legal_balls_bowled_before"] == 1
    assert states.loc[1, "legal_balls_bowled_after"] == 1

    # Ball 3 (Legal): balls before 1 -> after 2
    assert states.loc[2, "legal_balls_bowled_before"] == 1
    assert states.loc[2, "legal_balls_bowled_after"] == 2


def test_state_calculator_runs_required_and_rrr(synthetic_innings_data):
    deliveries, configs = synthetic_innings_data
    states = calculate_match_states(deliveries, configs)

    # Target = 150
    # Ball 1: runs_before = 0 -> req_before = 150
    assert states.loc[0, "runs_required_before"] == 150.0
    assert states.loc[0, "runs_required_after"] == 146.0

    # Required run rate before: 150 runs in 120 balls (20 overs) = 7.50 RRR
    assert states.loc[0, "required_run_rate_before"] == 7.50

