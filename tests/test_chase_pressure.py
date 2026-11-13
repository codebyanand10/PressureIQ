"""Unit tests for the second-innings chase pressure model.

Tests low-pressure chases, extreme required run rates, wicket collapses,
death-over finishes, completed chases, and reduced-over targets.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.pressure.chase_pressure import calculate_chase_pressure
from src.pressure.pressure_config import PressureConfig


def test_comfortable_low_pressure_chase():
    """Verify that a comfortable chase produces low pressure."""
    # 20 runs needed from 36 balls with 9 wickets in hand (RRR 3.33)
    res = calculate_chase_pressure(
        runs_required=20,
        legal_balls_remaining=36,
        required_run_rate=3.33,
        current_run_rate=8.5,
        wickets_lost=1,
    )
    score = res["chase_pressure_score"]
    assert 0.0 <= score < 35.0


def test_high_rrr_extreme_chase():
    """Verify that an extreme RRR chase produces high to extreme pressure."""
    # 45 runs needed from 12 balls with 4 wickets in hand (RRR 22.5)
    res = calculate_chase_pressure(
        runs_required=45,
        legal_balls_remaining=12,
        required_run_rate=22.5,
        current_run_rate=7.0,
        wickets_lost=6,
    )
    score = res["chase_pressure_score"]
    assert score >= 75.0


def test_chase_few_vs_many_wickets():
    """Verify that with the same RRR, fewer wickets remaining generates higher pressure."""
    # 36 runs needed from 24 balls (RRR 9.0) with 2 wickets down vs 8 wickets down
    res_many_wkts = calculate_chase_pressure(
        runs_required=36,
        legal_balls_remaining=24,
        required_run_rate=9.0,
        current_run_rate=8.0,
        wickets_lost=2,
    )
    res_few_wkts = calculate_chase_pressure(
        runs_required=36,
        legal_balls_remaining=24,
        required_run_rate=9.0,
        current_run_rate=8.0,
        wickets_lost=8,
    )
    assert res_few_wkts["chase_pressure_score"] > res_many_wkts["chase_pressure_score"]


def test_last_over_tight_chase():
    """Verify last-over chase behavior."""
    # 12 runs needed off 6 balls
    res = calculate_chase_pressure(
        runs_required=12,
        legal_balls_remaining=6,
        required_run_rate=12.0,
        current_run_rate=8.2,
        wickets_lost=4,
    )
    assert res["chase_pressure_score"] >= 60.0
    assert res["match_closeness_pressure"] > 50.0


def test_chase_completed_zero_runs_required():
    """Verify chase pressure is zero when target is achieved."""
    res = calculate_chase_pressure(
        runs_required=0,
        legal_balls_remaining=15,
        required_run_rate=0.0,
        current_run_rate=9.2,
        wickets_lost=3,
    )
    assert res["chase_pressure_score"] == 0.0


def test_zero_legal_balls_remaining_handling():
    """Verify calculation does not crash when 0 legal balls remaining."""
    res = calculate_chase_pressure(
        runs_required=4,
        legal_balls_remaining=0,
        required_run_rate=24.0,
        current_run_rate=8.0,
        wickets_lost=5,
    )
    assert not np.isnan(res["chase_pressure_score"])
    assert res["chase_pressure_score"] >= 75.0


def test_reduced_over_chase():
    """Verify handling of reduced over total balls (e.g. 5-over match = 30 balls)."""
    res = calculate_chase_pressure(
        runs_required=15,
        legal_balls_remaining=12,
        required_run_rate=7.5,
        current_run_rate=8.0,
        wickets_lost=1,
        total_balls=30.0,
    )
    assert 0.0 <= res["chase_pressure_score"] <= 100.0

