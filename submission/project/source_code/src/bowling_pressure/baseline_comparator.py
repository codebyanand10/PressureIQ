"""Baseline comparator module for bowling under pressure.

Compares high-pressure bowling performance against:
1. Overall Historical Baseline (`bowling_overall_baseline.parquet`)
2. Low-Pressure Baseline (`bowling_low_pressure_baseline.parquet`)

Produces `bowler_baseline_comparison.parquet`.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig

logger = logging.getLogger(__name__)


def compare_with_bowling_baselines(
    high_pressure_df: pd.DataFrame,
    overall_baseline_df: pd.DataFrame,
    low_pressure_baseline_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> pd.DataFrame:
    """Compare high-pressure bowling performance metrics with baseline performance.

    Args:
        high_pressure_df: High pressure performance dataset (`bowler_high_pressure_performance`).
        overall_baseline_df: Overall bowling baseline from Phase 5.
        low_pressure_baseline_df: Low-pressure bowling baseline from Phase 5.
        config: Configuration parameters.

    Returns:
        DataFrame with baseline comparison differentials and retention ratios.
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Computing bowling baseline comparison differentials and retention ratios...")

    hp = high_pressure_df.copy()
    hp["player_id"] = hp["player_id"].astype(str)

    # 1. Merge Overall Baseline
    base_cols = [
        "player_id",
        "economy_rate",
        "bowling_average",
        "bowling_strike_rate",
        "shrunk_economy_rate",
        "shrunk_bowling_average",
        "dot_ball_percentage",
        "boundary_percentage_conceded",
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

    # Ensure all expected baseline columns exist as series
    for c in base_cols:
        if c == "player_id":
            continue
        if f"overall_{c}" not in merged.columns:
            merged[f"overall_{c}"] = np.nan
        if f"lp_{c}" not in merged.columns:
            merged[f"lp_{c}"] = np.nan

    # 3. Overall Baseline Differentials
    # Economy rate (negative is favorable)
    merged["economy_difference_overall"] = merged["economy_rate"] - merged["overall_economy_rate"]
    merged["economy_retention_overall"] = np.where(
        (merged["overall_economy_rate"] > 0) & (merged["economy_rate"] > 0),
        (merged["overall_economy_rate"] / merged["economy_rate"]) * 100.0,
        np.nan,
    )
    # Shrunk economy retention (stabilized reference)
    merged["shrunk_econ_retention_overall"] = np.where(
        (merged["overall_shrunk_economy_rate"] > 0) & (merged["economy_rate"] > 0),
        (merged["overall_shrunk_economy_rate"] / merged["economy_rate"]) * 100.0,
        np.nan,
    )

    # Bowling average (negative is favorable)
    merged["average_difference_overall"] = merged["bowling_average"] - merged["overall_batting_average"] if "overall_batting_average" in merged.columns else (merged["bowling_average"] - merged["overall_bowling_average"])
    merged["average_retention_overall"] = np.where(
        (merged["overall_bowling_average"] > 0) & (merged["bowling_average"] > 0),
        (merged["overall_bowling_average"] / merged["bowling_average"]) * 100.0,
        np.nan,
    )

    # Bowling strike rate (negative is favorable)
    merged["strike_rate_difference_overall"] = merged["bowling_strike_rate"] - merged["overall_bowling_strike_rate"]

    # Dot-ball % (positive is favorable)
    merged["dot_ball_difference_overall"] = (
        merged["dot_ball_percentage"] - merged["overall_dot_ball_percentage"]
    )

    # Boundary % conceded (negative is favorable)
    merged["boundary_percentage_difference_overall"] = (
        merged["boundary_percentage_conceded"] - merged["overall_boundary_percentage_conceded"]
    )

    # 4. Low-Pressure Baseline Differentials
    merged["economy_difference_lp"] = merged["economy_rate"] - merged["lp_economy_rate"]
    merged["economy_retention_lp"] = np.where(
        (merged["lp_economy_rate"] > 0) & (merged["economy_rate"] > 0),
        (merged["lp_economy_rate"] / merged["economy_rate"]) * 100.0,
        np.nan,
    )
    merged["average_difference_lp"] = merged["bowling_average"] - merged["lp_bowling_average"]
    merged["strike_rate_difference_lp"] = merged["bowling_strike_rate"] - merged["lp_bowling_strike_rate"]
    merged["dot_ball_difference_lp"] = (
        merged["dot_ball_percentage"] - merged["lp_dot_ball_percentage"]
    )
    merged["boundary_percentage_difference_lp"] = (
        merged["boundary_percentage_conceded"] - merged["lp_boundary_percentage_conceded"]
    )

    # 5. Canonical Comparison Fields (Defaulting to Overall Baseline)
    merged["economy_difference"] = merged["economy_difference_overall"]
    merged["economy_retention"] = merged["economy_retention_overall"]
    merged["bowling_average_difference"] = merged["average_difference_overall"]
    merged["bowling_strike_rate_difference"] = merged["strike_rate_difference_overall"]
    merged["dot_ball_difference"] = merged["dot_ball_difference_overall"]
    merged["boundary_prevention_difference"] = merged["boundary_percentage_difference_overall"]

    # Wicket-taking difference: wickets per legal ball
    base_wkt_rate = np.where(
        merged["overall_bowling_strike_rate"] > 0,
        1.0 / merged["overall_bowling_strike_rate"],
        0.0,
    )
    hp_wkt_rate = (
        merged["wickets_per_legal_ball"]
        if "wickets_per_legal_ball" in merged.columns
        else np.where(
            merged["legal_balls_bowled"] > 0,
            merged.get("wickets_credited", pd.Series(0.0, index=merged.index)) / merged["legal_balls_bowled"],
            0.0,
        )
    )
    merged["wicket_taking_difference"] = hp_wkt_rate - base_wkt_rate

    # Overall Bowling Performance Retention Score
    econ_ret = merged["economy_retention"].fillna(100.0).clip(lower=20.0, upper=250.0)
    dot_ret = (100.0 + merged["dot_ball_difference"].fillna(0.0)).clip(lower=20.0, upper=200.0)
    bnd_ret = (100.0 - merged["boundary_prevention_difference"].fillna(0.0)).clip(lower=20.0, upper=200.0)
    merged["bowling_performance_retention"] = (0.50 * econ_ret + 0.25 * dot_ret + 0.25 * bnd_ret).round(2)

    logger.info("Computed bowling baseline comparisons for %d bowlers.", len(merged))
    return merged
