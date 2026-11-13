"""Baseline comparator module for batting under pressure.

Compares high-pressure batting performance against:
1. Overall Historical Baseline (`batting_overall_baseline.parquet`)
2. Low-Pressure Baseline (`batting_low_pressure_baseline.parquet`)

Produces `batter_baseline_comparison.parquet`.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig

logger = logging.getLogger(__name__)


def compare_with_baselines(
    high_pressure_df: pd.DataFrame,
    overall_baseline_df: pd.DataFrame,
    low_pressure_baseline_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> pd.DataFrame:
    """Compare high-pressure performance metrics with baseline performance.

    Args:
        high_pressure_df: High pressure performance dataset (`batter_high_pressure_performance`).
        overall_baseline_df: Overall batting baseline from Phase 5.
        low_pressure_baseline_df: Low-pressure batting baseline from Phase 5.
        config: Configuration parameters.

    Returns:
        DataFrame with baseline comparison differentials and retention ratios.
    """
    cfg = config or BattingPressureConfig()
    logger.info("Computing baseline comparison differentials and retention ratios...")

    hp = high_pressure_df.copy()
    hp["player_id"] = hp["player_id"].astype(str)

    # 1. Merge Overall Baseline
    base_cols = [
        "player_id",
        "strike_rate",
        "batting_average",
        "shrunk_strike_rate",
        "shrunk_batting_average",
        "boundary_percentage",
        "dot_ball_percentage",
        "dismissal_rate",
        "baseline_reliability_level",
    ]
    avail_cols = [c for c in base_cols if c in overall_baseline_df.columns]
    overall_sub = overall_baseline_df[avail_cols].rename(
        columns={c: f"overall_{c}" for c in avail_cols if c != "player_id"}
    )
    overall_sub["player_id"] = overall_sub["player_id"].astype(str)
    merged = hp.merge(overall_sub, on="player_id", how="left")

    # 2. Merge Low-Pressure Baseline
    lp_avail = [c for c in base_cols if c in low_pressure_baseline_df.columns]
    lp_sub = low_pressure_baseline_df[lp_avail].rename(
        columns={c: f"lp_{c}" for c in lp_avail if c != "player_id"}
    )
    lp_sub["player_id"] = lp_sub["player_id"].astype(str)
    merged = merged.merge(lp_sub, on="player_id", how="left")

    # Ensure all expected columns exist as float/object series if missing from baseline inputs
    for c in base_cols:
        if c == "player_id":
            continue
        if f"overall_{c}" not in merged.columns:
            merged[f"overall_{c}"] = np.nan
        if f"lp_{c}" not in merged.columns:
            merged[f"lp_{c}"] = np.nan

    # 3. Overall Baseline Differentials
    # Strike rate
    merged["strike_rate_difference_overall"] = merged["strike_rate"] - merged["overall_strike_rate"]
    merged["strike_rate_retention_overall"] = np.where(
        merged["overall_strike_rate"] > 0,
        (merged["strike_rate"] / merged["overall_strike_rate"]) * 100.0,
        np.nan,
    )
    # Shrunk strike rate retention (stabilized reference)
    merged["shrunk_sr_retention_overall"] = np.where(
        merged["overall_shrunk_strike_rate"] > 0,
        (merged["strike_rate"] / merged["overall_shrunk_strike_rate"]) * 100.0,
        np.nan,
    )

    # Batting average
    merged["average_difference_overall"] = merged["batting_average"] - merged["overall_batting_average"]
    merged["average_retention_overall"] = np.where(
        (merged["overall_batting_average"] > 0) & (merged["batting_average"].notna()),
        (merged["batting_average"] / merged["overall_batting_average"]) * 100.0,
        np.nan,
    )
    merged["shrunk_avg_retention_overall"] = np.where(
        (merged["overall_shrunk_batting_average"] > 0) & (merged["batting_average"].notna()),
        (merged["batting_average"] / merged["overall_shrunk_batting_average"]) * 100.0,
        np.nan,
    )

    # Boundary & Dot-ball %
    merged["boundary_percentage_difference_overall"] = (
        merged["boundary_percentage"] - merged["overall_boundary_percentage"]
    )
    merged["dot_ball_difference_overall"] = (
        merged["dot_ball_percentage"] - merged["overall_dot_ball_percentage"]
    )

    # Dismissal rate difference (hp - overall)
    merged["dismissal_rate_difference_overall"] = (
        merged["dismissal_rate"] - merged["overall_dismissal_rate"]
    )

    # 4. Low-Pressure Baseline Differentials (The definitive reference comparison)
    merged["strike_rate_difference_lp"] = merged["strike_rate"] - merged["lp_strike_rate"]
    merged["strike_rate_retention_lp"] = np.where(
        merged["lp_strike_rate"] > 0,
        (merged["strike_rate"] / merged["lp_strike_rate"]) * 100.0,
        np.nan,
    )
    merged["average_difference_lp"] = merged["batting_average"] - merged["lp_batting_average"]
    merged["average_retention_lp"] = np.where(
        (merged["lp_batting_average"] > 0) & (merged["batting_average"].notna()),
        (merged["batting_average"] / merged["lp_batting_average"]) * 100.0,
        np.nan,
    )
    merged["boundary_percentage_difference_lp"] = (
        merged["boundary_percentage"] - merged["lp_boundary_percentage"]
    )
    merged["dot_ball_difference_lp"] = (
        merged["dot_ball_percentage"] - merged["lp_dot_ball_percentage"]
    )
    merged["dismissal_rate_difference_lp"] = (
        merged["dismissal_rate"] - merged["lp_dismissal_rate"]
    )

    # 5. Primary Canonical Comparison Fields (Defaulting to Overall Baseline for complete cohort coverage)
    merged["strike_rate_difference"] = merged["strike_rate_difference_overall"]
    merged["strike_rate_retention"] = merged["strike_rate_retention_overall"]
    merged["average_difference"] = merged["average_difference_overall"]
    merged["average_retention"] = merged["average_retention_overall"]
    merged["boundary_percentage_difference"] = merged["boundary_percentage_difference_overall"]
    merged["dot_ball_difference"] = merged["dot_ball_difference_overall"]
    merged["dismissal_risk_difference"] = merged["dismissal_rate_difference_overall"]

    # Overall Performance Retention Score (Geometric/Harmonic-balanced retention composite)
    sr_ret = merged["strike_rate_retention"].fillna(100.0).clip(lower=20.0, upper=250.0)
    dot_ret = (100.0 - merged["dot_ball_difference"].fillna(0.0)).clip(lower=20.0, upper=200.0)
    bnd_ret = (100.0 + merged["boundary_percentage_difference"].fillna(0.0)).clip(lower=20.0, upper=200.0)
    merged["performance_retention"] = (0.50 * sr_ret + 0.25 * dot_ret + 0.25 * bnd_ret).round(2)

    logger.info("Computed baseline comparison for %d batters.", len(merged))
    return merged
