"""Pressure feature extraction module.

Extracts interpretable cricket pressure indicators from pre-delivery match states.
Operates on pre-delivery parameters with strict zero-lookahead guarantees.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Union


def calc_rrr_pressure(
    runs_required: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining: Union[float, np.ndarray, pd.Series],
    rrr_cap: float = 36.0,
    par_rrr: float = 8.5,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate scoring urgency pressure from required run rate.

    Uses a calibrated sigmoid curve centered around modern T20 par chase rate (8.5 RPO).
    Floors pressure at 0.0 when chase is already completed (runs_required <= 0).
    Caps extreme RRR at rrr_cap to avoid single-ball outlier distortion.
    """
    is_scalar = np.isscalar(runs_required)
    req = np.asarray(runs_required, dtype=float)
    balls = np.asarray(legal_balls_remaining, dtype=float)

    # Protect division by zero
    safe_balls = np.maximum(balls, 1.0)
    raw_rrr = (req / safe_balls) * 6.0

    # Clamp RRR between 0.0 and rrr_cap
    clamped_rrr = np.clip(raw_rrr, 0.0, rrr_cap)

    # Calibrated T20 sigmoid: RRR=0 -> ~4, RRR=8.5 -> 50, RRR=14 -> 86, RRR=20 -> 98
    sigmoid_score = 100.0 / (1.0 + np.exp(-0.35 * (clamped_rrr - par_rrr)))

    # Floor when target already reached or negative
    score = np.where(req <= 0, 0.0, sigmoid_score)
    score = np.clip(score, 0.0, 100.0)

    return float(score.item()) if is_scalar else score


