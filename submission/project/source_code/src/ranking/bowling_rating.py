"""Bowling rating computation module for Phase 8.

Calculates the Final Bowler Pressure Rating (FBOR: 0 to 100) combining:
1. Quality & Baseline Resilience Score (BPPI-B)
2. Absolute Pressure Performance Score (economy rate, dot ball %, and wicket taking)
3. Multi-Spell Consistency Score (economy rate variability and spell stability)
4. Pressure Context & Role Difficulty Score (death overs share and extreme pressure exposure)
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
import numpy as np
import pandas as pd

from src.ranking.normalization import safe_linear_scale
from src.ranking.ranking_config import RankingConfig

logger = logging.getLogger(__name__)


def calculate_bowling_rating_components(
    bowling_merged_df: pd.DataFrame,
    config: RankingConfig,
    weights_profile: str = "primary",
) -> pd.DataFrame:
    """Compute individual bowling rating component scores and composite raw FBOR.

    Args:
        bowling_merged_df: Merged DataFrame containing Phase 7 metrics, BPPI-B, and roles.
        config: Ranking configuration.
        weights_profile: Weight profile name ('primary', 'balanced', 'baseline_focused', 'absolute_focused').

    Returns:
        DataFrame containing all component scores and raw FBOR.
    """
    df = bowling_merged_df.copy()
    weights = config.weight_profiles.get(weights_profile, config.primary_weights)

    # 1. Quality & Baseline Resilience Score (0 - 100)
    # Directly uses validated Phase 7 BPPI-B (which integrates baseline retention)
    df["score_bowling_resilience"] = df["bppi_b"].fillna(50.0).clip(lower=0.0, upper=100.0).round(2)

    # 2. Absolute Pressure Performance Score (0 - 100)
    # Combines high-pressure economy rate (inverted), dot ball %, and wicket rate
    econ_hp = df.get("economy_rate", pd.Series(9.5, index=df.index)).fillna(9.5)
    dot_hp = df.get("dot_ball_percentage", df.get("dot_ball_pct", pd.Series(35.0, index=df.index))).fillna(35.0)
    lb = df.get("legal_balls_bowled", df.get("legal_balls", pd.Series(1, index=df.index))).fillna(1).replace(0, 1).astype(float)
    wkts = df.get("wickets_credited", df.get("wickets", pd.Series(0, index=df.index))).fillna(0).astype(float)
    wkt_rate = (wkts / lb).clip(lower=0.0, upper=0.20)

    # Economy: 13.0 -> 0.0 score, 9.5 -> 50.0 score, 6.0 -> 100.0 score (inverted)
    econ_score = safe_linear_scale(econ_hp, lower_bound=6.0, upper_bound=13.0, invert=True)
    # Dot %: 20% -> 0.0, 40% -> 50.0, 60% -> 100.0
    dot_score = safe_linear_scale(dot_hp, lower_bound=20.0, upper_bound=60.0)
    # Wicket rate: 0.01 -> 0.0, 0.05 -> 50.0, 0.10 -> 100.0
    wkt_score = safe_linear_scale(wkt_rate, lower_bound=0.01, upper_bound=0.10)

    df["score_bowling_absolute"] = (0.45 * econ_score + 0.35 * dot_score + 0.20 * wkt_score).round(2)

    # 3. Consistency Score (0 - 100)
    # Evaluates spell-level economy stability and multi-match sample depth
    econ_var = df.get("economy_rate_variability", pd.Series(3.0, index=df.index)).fillna(3.0)
    var_score = safe_linear_scale(econ_var, lower_bound=0.5, upper_bound=6.0, invert=True)

    matches_cnt = df.get("matches_bowled", df.get("matches_count", pd.Series(1, index=df.index))).fillna(1).astype(int)
    depth_score = safe_linear_scale(matches_cnt, lower_bound=2.0, upper_bound=15.0)

    df["score_bowling_consistency"] = (0.60 * var_score + 0.40 * depth_score).round(2)

    # 4. Pressure Context & Role Difficulty Score (0 - 100)
    # Rewards bowling in death overs and high extreme-pressure delivery volume
    death_pct = df.get("death_pct", pd.Series(30.0, index=df.index)).fillna(30.0).astype(float)
    death_score = safe_linear_scale(death_pct, lower_bound=0.0, upper_bound=80.0)

    extreme_balls = df.get("extreme_pressure_balls", pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    extreme_ratio = (extreme_balls / lb).clip(lower=0.0, upper=1.0)
    extreme_score = safe_linear_scale(extreme_ratio, lower_bound=0.0, upper_bound=0.40)

    vol_score = safe_linear_scale(lb, lower_bound=24.0, upper_bound=150.0)

    df["score_bowling_context"] = (0.40 * death_score + 0.30 * extreme_score + 0.30 * vol_score).round(2)

    # Composite Raw FBOR
    w_res = weights["quality_and_resilience"]
    w_abs = weights["absolute_performance"]
    w_con = weights["consistency"]
    w_ctx = weights["pressure_context"]

    raw_fbor = (
        w_res * df["score_bowling_resilience"]
        + w_abs * df["score_bowling_absolute"]
        + w_con * df["score_bowling_consistency"]
        + w_ctx * df["score_bowling_context"]
    )
    df["raw_fbor"] = raw_fbor.clip(lower=0.0, upper=100.0).round(2)

    logger.info(
        "Bowling rating components computed (Mean Raw FBOR: %.2f, Min: %.2f, Max: %.2f).",
        df["raw_fbor"].mean(),
        df["raw_fbor"].min(),
        df["raw_fbor"].max(),
    )
    return df

