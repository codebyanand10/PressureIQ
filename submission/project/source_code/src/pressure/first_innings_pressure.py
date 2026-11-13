"""First-innings batting pressure model.

Quantifies batting pressure in first innings where no chase target exists.
Evaluates pressure against empirical scoring benchmarks, phase-based acceleration demands,
and wicket depletion without lookahead to final innings totals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, Union
from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_features import (
    calc_wicket_pressure,
    calc_time_pressure,
    calc_match_importance_pressure,
)


# Empirical historical scoring benchmarks by competition and phase
PHASE_CRR_BENCHMARKS = {
    "IPL": {
        "powerplay": 7.8,
        "middle": 8.3,
        "death": 11.0,
    },
    "T20I": {
        "powerplay": 7.2,
        "middle": 7.7,
        "death": 10.2,
    },
    "DEFAULT": {
        "powerplay": 7.5,
        "middle": 8.0,
        "death": 10.5,
    },
}


def get_expected_benchmark_crr(
    competition_type: Union[str, np.ndarray, pd.Series, None],
    innings_phase: Union[str, np.ndarray, pd.Series, None],
) -> Union[float, np.ndarray, pd.Series]:
    """Retrieve historical empirical CRR benchmark for competition and phase."""
    if isinstance(innings_phase, (pd.Series, np.ndarray)):
        phase_s = pd.Series(innings_phase).str.lower()
        comp_s = pd.Series(competition_type).fillna("DEFAULT") if competition_type is not None else pd.Series(["DEFAULT"] * len(phase_s))

        benchmarks = np.where(
            comp_s == "IPL",
            np.where(phase_s == "death", 11.0, np.where(phase_s == "middle", 8.3, 7.8)),
            np.where(
                comp_s == "T20I",
                np.where(phase_s == "death", 10.2, np.where(phase_s == "middle", 7.7, 7.2)),
                np.where(phase_s == "death", 10.5, np.where(phase_s == "middle", 8.0, 7.5)),
            ),
        )
        return benchmarks

    p = str(innings_phase).lower() if innings_phase else "middle"
    c = str(competition_type) if competition_type in PHASE_CRR_BENCHMARKS else "DEFAULT"
    comp_dict = PHASE_CRR_BENCHMARKS.get(c, PHASE_CRR_BENCHMARKS["DEFAULT"])
    return float(comp_dict.get(p, 8.0))


def calculate_first_innings_pressure(
    current_run_rate: Union[float, np.ndarray, pd.Series],
    wickets_lost: Union[int, float, np.ndarray, pd.Series],
    legal_balls_remaining: Union[float, np.ndarray, pd.Series],
    total_balls: Union[float, np.ndarray, pd.Series] = 120.0,
    innings_phase: Union[str, np.ndarray, pd.Series, None] = "middle",
    competition_type: Union[str, np.ndarray, pd.Series, None] = "IPL",
    is_knockout: Union[int, bool, np.ndarray, pd.Series] = 0,
    stage: Union[str, np.ndarray, pd.Series, None] = None,
    is_super_over: Union[int, bool, np.ndarray, pd.Series] = 0,
    config: Optional[PressureConfig] = None,
) -> Dict[str, Union[float, np.ndarray, pd.Series]]:
    """Calculate first-innings batting pressure and component indicators.

    Returns:
        Dictionary containing:
        - first_innings_pressure_score: float or array in [0.0, 100.0]
        - first_innings_scoring_pressure: float or array
        - first_innings_wicket_pressure: float or array
        - first_innings_time_pressure: float or array
        - first_innings_context_pressure: float or array
    """
    cfg = config or PressureConfig()
    weights = cfg.first_innings_weights

    crr_arr = np.asarray(current_run_rate, dtype=float)
    bench_crr = get_expected_benchmark_crr(competition_type, innings_phase)

    # 1. Scoring Pace Deficit Pressure
    # If CRR is lagging behind benchmark, pressure increases; if exceeding benchmark, pressure eases
    # gap = benchmark - crr: positive gap means behind par
    crr_gap = bench_crr - crr_arr
    scoring_p = 100.0 / (1.0 + np.exp(-0.45 * crr_gap))
    scoring_p = np.clip(scoring_p, 0.0, 100.0)

    # 2. Wicket Vulnerability Pressure
    wkt_p = calc_wicket_pressure(
        wickets_lost=wickets_lost,
        legal_balls_remaining=legal_balls_remaining,
        total_balls=total_balls,
    )

    # 3. Time Scarcity / Acceleration Pressure (higher in death overs)
    time_p = calc_time_pressure(
        legal_balls_remaining=legal_balls_remaining,
        total_balls=total_balls,
    )

    # In first innings, death overs create high acceleration pressure even with few wickets down
    phase_s = pd.Series(innings_phase).str.lower() if isinstance(innings_phase, (pd.Series, np.ndarray)) else str(innings_phase).lower()
    is_death = (phase_s == "death") if isinstance(phase_s, pd.Series) else (phase_s == "death")
    death_acceleration = np.where(is_death, 15.0, 0.0)

    # 4. Contextual Match Importance Pressure
    imp_p = calc_match_importance_pressure(
        is_knockout=is_knockout,
        stage=stage,
    )

    # Collapse boost: heavy wickets lost in early/middle overs creates severe pressure
    w_arr = np.asarray(wickets_lost, dtype=float)
    b_arr = np.asarray(legal_balls_remaining, dtype=float)
    collapse_boost = np.where((w_arr >= 3) & (b_arr >= 60.0), (w_arr - 2.0) * 8.5, 0.0)

    # Super over modifier: maximum urgency for 1st innings of super over
    is_so = np.asarray(is_super_over, dtype=int)
    so_boost = np.where(is_so == 1, 35.0, 0.0)

    # Weighted combination
    raw_score = (
        weights.get("scoring_pace", 0.30) * scoring_p
        + weights.get("wicket_vulnerability", 0.35) * wkt_p
        + weights.get("phase_pressure", 0.20) * (0.6 * time_p + 0.4 * (time_p + death_acceleration))
        + weights.get("match_context", 0.15) * imp_p
        + collapse_boost
        + so_boost
    )

    final_score = np.clip(raw_score, cfg.score_min, cfg.score_max)

    if np.isscalar(current_run_rate) and np.isscalar(wickets_lost):
        final_score = float(final_score.item() if hasattr(final_score, "item") else final_score)

    return {
        "first_innings_pressure_score": final_score,
        "first_innings_scoring_pressure": scoring_p,
        "first_innings_wicket_pressure": wkt_p,
        "first_innings_time_pressure": time_p,
        "first_innings_context_pressure": imp_p,
    }

