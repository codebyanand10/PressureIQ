"""Bowling pressure calculation module.

Quantifies pressure experienced by the bowling side at the start of each delivery.
Reflects defense difficulty, run-containment urgency, and threat of match loss.
Crucially, bowling pressure is NOT a mere mirror image of batting pressure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, Union
from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_classifier import classify_pressure_vector
from src.pressure.first_innings_pressure import get_expected_benchmark_crr
from src.pressure.pressure_features import calc_match_importance_pressure


def derive_bowling_reason(
    is_chase: bool,
    score: float,
    runs_required: Optional[float] = None,
    rrr: Optional[float] = None,
    wickets: Optional[int] = None,
    balls_left: Optional[int] = None,
    crr: Optional[float] = None,
    phase: Optional[str] = None,
) -> str:
    """Derive human-interpretable reason string for bowling pressure."""
    req_val = runs_required if runs_required is not None else 0.0
    rrr_val = rrr if rrr is not None else 0.0
    wkt_val = wickets if wickets is not None else 0
    balls_val = balls_left if balls_left is not None else 0
    crr_val = crr if crr is not None else 0.0

    if is_chase:
        if runs_required is not None and runs_required <= 0:
            return "Target breached; match decided"

        if score >= 75.0:
            if balls_left is not None and balls_left <= 18:
                return f"Defending tight margin ({req_val:.0f} off {balls_val} balls)"
            return f"Low defensive cushion (RRR {rrr_val:.1f}) with batting wickets in hand"
        elif score < 30.0:
            return f"Comfortable defense cushion (RRR {rrr_val:.1f})"
        else:
            return f"Balanced defense contest ({req_val:.0f} runs needed off {balls_val} balls)"
    else:
        if score >= 75.0:
            if str(phase).lower() == "death":
                return "Death overs containment under high boundary threat"
            return f"Batting team scoring heavily at {crr_val:.1f} CRR; wicket needed"
        elif score < 30.0:
            return f"Bowler on top; batting side restricted ({wkt_val} wickets down)"
        else:
            return "Normal competitive first-innings containment"


def calculate_bowling_pressure(
    df: pd.DataFrame,
    config: Optional[PressureConfig] = None,
) -> pd.DataFrame:
    """Calculate bowling pressure scores, levels, and reasons across all deliveries."""
    cfg = config or PressureConfig()
    result = df.copy()

    is_chasing = result["is_chasing_innings"].fillna(False).astype(bool)
    bowling_scores = np.zeros(len(result), dtype=float)

    # 1. Chasing Innings Bowling Pressure (Innings 2 and 4)
    chase_mask = is_chasing
    if chase_mask.any():
        chase_sub = result[chase_mask]
        req = chase_sub["runs_required_before"].fillna(0.0).values
        balls = chase_sub["legal_balls_remaining_before"].fillna(0.0).values
        rrr = chase_sub["required_run_rate_before"].fillna(0.0).values
        wkts = chase_sub["wickets_before"].fillna(0).values
        ko = chase_sub.get("knock_out", pd.Series(0, index=chase_sub.index)).fillna(0).values
        stage = chase_sub.get("stage", None)

        weights = cfg.bowling_chase_weights

        # In a chase, lower RRR means higher bowling defense risk!
        # When RRR is 6.0: defense_risk is ~65. When RRR is 14.0: defense_risk is ~6.
        defense_risk = 100.0 / (1.0 + np.exp(0.35 * (rrr - 7.5)))

        # Wickets in hand for the batting team increases bowling pressure
        batting_resources = (10.0 - wkts) / 10.0
        wkt_factor = (batting_resources ** 0.8) * 85.0

        # Time margin: when balls remaining is small (<= 24) and target is close (req <= 36)
        tight_finish_threat = np.where(
            (balls <= 24) & (req > 0) & (req <= 40),
            np.clip(100.0 - (req - balls) * 2.5, 30.0, 100.0),
            0.0
        )

        imp_p = calc_match_importance_pressure(is_knockout=ko, stage=stage)

        # Composite chase bowling pressure
        chase_bowling_raw = (
            weights.get("defense_risk", 0.50) * defense_risk
            + weights.get("time_margin", 0.30) * np.maximum(wkt_factor * 0.4 + tight_finish_threat * 0.6, defense_risk * 0.5)
            + weights.get("match_context", 0.20) * imp_p
        )

        # Floor when chase is finished (req <= 0)
        chase_bowling_raw = np.where(req <= 0, 0.0, chase_bowling_raw)
        bowling_scores[chase_mask] = np.clip(chase_bowling_raw, cfg.score_min, cfg.score_max)

    # 2. First-Innings Bowling Pressure (Innings 1 and 3)
    first_inn_mask = ~is_chasing
    if first_inn_mask.any():
        first_sub = result[first_inn_mask]
        crr = first_sub["current_run_rate_before"].fillna(0.0).values
        wkts = first_sub["wickets_before"].fillna(0).values
        phase = first_sub.get("innings_phase_before", pd.Series("middle", index=first_sub.index))
        comp = first_sub.get("competition_type", pd.Series("IPL", index=first_sub.index))
        ko = first_sub.get("knock_out", pd.Series(0, index=first_sub.index)).fillna(0).values
        stage = first_sub.get("stage", None)

        weights = cfg.bowling_first_inn_weights
        bench_crr = get_expected_benchmark_crr(comp, phase)

        # In 1st innings: high batting CRR creates high bowling pressure (containment risk)
        crr_gap = crr - bench_crr
        containment_risk = 100.0 / (1.0 + np.exp(-0.40 * crr_gap))

        # Wickets remaining for the batting side: if 10 wkts intact, pressure is high to take wickets
        wicket_need = ((10.0 - wkts) / 10.0) ** 1.2 * 90.0

        # Phase factor: death overs are high stress for bowlers
        phase_s = pd.Series(phase).str.lower()
        is_death = (phase_s == "death").values
        death_penalty = np.where(is_death, 15.0, 0.0)

        imp_p = calc_match_importance_pressure(is_knockout=ko, stage=stage)

        first_bowling_raw = (
            weights.get("containment_risk", 0.45) * containment_risk
            + weights.get("wicket_need", 0.35) * (wicket_need + death_penalty)
            + weights.get("match_context", 0.20) * imp_p
        )
        bowling_scores[first_inn_mask] = np.clip(first_bowling_raw, cfg.score_min, cfg.score_max)

    result["bowling_pressure_score"] = np.round(bowling_scores, 2)
    result["bowling_pressure_level"] = classify_pressure_vector(result["bowling_pressure_score"], cfg)

    # Fast zip over numpy arrays instead of slow iterrows
    is_ch_arr = result["is_chasing_innings"].fillna(False).values.astype(bool)
    score_arr = result["bowling_pressure_score"].values
    req_arr = result["runs_required_before"].values if "runs_required_before" in result.columns else np.full(len(result), np.nan)
    rrr_vals = result["required_run_rate_before"].values if "required_run_rate_before" in result.columns else np.full(len(result), np.nan)
    wkts_arr = result["wickets_before"].values if "wickets_before" in result.columns else np.zeros(len(result), dtype=int)
    balls_arr = result["legal_balls_remaining_before"].values if "legal_balls_remaining_before" in result.columns else np.zeros(len(result), dtype=int)
    crr_vals = result["current_run_rate_before"].values if "current_run_rate_before" in result.columns else np.zeros(len(result), dtype=float)
    phase_arr = result["innings_phase_before"].values if "innings_phase_before" in result.columns else np.full(len(result), "")

    reasons = []
    for is_ch, score_val, req_val, rrr_val, wkt_val, balls_val, crr_val, phase_val in zip(
        is_ch_arr, score_arr, req_arr, rrr_vals, wkts_arr, balls_arr, crr_vals, phase_arr
    ):
        r_str = derive_bowling_reason(
            is_chase=bool(is_ch),
            score=float(score_val),
            runs_required=float(req_val) if pd.notna(req_val) else None,
            rrr=float(rrr_val) if pd.notna(rrr_val) else None,
            wickets=int(wkt_val) if pd.notna(wkt_val) else None,
            balls_left=int(balls_val) if pd.notna(balls_val) else None,
            crr=float(crr_val) if pd.notna(crr_val) else None,
            phase=str(phase_val),
        )
        reasons.append(r_str)

    result["bowling_pressure_reason"] = reasons
    return result