def calc_run_rate_gap_pressure(
    rrr: Union[float, np.ndarray, pd.Series],
    crr: Union[float, np.ndarray, pd.Series],
    runs_required: Union[float, np.ndarray, pd.Series, None] = None,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate pressure caused by the divergence between required and current run rate.

    A positive gap (RRR > CRR) indicates that the batting side is falling behind the clock.
    A negative gap (CRR > RRR) indicates that the batting side is scoring comfortably above par.
    """
    is_scalar = np.isscalar(rrr) and np.isscalar(crr)
    r = np.asarray(rrr, dtype=float)
    c = np.asarray(crr, dtype=float)

    gap = r - c
    # Sigmoid centered at 0 gap: gap=0 -> 50, gap=+4 -> 85, gap=-4 -> 14
    score = 100.0 / (1.0 + np.exp(-0.40 * gap))

    if runs_required is not None:
        req = np.asarray(runs_required, dtype=float)
        score = np.where(req <= 0, 0.0, score)

    score = np.clip(score, 0.0, 100.0)
    return float(score.item()) if is_scalar else score


def calc_wicket_pressure(
    wickets_lost: Union[int, float, np.ndarray, pd.Series],
    legal_balls_remaining: Union[int, float, np.ndarray, pd.Series],
    total_balls: float = 120.0,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate wicket vulnerability pressure based on wickets down and balls left.

    Considers tail-ender exposure (wickets >= 6) and wicket depletion relative to balls consumed.
    """
    is_scalar = np.isscalar(wickets_lost) and np.isscalar(legal_balls_remaining)
    w = np.clip(np.asarray(wickets_lost, dtype=float), 0.0, 10.0)
    b = np.clip(np.asarray(legal_balls_remaining, dtype=float), 0.0, total_balls)

    # Base vulnerability rises monotonically as wickets fall
    base_vuln = (w / 10.0) ** 1.15 * 85.0

    # Resource ratio: fraction of wickets lost vs fraction of overs consumed
    balls_consumed_fraction = 1.0 - (b / total_balls)
    wickets_lost_fraction = w / 10.0
    deficit = wickets_lost_fraction - balls_consumed_fraction

    # If wickets lost faster than overs consumed, strong penalty
    # If wickets lost is high (>= 5), tail is exposed regardless of overs
    deficit_adj = np.where(deficit > 0, deficit * 140.0, np.where(w >= 5, 0.0, deficit * 15.0))

    # Tail exposure bonus for 6+ wickets down
    tail_bonus = np.where(w >= 6, (w - 5.0) * 4.0, 0.0)

    score = np.clip(base_vuln + deficit_adj + tail_bonus, 0.0, 100.0)
    return float(score.item()) if is_scalar else score


def calc_time_pressure(
    legal_balls_remaining: Union[int, float, np.ndarray, pd.Series],
    total_balls: float = 120.0,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate time scarcity pressure as remaining legal deliveries decrease.

    Pressure accelerates in the death overs (final 24 balls) where opportunity to recover shrinks.
    """
    is_scalar = np.isscalar(legal_balls_remaining)
    b = np.clip(np.asarray(legal_balls_remaining, dtype=float), 0.0, total_balls)

    fraction_consumed = 1.0 - (b / total_balls)
    # Exponential acceleration in the final phase
    score = (fraction_consumed ** 1.6) * 100.0

    score = np.clip(score, 0.0, 100.0)
    return float(score.item()) if is_scalar else score


def calc_match_importance_pressure(
    is_knockout: Union[int, bool, np.ndarray, pd.Series],
    stage: Union[str, np.ndarray, pd.Series, None] = None,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate contextual match importance based on tournament stakes.

    Finals and qualifiers/eliminators carry significantly higher competitive stakes than group fixtures.
    """
    is_scalar = np.isscalar(is_knockout)
    ko = np.asarray(is_knockout, dtype=int)

    base_score = np.where(ko == 1, 80.0, 45.0)

    if stage is not None:
        if isinstance(stage, (pd.Series, np.ndarray)):
            s_arr = pd.Series(stage).astype(str).str.lower()
            stage_boost = np.where(
                s_arr.str.contains("final"), 15.0,
                np.where(s_arr.str.contains("semi|eliminator|qualifier"), 10.0,
                         np.where(s_arr.str.contains("super 4"), 5.0, 0.0))
            )
            base_score = base_score + stage_boost
        elif isinstance(stage, str):
            s_lower = stage.lower()
            if "final" in s_lower:
                base_score += 15.0
            elif any(k in s_lower for k in ["semi", "eliminator", "qualifier"]):
                base_score += 10.0
            elif "super 4" in s_lower:
                base_score += 5.0

    score = np.clip(base_score, 0.0, 100.0)
    return float(score.item()) if is_scalar else score


def calc_match_closeness_pressure(
    runs_required: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining: Union[float, np.ndarray, pd.Series],
    wickets_lost: Union[int, float, np.ndarray, pd.Series],
    total_balls: float = 120.0,
) -> Union[float, np.ndarray, pd.Series]:
    """Calculate match closeness / tension for chasing innings.

    Peak closeness occurs when balls remaining is small (<= 30 balls) and runs required is tightly
    balanced with wickets in hand, creating maximum outcome uncertainty.
    """
    is_scalar = np.isscalar(runs_required) and np.isscalar(legal_balls_remaining)
    req = np.asarray(runs_required, dtype=float)
    balls = np.asarray(legal_balls_remaining, dtype=float)
    wkts = np.asarray(wickets_lost, dtype=float)

    # Par runs expected for remaining balls given wickets lost: ~1.4 runs per ball with 4 wkts down
    expected_rate = 1.3 + (10.0 - wkts) * 0.05
    par_runs = balls * expected_rate
    diff = req - par_runs

    # Closeness peaks when diff is near 0 and balls remaining is small
    decay = np.exp(- (diff / 16.0) ** 2)
    late_stage_weight = (1.0 - np.clip(balls / total_balls, 0.0, 1.0)) ** 1.2

    score = 100.0 * decay * late_stage_weight
    # Zero when chase completed
    score = np.where(req <= 0, 0.0, score)

    score = np.clip(score, 0.0, 100.0)
    return float(score.item()) if is_scalar else score

