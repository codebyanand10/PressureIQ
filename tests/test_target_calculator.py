"""Unit tests for target score calculation and sourcing (Phase 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.match_state.target_calculator import calculate_targets


@pytest.fixture
def sample_match_data_for_targets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    deliveries = pd.DataFrame({
        "match_id": [1, 1, 1, 2, 2, 3, 3],
        "innings": [1, 1, 2, 1, 2, 3, 4],
        "runs": [10, 20, 5, 50, 10, 10, 12],
        "extras1_runs": [1, 0, 0, 0, 0, 0, 0],
        "extras_2_runs": [0, 0, 0, 0, 0, 0, 0],
    })
    matches = pd.DataFrame({
        "match_id": [1, 2, 3],
        "revised_target": [np.nan, 85.0, np.nan],  # Match 2 has DLS revised target
    })
    return deliveries, matches


def test_first_innings_target_not_applicable(sample_match_data_for_targets):
    bbb, matches = sample_match_data_for_targets
    targets = calculate_targets(bbb, matches)
    target_score, source = targets[(1, 1)]
    assert target_score is None
    assert source == "NOT_APPLICABLE_FIRST_INNINGS"


def test_standard_second_innings_target(sample_match_data_for_targets):
    bbb, matches = sample_match_data_for_targets
    targets = calculate_targets(bbb, matches)
    # Match 1: Innings 1 scored 10 + 1 + 20 = 31 runs -> Target = 32
    target_score, source = targets[(1, 2)]
    assert target_score == 32.0
    assert source == "FIRST_INNINGS_TOTAL"


def test_dls_revised_target(sample_match_data_for_targets):
    bbb, matches = sample_match_data_for_targets
    targets = calculate_targets(bbb, matches)
    # Match 2: revised_target in matches is 85.0
    target_score, source = targets[(2, 2)]
    assert target_score == 85.0
    assert source == "DLS_REVISED_TARGET"


def test_super_over_target(sample_match_data_for_targets):
    bbb, matches = sample_match_data_for_targets
    targets = calculate_targets(bbb, matches)
    # Match 3: Innings 3 scored 10 -> Innings 4 target is 11
    target_score, source = targets[(3, 4)]
    assert target_score == 11.0
    assert source == "SUPER_OVER_TARGET"

