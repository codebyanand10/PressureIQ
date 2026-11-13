"""Unit tests for the first-innings batting pressure model.

Tests baseline scoring benchmarks, wicket collapses, death overs with strong position,
and competition-specific scoring baselines without lookahead leakage.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.pressure.first_innings_pressure import (
    calculate_first_innings_pressure,
    get_expected_benchmark_crr,
)


def test_first_innings_benchmark_crr_retrieval():
    """Verify empirical benchmarks by competition and phase."""
    ipl_death = get_expected_benchmark_crr("IPL", "death")
    ipl_pp = get_expected_benchmark_crr("IPL", "powerplay")
    t20i_death = get_expected_benchmark_crr("T20I", "death")

    assert ipl_death > ipl_pp
    assert ipl_death >= 10.5
    assert t20i_death >= 10.0


def test_first_innings_normal_state():
    """Verify standard first-innings pressure is moderate and well-behaved."""
    res = calculate_first_innings_pressure(
        current_run_rate=8.2,
        wickets_lost=2,
        legal_balls_remaining=60,
        innings_phase="middle",
        competition_type="IPL",
    )
    score = res["first_innings_pressure_score"]
    assert 30.0 <= score <= 60.0


def test_first_innings_wicket_collapse():
    """Verify early wicket collapse produces high pressure even in powerplay."""
    # 4 wickets down in powerplay (72 balls remaining) scoring at only 5.0 RPO
    res = calculate_first_innings_pressure(
        current_run_rate=5.0,
        wickets_lost=4,
        legal_balls_remaining=90,
        innings_phase="powerplay",
        competition_type="IPL",
    )
    score = res["first_innings_pressure_score"]
    assert score >= 60.0
    assert res["first_innings_wicket_pressure"] > 50.0


def test_first_innings_death_overs_strong_position():
    """Verify death overs with wickets in hand has acceleration pressure but low wicket pressure."""
    # 180/2 with 12 balls remaining in death overs, CRR 10.0
    res = calculate_first_innings_pressure(
        current_run_rate=10.0,
        wickets_lost=2,
        legal_balls_remaining=12,
        innings_phase="death",
        competition_type="IPL",
    )
    assert res["first_innings_wicket_pressure"] < 35.0
    assert res["first_innings_time_pressure"] > 70.0


def test_first_innings_super_over():
    """Verify Super Over 1st innings receives maximal urgency boost."""
    res = calculate_first_innings_pressure(
        current_run_rate=0.0,
        wickets_lost=0,
        legal_balls_remaining=6,
        total_balls=6.0,
        is_super_over=1,
    )
    assert res["first_innings_pressure_score"] >= 65.0

