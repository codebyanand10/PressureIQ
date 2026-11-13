"""Unit tests for delivery processing and legal ball classification (Phase 3)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.match_state.delivery_processor import ILLEGAL_EXTRAS, process_deliveries


@pytest.fixture
def sample_deliveries_raw() -> pd.DataFrame:
    """Synthetic deliveries representing normal, wide, no-ball, bye, leg-bye, and multiple extras."""
    return pd.DataFrame({
        "match_id": [1, 1, 1, 1, 1, 1],
        "innings": [1, 1, 1, 1, 1, 1],
        "overid": [1, 1, 1, 1, 1, 1],
        "over_ball_num": [1, 2, 3, 4, 5, 6],
        "innings_ball_num": [1, 2, 3, 4, 5, 6],
        "delivery_order_idx": [0, 1, 2, 3, 4, 5],
        "runs": [1, 0, 4, 0, 0, 0],
        "extras1_runs": [0, 1, 1, 4, 1, 0],
        "extras_2_runs": [0, 0, 0, 0, 0, 0],
        "extras_type": [None, "wide", "Overstep", "byes", "legbyes", None],
        "is_four": [False, False, True, False, False, False],
        "is_six": [False, False, False, False, False, False],
        "is_wicket": [False, False, False, False, False, True],
        "dismissal_type": [None, None, None, None, None, "Bowled"],
        "dismissed_player_id": [None, None, None, None, None, 101],
    })


def test_process_deliveries_scoring_and_extras(sample_deliveries_raw: pd.DataFrame):
    processed = process_deliveries(sample_deliveries_raw)
    assert len(processed) == 6
    # Ball 1: 1 run off bat, 0 extras = 1 delivery run
    assert processed.loc[0, "delivery_runs"] == 1
    # Ball 2: Wide, 0 off bat, 1 extra = 1 delivery run
    assert processed.loc[1, "delivery_runs"] == 1
    # Ball 3: No-ball boundary, 4 off bat, 1 extra = 5 delivery runs
    assert processed.loc[2, "delivery_runs"] == 5
    # Ball 4: Byes 4, 0 off bat, 4 extras = 4 delivery runs
    assert processed.loc[3, "delivery_runs"] == 4


def test_legal_delivery_classification(sample_deliveries_raw: pd.DataFrame):
    processed = process_deliveries(sample_deliveries_raw)
    # Ball 1: Normal legal
    assert processed.loc[0, "is_legal_delivery"] == True
    # Ball 2: Wide (illegal)
    assert processed.loc[1, "is_legal_delivery"] == False
    # Ball 3: Overstep (illegal)
    assert processed.loc[2, "is_legal_delivery"] == False
    # Ball 4: Byes (legal)
    assert processed.loc[3, "is_legal_delivery"] == True
    # Ball 5: Leg-byes (legal)
    assert processed.loc[4, "is_legal_delivery"] == True
    # Ball 6: Wicket on normal ball (legal)
    assert processed.loc[5, "is_legal_delivery"] == True


def test_delivery_sequence_numbering():
    df = pd.DataFrame({
        "match_id": [1, 1, 2, 2],
        "innings": [1, 1, 1, 1],
        "delivery_order_idx": [10, 11, 20, 21],
        "runs": [0, 1, 4, 6],
        "extras1_runs": [0, 0, 0, 0],
        "extras_2_runs": [0, 0, 0, 0],
        "extras_type": [None, None, None, None],
        "is_wicket": [False, False, False, False],
    })
    processed = process_deliveries(df)
    assert processed.loc[processed["match_id"] == 1, "delivery_sequence"].tolist() == [1, 2]
    assert processed.loc[processed["match_id"] == 2, "delivery_sequence"].tolist() == [1, 2]

