"""Unit tests for pressure feature extraction functions.

Tests scoring urgency, run rate gap, wicket pressure, time pressure,
match importance, and match closeness on synthetic match states.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.pressure.pressure_features import (
    calc_rrr_pressure,
    calc_run_rate_gap_pressure,
    calc_wicket_pressure,
    calc_time_pressure,
    calc_match_importance_pressure,
    calc_match_closeness_pressure,
)


def test_calc_rrr_pressure_monotonicity():
    """Verify that increasing required run rate strictly increases pressure."""
    # RRR 6 vs 10 vs 18
    p_low = calc_rrr_pressure(runs_required=36, legal_balls_remaining=36)   # RRR 6.0
    p_med = calc_rrr_pressure(runs_required=60, legal_balls_remaining=36)   # RRR 10.0
    p_high = calc_rrr_pressure(runs_required=108, legal_balls_remaining=36) # RRR 18.0

    assert 0 <= p_low < p_med < p_high <= 100.0


def test_calc_rrr_pressure_completed_chase():
    """Verify that completed chase (runs_required <= 0) drops pressure to 0.0."""
    p_zero = calc_rrr_pressure(runs_required=0, legal_balls_remaining=12)
    p_neg = calc_rrr_pressure(runs_required=-4, legal_balls_remaining=6)

    assert p_zero == 0.0
    assert p_neg == 0.0


def test_calc_rrr_pressure_extreme_capped():
    """Verify that extreme RRR values are capped without crashing or yielding NaN."""
    p_extreme = calc_rrr_pressure(runs_required=100, legal_balls_remaining=1, rrr_cap=36.0)
    assert not np.isnan(p_extreme)
    assert p_extreme <= 100.0
    assert p_extreme >= 90.0


def test_calc_run_rate_gap_pressure():
    """Verify that trailing run rate gap increases pressure."""
    p_ahead = calc_run_rate_gap_pressure(rrr=6.0, crr=10.0) # gap = -4.0
    p_par = calc_run_rate_gap_pressure(rrr=8.0, crr=8.0)    # gap = 0.0
    p_behind = calc_run_rate_gap_pressure(rrr=12.0, crr=7.0) # gap = +5.0

    assert p_ahead < p_par < p_behind


def test_calc_wicket_pressure_monotonicity():
    """Verify that losing more wickets increases wicket vulnerability pressure."""
    p_1w = calc_wicket_pressure(wickets_lost=1, legal_balls_remaining=60)
    p_4w = calc_wicket_pressure(wickets_lost=4, legal_balls_remaining=60)
    p_8w = calc_wicket_pressure(wickets_lost=8, legal_balls_remaining=60)

    assert p_1w < p_4w < p_8w


def test_calc_time_pressure_death_acceleration():
    """Verify that time pressure accelerates as remaining legal deliveries decrease."""
    p_powerplay = calc_time_pressure(legal_balls_remaining=96)
    p_middle = calc_time_pressure(legal_balls_remaining=48)
    p_death = calc_time_pressure(legal_balls_remaining=12)

    assert p_powerplay < p_middle < p_death


def test_calc_match_importance_knockout():
    """Verify that knockout matches receive higher contextual importance pressure."""
    p_league = calc_match_importance_pressure(is_knockout=0, stage="League")
    p_final = calc_match_importance_pressure(is_knockout=1, stage="Final")

    assert p_final > p_league


def test_calc_match_closeness_tight_finish():
    """Verify match closeness peaks in a tight last-over finish."""
    # 10 runs off 6 balls with 6 wickets in hand
    p_close = calc_match_closeness_pressure(runs_required=10, legal_balls_remaining=6, wickets_lost=4)
    # 80 runs off 6 balls (hopeless)
    p_blowout = calc_match_closeness_pressure(runs_required=80, legal_balls_remaining=6, wickets_lost=4)

    assert p_close > p_blowout

