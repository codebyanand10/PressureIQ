"""Batting rating computation module for Phase 8.

Calculates the Final Batter Pressure Rating (FBPR: 0 to 100) combining:
1. Quality & Baseline Resilience Score (BPPI)
2. Absolute Pressure Performance Score (high-pressure SR and boundary %)
3. Multi-Match Consistency Score (scoring consistency & SR stability)
4. Pressure Context & Difficulty Score (extreme pressure exposure & match depth)
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
import numpy as np
import pandas as pd

from src.ranking.normalization import safe_linear_scale
from src.ranking.ranking_config import RankingConfig

logger = logging.getLogger(__name__)


def calculate_batting_rating_components(
    batting_merged_df: pd.DataFrame,
    config: RankingConfig,
    weights_profile: str = "primary",
) -> pd.DataFrame:
    """Compute individual batting rating component scores and composite raw FBPR.

    Args:
        batting_merged_df: Merged DataFrame containing Phase 6 metrics and BPPI.
        config: Ranking configuration.
        weights_profile: Weight profile name ('primary', 'balanced', 'baseline_focused', 'absolute_focused').

    Returns:
        DataFrame containing all component scores and raw FBPR.
    """
    df = batting_merged_df.copy()
    weights = config.weight_profiles.get(weights_profile, config.primary_weights)

    # 1. Quality & Baseline Resilience Score (0 - 100)
    # Directly uses validated Phase 6 BPPI (which integrates baseline retention)
    df["score_batting_resilience"] = df["bppi"].fillna(50.0).clip(lower=0.0, upper=100.0).round(2)

    # 2. Absolute Pressure Performance Score (0 - 100)
    # Combines high-pressure strike rate and boundary run percentage
    sr_hp = df.get("strike_rate", pd.Series(120.0, index=df.index)).fillna(120.0)
    bnd_hp = df.get("boundary_percentage", df.get("boundary_pct", pd.Series(40.0, index=df.index))).fillna(40.0)

    # SR 80 -> 0.0, 140 -> 50.0, 200 -> 100.0
    sr_score = safe_linear_scale(sr_hp, lower_bound=80.0, upper_bound=200.0)
    # Boundary % 20% -> 0.0, 45% -> 50.0, 70% -> 100.0
    bnd_score = safe_linear_scale(bnd_hp, lower_bound=20.0, upper_bound=70.0)

    df["score_batting_absolute"] = (0.60 * sr_score + 0.40 * bnd_score).round(2)

    # 3. Consistency Score (0 - 100)
    # Evaluates multi-match scoring stability using strike rate variability and innings count
    sr_var = df.get("strike_rate_variability", pd.Series(50.0, index=df.index)).fillna(50.0)
    var_score = safe_linear_scale(sr_var, lower_bound=10.0, upper_bound=150.0, invert=True)

    inns_cnt = df.get("innings_count", pd.Series(1, index=df.index)).fillna(1).astype(int)
    matches_cnt = df["matches_count"].fillna(1).astype(int)
    depth_score = safe_linear_scale(matches_cnt, lower_bound=2.0, upper_bound=15.0)

    df["score_batting_consistency"] = (0.60 * var_score + 0.40 * depth_score).round(2)

    # 4. Pressure Context & Difficulty Score (0 - 100)
    # Rewards exposure to extreme pressure deliveries (score >= 80) and high-leverage situations
    hp_balls = df["balls_faced"].fillna(1).replace(0, 1).astype(float)
    extreme_balls = df.get("extreme_pressure_balls", pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    extreme_ratio = (extreme_balls / hp_balls).clip(lower=0.0, upper=1.0)
    extreme_score = safe_linear_scale(extreme_ratio, lower_bound=0.0, upper_bound=0.40)

    vol_score = safe_linear_scale(hp_balls, lower_bound=20.0, upper_bound=150.0)

    df["score_batting_context"] = (0.50 * extreme_score + 0.50 * vol_score).round(2)

    # Composite Raw FBPR
    w_res = weights["quality_and_resilience"]
    w_abs = weights["absolute_performance"]
    w_con = weights["consistency"]
    w_ctx = weights["pressure_context"]

    raw_fbpr = (
        w_res * df["score_batting_resilience"]
        + w_abs * df["score_batting_absolute"]
        + w_con * df["score_batting_consistency"]
        + w_ctx * df["score_batting_context"]
    )
    df["raw_fbpr"] = raw_fbpr.clip(lower=0.0, upper=100.0).round(2)

    logger.info(
        "Batting rating components computed (Mean Raw FBPR: %.2f, Min: %.2f, Max: %.2f).",
        df["raw_fbpr"].mean(),
        df["raw_fbpr"].min(),
        df["raw_fbpr"].max(),
    )
    return df

