"""Unit tests for innings phase proportional partitioning (Phase 3)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.match_state.innings_phase import (
    InningsPhaseConfig,
    classify_innings_phase,
    classify_phase_single,
)


def test_standard_t20_phase_boundaries():
    cfg = InningsPhaseConfig(powerplay_end=0.30, middle_overs_end=0.75)
    total_balls = 120

    # Balls 0 to 36 = Powerplay (0 to 30%)
    assert classify_phase_single(0, total_balls, config=cfg) == "POWERPLAY"
    assert classify_phase_single(36, total_balls, config=cfg) == "POWERPLAY"

    # Balls 37 to 90 = Middle Overs (30% to 75%)
    assert classify_phase_single(37, total_balls, config=cfg) == "MIDDLE_OVERS"
    assert classify_phase_single(90, total_balls, config=cfg) == "MIDDLE_OVERS"

    # Balls 91 to 120 = Death Overs (> 75%)
    assert classify_phase_single(91, total_balls, config=cfg) == "DEATH_OVERS"
    assert classify_phase_single(120, total_balls, config=cfg) == "DEATH_OVERS"


def test_reduced_overs_proportional_phases():
    cfg = InningsPhaseConfig(powerplay_end=0.30, middle_overs_end=0.75)
    # Reduced to 10 overs = 60 legal balls
    total_balls = 60

    # Powerplay: 60 * 0.30 = 18 balls
    assert classify_phase_single(18, total_balls, config=cfg) == "POWERPLAY"
    assert classify_phase_single(19, total_balls, config=cfg) == "MIDDLE_OVERS"

    # Middle Overs: 60 * 0.75 = 45 balls
    assert classify_phase_single(45, total_balls, config=cfg) == "MIDDLE_OVERS"
    assert classify_phase_single(46, total_balls, config=cfg) == "DEATH_OVERS"


def test_super_over_phase():
    # Super over (<= 6 balls)
    assert classify_phase_single(3, 6, is_super_over=True) == "SUPER_OVER"
    assert classify_phase_single(6, 6, is_super_over=False) == "SUPER_OVER"


def test_vectorized_phase_classification():
    balls = pd.Series([10, 50, 100, 3])
    avail = pd.Series([120, 120, 120, 6])
    so = pd.Series([False, False, False, True])

    phases = classify_innings_phase(balls, avail, so)
    assert phases.tolist() == ["POWERPLAY", "MIDDLE_OVERS", "DEATH_OVERS", "SUPER_OVER"]

