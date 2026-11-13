"""Second-innings chase pressure model.

Quantifies batting pressure during run chases using pre-delivery match state:
- Scoring urgency (RRR and CRR gap)
- Wicket vulnerability (wickets down vs remaining resources)
- Time scarcity (balls remaining)
- Match context (knockout stakes, Super Overs)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, Union
from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_features import (
    calc_rrr_pressure,
    calc_run_rate_gap_pressure,
    calc_wicket_pressure,
    calc_time_pressure,
    calc_match_importance_pressure,
    calc_match_closeness_pressure,
)


def calculate_chase_pressure(
    runs_required: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining: Union[float, np.ndarray, pd.Series],
    required_run_rate: Union[float, np.ndarray, pd.Series],
    current_run_rate: Union[float, np.ndarray, pd.Series],
    wickets_lost: Union[int, float, np.ndarray, pd.Series],
    total_balls: Union[float, np.ndarray, pd.Series] = 120.0,
    is_knockout: Union[int, bool, np.ndarray, pd.Series] = 0,
    stage: Union[str, np.ndarray, pd.Series, None] = None,
    is_super_over: Union[int, bool, np.ndarray, pd.Series] = 0,
    config: Optional[PressureConfig] = None,
) -> Dict[str, Union[float, np.ndarray, pd.Series]]:
    """Compute comprehensive chase pressure score and component indicators.

    Returns:
        Dictionary containing:
        - chase_pressure_score: float or array in [0.0, 100.0]
        - rrr_pressure: float or array
        - run_rate_gap_pressure: float or array
        - wicket_pressure: float or array
        - time_pressure: float or array
        - match_importance_pressure: float or array
        - match_closeness_pressure: float or array
        - dominant_factor: string explanation or array
    """
    cfg = config or PressureConfig()
    weights = cfg.chase_weights

    # 1. RRR Urgency
    rrr_p = calc_rrr_pressure(
        runs_required=runs_required,
        legal_balls_remaining=legal_balls_remaining,
        rrr_cap=cfg.rrr_cap,
        par_rrr=8.5,
    )

    # 2. Run Rate Gap
    gap_p = calc_run_rate_gap_pressure(
        rrr=required_run_rate,
        crr=current_run_rate,
        runs_required=runs_required,
    )

    # Urgency combined
    urgency = 0.65 * rrr_p + 0.35 * gap_p

    # 3. Wicket Vulnerability
    wkt_p = calc_wicket_pressure(
        wickets_lost=wickets_lost,
        legal_balls_remaining=legal_balls_remaining,
        total_balls=total_balls,
    )

    # 4. Time Scarcity
    time_p = calc_time_pressure(
        legal_balls_remaining=legal_balls_remaining,
        total_balls=total_balls,
    )

    # 5. Match Importance
    imp_p = calc_match_importance_pressure(
        is_knockout=is_knockout,
        stage=stage,
    )

    # 6. Match Closeness
    close_p = calc_match_closeness_pressure(
        runs_required=runs_required,
        legal_balls_remaining=legal_balls_remaining,
        wickets_lost=wickets_lost,
        total_balls=total_balls,
    )

    # Super over modifier: amplify baseline urgency
    is_so = np.asarray(is_super_over, dtype=int)
    so_boost = np.where(is_so == 1, 15.0, 0.0)

    # Tight finish / closeness boost
    closeness_boost = close_p * 0.12

    # High urgency boost when RRR is demanding
    urgency_boost = np.where(urgency > 85.0, (urgency - 85.0) * 0.15, 0.0)

    # Weighted linear combination
    raw_score = (
        weights.get("urgency", 0.35) * urgency
        + weights.get("wicket_vulnerability", 0.30) * wkt_p
        + weights.get("time_scarcity", 0.20) * time_p
        + weights.get("match_context", 0.15) * imp_p
        + closeness_boost
        + urgency_boost
        + so_boost
    )

    # If legal_balls_remaining == 0 and runs still required, sudden death pressure
    balls_arr = np.asarray(legal_balls_remaining, dtype=float)
    raw_score = np.where((balls_arr <= 0) & (np.asarray(runs_required, dtype=float) > 0), np.maximum(raw_score, 85.0), raw_score)

    # Floor when chase completed (runs_required <= 0)
    req_arr = np.asarray(runs_required, dtype=float)
    final_score = np.where(req_arr <= 0, 0.0, raw_score)
    final_score = np.clip(final_score, cfg.score_min, cfg.score_max)

    if np.isscalar(runs_required):
        final_score = float(final_score.item() if hasattr(final_score, "item") else final_score)

    return {
        "chase_pressure_score": final_score,
        "rrr_pressure": rrr_p,
        "run_rate_gap_pressure": gap_p,
        "wicket_pressure": wkt_p,
        "time_pressure": time_p,
        "match_importance_pressure": imp_p,
        "match_closeness_pressure": close_p,
    }

