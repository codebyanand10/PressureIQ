"""Batting pressure calculation module.

Routes deliveries to chase or first-innings models and derives interpretable
pressure scores, classifications, and dominant reason factors for batters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, Union
from src.pressure.pressure_config import PressureConfig
from src.pressure.chase_pressure import calculate_chase_pressure
from src.pressure.first_innings_pressure import calculate_first_innings_pressure
from src.pressure.pressure_classifier import classify_pressure_score, classify_pressure_vector


def derive_batting_reason_and_factor(
    is_chase: bool,
    score: float,
    rrr_p: float,
    gap_p: float,
    wkt_p: float,
    time_p: float,
    imp_p: float,
    runs_required: Optional[float] = None,
    rrr: Optional[float] = None,
    wickets: Optional[int] = None,
    balls_left: Optional[int] = None,
    phase: Optional[str] = None,
) -> Tuple[str, str]:
    """Derive human-interpretable reason string and dominant factor for a batting delivery."""
    if runs_required is not None and runs_required <= 0:
        return ("Chase completed; target reached", "TARGET_ACHIEVED")

    if score < 20.0:
        rrr_val = rrr if rrr is not None else 0.0
        wkt_val = wickets if wickets is not None else 0
        if is_chase:
            return (f"Comfortable chase (RRR {rrr_val:.1f}, {10 - wkt_val} wkts in hand)", "COMFORTABLE_POSITION")
        else:
            return ("Strong first-innings base, low wicket loss", "SOLID_FOUNDATION")

    components = {
        "RRR_URGENCY": rrr_p if is_chase else 0.0,
        "RUN_RATE_DEFICIT": gap_p if is_chase else 0.0,
        "WICKET_PRESSURE": wkt_p,
        "TIME_DECAY": time_p,
        "MATCH_STAKES": imp_p,
    }

    dominant = max(components.items(), key=lambda x: x[1])[0]

    if is_chase:
        rrr_val = rrr if rrr is not None else 0.0
        wkt_val = wickets if wickets is not None else 0
        balls_val = balls_left if balls_left is not None else 0
        if dominant == "RRR_URGENCY" or dominant == "RUN_RATE_DEFICIT":
            reason = f"High RRR ({rrr_val:.1f}) demanding immediate boundaries"
        elif dominant == "WICKET_PRESSURE":
            reason = f"Heavy wicket loss ({wkt_val} down), tail exposed"
        elif dominant == "TIME_DECAY":
            reason = f"Shrinking deliveries ({balls_val} balls remaining)"
        else:
            reason = "High-stakes match context"
    else:
        wkt_val = wickets if wickets is not None else 0
        balls_val = balls_left if balls_left is not None else 0
        if str(phase).lower() == "death":
            reason = f"Death overs acceleration required ({balls_val} balls left)"
            dominant = "DEATH_ACCELERATION"
        elif dominant == "WICKET_PRESSURE":
            reason = f"Top/middle order collapse ({wkt_val} wickets lost)"
        elif dominant == "TIME_DECAY":
            reason = f"Late innings phase ({balls_val} balls remaining)"
        else:
            reason = "Scoring pace lagging behind competition par"

    return (reason, dominant)


def calculate_batting_pressure(
    df: pd.DataFrame,
    config: Optional[PressureConfig] = None,
) -> pd.DataFrame:
    """Calculate batting pressure scores, levels, indicators, and reasons across all deliveries.

    Operates vectorially on the match-state DataFrame.
    """
    cfg = config or PressureConfig()
    result = df.copy()

    # Identify chase vs 1st innings deliveries
    is_chasing = result["is_chasing_innings"].fillna(False).astype(bool)

    # Initialize pressure score columns
    batting_scores = np.zeros(len(result), dtype=float)
    rrr_pressures = np.full(len(result), np.nan, dtype=float)
    gap_pressures = np.full(len(result), np.nan, dtype=float)
    wkt_pressures = np.zeros(len(result), dtype=float)
    time_pressures = np.zeros(len(result), dtype=float)
    imp_pressures = np.zeros(len(result), dtype=float)
    close_pressures = np.full(len(result), np.nan, dtype=float)
    first_inn_scoring_pressures = np.full(len(result), np.nan, dtype=float)

    # 1. Process Chasing Deliveries (Innings 2 and 4)
    chase_mask = is_chasing
    if chase_mask.any():
        chase_sub = result[chase_mask]
        total_balls = chase_sub.get("available_legal_balls", pd.Series(120.0, index=chase_sub.index)).fillna(120.0)

        chase_res = calculate_chase_pressure(
            runs_required=chase_sub["runs_required_before"].fillna(0.0),
            legal_balls_remaining=chase_sub["legal_balls_remaining_before"].fillna(0.0),
            required_run_rate=chase_sub["required_run_rate_before"].fillna(0.0),
            current_run_rate=chase_sub["current_run_rate_before"].fillna(0.0),
            wickets_lost=chase_sub["wickets_before"].fillna(0),
            total_balls=total_balls,
            is_knockout=chase_sub.get("knock_out", pd.Series(0, index=chase_sub.index)).fillna(0),
            stage=chase_sub.get("stage", None),
            is_super_over=chase_sub.get("is_super_over", pd.Series(False, index=chase_sub.index)).fillna(False).astype(int),
            config=cfg,
        )

        batting_scores[chase_mask] = chase_res["chase_pressure_score"]
        rrr_pressures[chase_mask] = chase_res["rrr_pressure"]
        gap_pressures[chase_mask] = chase_res["run_rate_gap_pressure"]
        wkt_pressures[chase_mask] = chase_res["wicket_pressure"]
        time_pressures[chase_mask] = chase_res["time_pressure"]
        imp_pressures[chase_mask] = chase_res["match_importance_pressure"]
        close_pressures[chase_mask] = chase_res["match_closeness_pressure"]

    # 2. Process First-Innings Deliveries (Innings 1 and 3)
    first_inn_mask = ~is_chasing
    if first_inn_mask.any():
        first_sub = result[first_inn_mask]
        total_balls = first_sub.get("available_legal_balls", pd.Series(120.0, index=first_sub.index)).fillna(120.0)

        first_res = calculate_first_innings_pressure(
            current_run_rate=first_sub["current_run_rate_before"].fillna(0.0),
            wickets_lost=first_sub["wickets_before"].fillna(0),
            legal_balls_remaining=first_sub["legal_balls_remaining_before"].fillna(120.0),
            total_balls=total_balls,
            innings_phase=first_sub.get("innings_phase_before", pd.Series("middle", index=first_sub.index)),
            competition_type=first_sub.get("competition_type", pd.Series("IPL", index=first_sub.index)),
            is_knockout=first_sub.get("knock_out", pd.Series(0, index=first_sub.index)).fillna(0),
            stage=first_sub.get("stage", None),
            is_super_over=first_sub.get("is_super_over", pd.Series(False, index=first_sub.index)).fillna(False).astype(int),
            config=cfg,
        )

        batting_scores[first_inn_mask] = first_res["first_innings_pressure_score"]
        first_inn_scoring_pressures[first_inn_mask] = first_res["first_innings_scoring_pressure"]
        wkt_pressures[first_inn_mask] = first_res["first_innings_wicket_pressure"]
        time_pressures[first_inn_mask] = first_res["first_innings_time_pressure"]
        imp_pressures[first_inn_mask] = first_res["first_innings_context_pressure"]

    # Assign core output columns
    result["batting_pressure_score"] = np.round(batting_scores, 2)
    result["batting_pressure_level"] = classify_pressure_vector(result["batting_pressure_score"], cfg)

    result["rrr_pressure"] = np.round(rrr_pressures, 2)
    result["run_rate_gap_pressure"] = np.round(gap_pressures, 2)
    result["wicket_pressure"] = np.round(wkt_pressures, 2)
    result["time_pressure"] = np.round(time_pressures, 2)
    result["match_importance_pressure"] = np.round(imp_pressures, 2)
    result["match_closeness_pressure"] = np.round(close_pressures, 2)
    result["first_innings_scoring_pressure"] = np.round(first_inn_scoring_pressures, 2)

    # Fast zip over numpy arrays instead of slow iterrows
    is_ch_arr = result["is_chasing_innings"].fillna(False).values.astype(bool)
    score_arr = result["batting_pressure_score"].values
    rrr_p_arr = np.nan_to_num(result["rrr_pressure"].values, nan=0.0)
    gap_p_arr = np.nan_to_num(result["run_rate_gap_pressure"].values, nan=0.0)
    wkt_p_arr = np.nan_to_num(result["wicket_pressure"].values, nan=0.0)
    time_p_arr = np.nan_to_num(result["time_pressure"].values, nan=0.0)
    imp_p_arr = np.nan_to_num(result["match_importance_pressure"].values, nan=0.0)

    req_arr = result["runs_required_before"].values if "runs_required_before" in result.columns else np.full(len(result), np.nan)
    rrr_vals = result["required_run_rate_before"].values if "required_run_rate_before" in result.columns else np.full(len(result), np.nan)
    wkts_arr = result["wickets_before"].values if "wickets_before" in result.columns else np.zeros(len(result), dtype=int)
    balls_arr = result["legal_balls_remaining_before"].values if "legal_balls_remaining_before" in result.columns else np.zeros(len(result), dtype=int)
    phase_arr = result["innings_phase_before"].values if "innings_phase_before" in result.columns else np.full(len(result), "")

    reasons = []
    factors = []

    for is_ch, score_val, rrr_p_val, gap_p_val, wkt_p_val, time_p_val, imp_p_val, req_val, rrr_val, wkt_val, balls_val, phase_val in zip(
        is_ch_arr, score_arr, rrr_p_arr, gap_p_arr, wkt_p_arr, time_p_arr, imp_p_arr, req_arr, rrr_vals, wkts_arr, balls_arr, phase_arr
    ):
        r_str, f_str = derive_batting_reason_and_factor(
            is_chase=bool(is_ch),
            score=float(score_val),
            rrr_p=float(rrr_p_val),
            gap_p=float(gap_p_val),
            wkt_p=float(wkt_p_val),
            time_p=float(time_p_val),
            imp_p=float(imp_p_val),
            runs_required=float(req_val) if pd.notna(req_val) else None,
            rrr=float(rrr_val) if pd.notna(rrr_val) else None,
            wickets=int(wkt_val) if pd.notna(wkt_val) else None,
            balls_left=int(balls_val) if pd.notna(balls_val) else None,
            phase=str(phase_val),
        )
        reasons.append(r_str)
        factors.append(f_str)

    result["batting_pressure_reason"] = reasons
    result["dominant_pressure_factor"] = factors

    return result
